"""Cross-platform IPC for daemon communication."""

from __future__ import annotations

import asyncio
import json
import logging
import struct
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .platform import IS_WINDOWS, get_socket_path

# Logger for IPC debugging
logger = logging.getLogger("mcpl.ipc")

if TYPE_CHECKING:
    pass

# Type alias for IPC message handlers
IPCHandler = Callable[["IPCMessage"], Awaitable["IPCMessage"]]


# Message format: 4-byte length prefix + JSON payload
HEADER_SIZE = 4


@dataclass
class IPCMessage:
    """A message sent between CLI and daemon."""

    action: str
    payload: dict[str, Any]

    def to_bytes(self) -> bytes:
        """Serialize message to bytes with length prefix."""
        data = json.dumps({"action": self.action, "payload": self.payload}).encode()
        return struct.pack(">I", len(data)) + data

    @classmethod
    def from_bytes(cls, data: bytes) -> IPCMessage:
        """Deserialize message from JSON bytes."""
        parsed = json.loads(data.decode())
        return cls(action=parsed["action"], payload=parsed.get("payload", {}))


async def read_message(reader: asyncio.StreamReader) -> IPCMessage | None:
    """Read a length-prefixed message from the stream.

    Uses readexactly() to ensure we read the complete message, even if
    the data arrives in multiple chunks over the socket.
    """
    try:
        # Read exactly HEADER_SIZE bytes for the length prefix
        header = await reader.readexactly(HEADER_SIZE)
    except asyncio.IncompleteReadError:
        # Connection closed before header was fully received (e.g., ping check)
        return None

    (length,) = struct.unpack(">I", header)

    try:
        # Read exactly 'length' bytes for the message body
        data = await reader.readexactly(length)
    except asyncio.IncompleteReadError as e:
        logger.warning(
            f"Connection closed during message read: got {len(e.partial)} of {length} bytes"
        )
        return None

    return IPCMessage.from_bytes(data)


async def write_message(writer: asyncio.StreamWriter, message: IPCMessage) -> None:
    """Write a length-prefixed message to the stream."""
    writer.write(message.to_bytes())
    await writer.drain()


class IPCServer(ABC):
    """Abstract base class for IPC server."""

    @abstractmethod
    async def start(self) -> None:
        """Start the server."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the server."""
        pass


