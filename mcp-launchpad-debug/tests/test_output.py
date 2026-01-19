"""Tests for output module."""

import json

import pytest

from mcp_launchpad.output import (
    OutputHandler,
    format_error_json,
    format_json,
)


class TestFormatJson:
    """Tests for format_json function."""

    def test_format_success(self):
        """Test formatting successful response."""
        result = format_json({"key": "value"})
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"] == {"key": "value"}

    def test_format_success_with_list(self):
        """Test formatting list data."""
        result = format_json([1, 2, 3])
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"] == [1, 2, 3]

    def test_format_success_false(self):
        """Test formatting with success=False."""
        error_data = {"success": False, "error": "message"}
        result = format_json(error_data, success=False)
        parsed = json.loads(result)
        assert parsed == error_data


class TestFormatErrorJson:
    """Tests for format_error_json function."""

    def test_basic_error(self):
        """Test formatting a basic error."""
        error = ValueError("Something went wrong")
        result = format_error_json(error)
        parsed = json.loads(result)

        assert parsed["success"] is False
        assert parsed["error"]["type"] == "ValueError"
        assert parsed["error"]["message"] == "Something went wrong"
        assert "traceback" in parsed["error"]

    def test_error_with_type_override(self):
        """Test formatting error with custom type."""
        error = Exception("Generic error")
        result = format_error_json(error, error_type="CustomError")
        parsed = json.loads(result)

        assert parsed["error"]["type"] == "CustomError"

    def test_error_with_help_text(self):
        """Test formatting error with help text."""
        error = ValueError("Bad value")
        result = format_error_json(error, help_text="Try using a different value")
        parsed = json.loads(result)

        assert parsed["error"]["help"] == "Try using a different value"


class TestOutputHandler:
    """Tests for OutputHandler class."""

    def test_json_mode_flag(self):
        """Test json_mode flag is set correctly."""
        handler_json = OutputHandler(json_mode=True)
        handler_human = OutputHandler(json_mode=False)

        assert handler_json.json_mode is True
        assert handler_human.json_mode is False

    def test_default_human_mode(self):
        """Test default mode is human."""
        handler = OutputHandler()
        assert handler.json_mode is False

    def test_success_json_mode(self, capsys):
        """Test success output in JSON mode."""
        handler = OutputHandler(json_mode=True)
        handler.success({"result": "test"})

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["success"] is True
        assert parsed["data"]["result"] == "test"

    def test_success_human_mode_with_message(self, capsys):
        """Test success output in human mode with custom message."""
        handler = OutputHandler(json_mode=False)
        handler.success({"data": "value"}, human_message="Operation completed!")

        captured = capsys.readouterr()
        assert "Operation completed!" in captured.out

    def test_success_human_mode_default(self, capsys):
        """Test success output in human mode without custom message."""
        handler = OutputHandler(json_mode=False)
        handler.success({"key": "value"})

        captured = capsys.readouterr()
        # Should output JSON-formatted data
        assert "key" in captured.out
        assert "value" in captured.out

    def test_error_json_mode(self, capsys):
        """Test error output in JSON mode."""
        handler = OutputHandler(json_mode=True)

        with pytest.raises(SystemExit) as excinfo:
            handler.error(ValueError("Test error"), help_text="Try again")

        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["success"] is False
        assert parsed["error"]["message"] == "Test error"

    def test_error_human_mode(self, capsys):
        """Test error output in human mode."""
        handler = OutputHandler(json_mode=False)

        with pytest.raises(SystemExit) as excinfo:
            handler.error(ValueError("Human error"))

        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
        assert "Human error" in captured.err

    def test_table_json_mode(self, capsys):
        """Test table output in JSON mode."""
        handler = OutputHandler(json_mode=True)
        headers = ["Name", "Status"]
        rows = [["server1", "active"], ["server2", "inactive"]]
        handler.table(headers, rows)

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["success"] is True
        assert len(parsed["data"]) == 2
        assert parsed["data"][0] == {"Name": "server1", "Status": "active"}

    def test_table_human_mode(self, capsys):
        """Test table output in human mode."""
        handler = OutputHandler(json_mode=False)
        headers = ["Name", "Status"]
        rows = [["server1", "active"], ["server2", "inactive"]]
        handler.table(headers, rows)

        captured = capsys.readouterr()
        assert "Name" in captured.out
        assert "Status" in captured.out
        assert "server1" in captured.out
        assert "server2" in captured.out