class UnixIPCServer(IPCServer):
    """Unix socket-based IPC server."""

    def __init__(self, socket_path: Path, handler: IPCHandler) -> None:
        self.socket_path = socket_path
        self.handler = handler
        self.server: asyncio.Server | None = None

    async def start(self) -> None:
        """Start listening on Unix socket."""
        # Check if socket file exists and if it's actually in use
        if self.socket_path.exists():
            if await self._is_socket_in_use():
                raise RuntimeError(
                    f"Socket {self.socket_path} is already in use by another process. "
                    "Another daemon may be running. Use 'mcpl session stop' first."
                )
            # Socket exists but not in use - safe to remove (stale)
            logger.debug(f"Removing stale socket file: {self.socket_path}")
            self.socket_path.unlink()

        self.server = await asyncio.start_unix_server(
            self._handle_client, path=str(self.socket_path)
        )

    async def _is_socket_in_use(self) -> bool:
        """Check if the socket file is actually in use by trying to connect."""
        try:
            _reader, writer = await asyncio.wait_for(
                asyncio.open_unix_connection(str(self.socket_path)),
                timeout=1.0,
            )
            # Connection succeeded - socket is in use
            writer.close()
            await writer.wait_closed()
            return True
        except (ConnectionRefusedError, FileNotFoundError, asyncio.TimeoutError):
            # Socket file exists but no one is listening - it's stale
            return False
        except Exception as e:
            logger.debug(f"Error checking socket: {e}")
            # Assume stale on any other error
            return False

    async def stop(self) -> None:
        """Stop the server and cleanup."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        if self.socket_path.exists():
            self.socket_path.unlink()

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle a client connection."""
        try:
            message = await read_message(reader)
            if message:
                try:
                    response = await self.handler(message)
                    await write_message(writer, response)
                except Exception as e:
                    logger.exception(f"Error in IPC handler: {e}")
                    # Send error response to client instead of silently closing
                    error_response = IPCMessage(
                        action="error", payload={"error": str(e)}
                    )
                    try:
                        await write_message(writer, error_response)
                    except Exception as write_err:
                        logger.debug(
                            f"Failed to send error response (connection broken): {write_err}"
                        )
        except Exception as e:
            logger.exception(f"Error handling IPC client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()


class WindowsIPCServer(IPCServer):
    """Windows named pipe-based IPC server.

    Note: Windows support is experimental. The named pipe implementation
    may have limitations compared to Unix sockets.
    """

    def __init__(self, pipe_name: str, handler: IPCHandler) -> None:
        self.pipe_name = pipe_name
        self.handler = handler
        self._running = False
        self._server_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Start listening on named pipe."""
        self._running = True
        self._server_task = asyncio.create_task(self._run_server())

    async def stop(self) -> None:
        """Stop the server."""
        self._running = False
        if self._server_task:
            self._server_task.cancel()
            try:
                await self._server_task
            except asyncio.CancelledError:
                pass

    async def _run_server(self) -> None:
        """Main server loop for Windows named pipes."""
        import ctypes  # noqa: PLC0415

        PIPE_ACCESS_DUPLEX = 0x00000003
        PIPE_TYPE_MESSAGE = 0x00000004
        PIPE_READMODE_MESSAGE = 0x00000002
        PIPE_WAIT = 0x00000000
        PIPE_UNLIMITED_INSTANCES = 255
        BUFFER_SIZE = 65536
        INVALID_HANDLE_VALUE = -1

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]

        while self._running:
            # Create named pipe
            pipe_handle = kernel32.CreateNamedPipeW(
                self.pipe_name,
                PIPE_ACCESS_DUPLEX,
                PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
                PIPE_UNLIMITED_INSTANCES,
                BUFFER_SIZE,
                BUFFER_SIZE,
                0,
                None,
            )

            if pipe_handle == INVALID_HANDLE_VALUE:
                await asyncio.sleep(0.1)
                continue

            try:
                # Wait for client connection (in thread to not block)
                connected = await asyncio.to_thread(
                    kernel32.ConnectNamedPipe, pipe_handle, None
                )
                if connected or kernel32.GetLastError() == 535:  # ERROR_PIPE_CONNECTED
                    await self._handle_pipe_client(kernel32, pipe_handle)
            finally:
                kernel32.CloseHandle(pipe_handle)

    async def _handle_pipe_client(self, kernel32: Any, pipe_handle: Any) -> None:
        """Handle a client connected via named pipe."""
        import ctypes  # noqa: PLC0415

        BUFFER_SIZE = 65536

        # Read message
        buffer = ctypes.create_string_buffer(BUFFER_SIZE)
        bytes_read = ctypes.c_ulong(0)

        success = await asyncio.to_thread(
            kernel32.ReadFile,
            pipe_handle,
            buffer,
            BUFFER_SIZE,
            ctypes.byref(bytes_read),
            None,
        )

        if success and bytes_read.value > 0:
            try:
                # Parse message - skip the 4-byte length header prefix
                message = IPCMessage.from_bytes(
                    buffer.raw[HEADER_SIZE : bytes_read.value]
                )
                response = await self.handler(message)

                # Write response
                response_bytes = response.to_bytes()
                bytes_written = ctypes.c_ulong(0)
                await asyncio.to_thread(
                    kernel32.WriteFile,
                    pipe_handle,
                    response_bytes,
                    len(response_bytes),
                    ctypes.byref(bytes_written),
                    None,
                )
            except Exception as e:
                logger.debug(f"Windows pipe client error: {e}")


async def connect_to_daemon() -> (
    tuple[asyncio.StreamReader, asyncio.StreamWriter] | None
):
    """Connect to the daemon IPC endpoint.

    Returns (reader, writer) tuple or None if connection failed.
    """
    socket_path = get_socket_path()

    if IS_WINDOWS:
        return await _connect_windows(str(socket_path))
    else:
        return await _connect_unix(socket_path)


async def _connect_unix(
    socket_path: Path,
) -> tuple[asyncio.StreamReader, asyncio.StreamWriter] | None:
    """Connect to Unix socket."""
    if not socket_path.exists():
        return None

    try:
        reader, writer = await asyncio.open_unix_connection(str(socket_path))
        return reader, writer
    except (ConnectionRefusedError, FileNotFoundError):
        return None


async def _connect_windows(
    pipe_name: str,
) -> tuple[asyncio.StreamReader, asyncio.StreamWriter] | None:
    """Connect to Windows named pipe.

    Note: Windows support is experimental.
    """
    import ctypes  # noqa: PLC0415

    GENERIC_READ = 0x80000000
    GENERIC_WRITE = 0x40000000
    OPEN_EXISTING = 3
    INVALID_HANDLE_VALUE = -1

    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]

    # Try to open the pipe
    handle = kernel32.CreateFileW(
        pipe_name,
        GENERIC_READ | GENERIC_WRITE,
        0,
        None,
        OPEN_EXISTING,
        0,
        None,
    )

    if handle == INVALID_HANDLE_VALUE:
        return None

    # Create asyncio-compatible streams from the pipe handle
    return _create_pipe_streams(kernel32, handle)


def _create_pipe_streams(
    kernel32: Any, handle: Any
) -> tuple[asyncio.StreamReader, Any]:
    """Create asyncio streams from a Windows pipe handle.

    Note: This is a simplified implementation for Windows named pipes.
    Windows support is experimental and may have limitations.
    """
    import ctypes  # noqa: PLC0415

    BUFFER_SIZE = 65536

    # For Windows, we create a custom reader/writer that wraps the pipe handle
    class PipeReader:
        """Async reader that reads from a Windows pipe handle."""

        def __init__(self, kernel32: Any, handle: Any) -> None:
            self.kernel32 = kernel32
            self.handle = handle
            self._buffer = b""
            self._eof = False

        async def _read_from_pipe(self, size: int) -> bytes:
            """Read data from the pipe handle in a thread."""
            buffer = ctypes.create_string_buffer(size)
            bytes_read = ctypes.c_ulong(0)

            # Read in thread to avoid blocking
            success = await asyncio.to_thread(
                self.kernel32.ReadFile,
                self.handle,
                buffer,
                size,
                ctypes.byref(bytes_read),
                None,
            )

            if success and bytes_read.value > 0:
                return buffer.raw[: bytes_read.value]
            return b""

        async def readexactly(self, n: int) -> bytes:
            """Read exactly n bytes from the pipe."""
            while len(self._buffer) < n:
                if self._eof:
                    raise asyncio.IncompleteReadError(self._buffer, n)
                chunk = await self._read_from_pipe(BUFFER_SIZE)
                if not chunk:
                    self._eof = True
                    raise asyncio.IncompleteReadError(self._buffer, n)
                self._buffer += chunk

            result = self._buffer[:n]
            self._buffer = self._buffer[n:]
            return result

    class PipeWriter:
        """Writer that writes to a Windows pipe handle."""

        def __init__(self, kernel32: Any, handle: Any) -> None:
            self.kernel32 = kernel32
            self.handle = handle
            self._closed = False

        def write(self, data: bytes) -> None:
            """Write data to the pipe (synchronous, buffered)."""
            if self._closed:
                return
            bytes_written = ctypes.c_ulong(0)
            self.kernel32.WriteFile(
                self.handle, data, len(data), ctypes.byref(bytes_written), None
            )

        async def drain(self) -> None:
            """Flush the write buffer (no-op for pipes)."""
            pass

        def close(self) -> None:
            """Close the pipe handle."""
            if not self._closed:
                self.kernel32.CloseHandle(self.handle)
                self._closed = True

        async def wait_closed(self) -> None:
            """Wait for close to complete (no-op)."""
            pass

    reader = PipeReader(kernel32, handle)
    writer = PipeWriter(kernel32, handle)
    return reader, writer  # type: ignore[return-value]


def create_ipc_server(handler: IPCHandler) -> IPCServer:
    """Create the appropriate IPC server for the current platform."""
    socket_path = get_socket_path()

    if IS_WINDOWS:
        return WindowsIPCServer(str(socket_path), handler)
    else:
        return UnixIPCServer(socket_path, handler)
