
import subprocess
from typing import Dict, Any

class CodeExecutorTool:
    """
    A tool for executing code snippets in a sandboxed environment.
    Note: This implementation uses a simple subprocess and is not fully secure.
    A production system should use a more robust sandbox like Docker.
    """

    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        """Returns the OpenAPI schema for the code executor tool."""
        return {
            "name": "code_executor",
            "description": "Executes a code snippet (e.g., JavaScript) and returns its output and errors. Use this to test and debug generated code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "description": "The programming language of the code snippet (e.g., 'javascript')."
                    },
                    "code": {
                        "type": "string",
                        "description": "The code snippet to execute."
                    }
                },
                "required": ["language", "code"]
            }
        }

    def execute(self, language: str, code: str) -> Dict[str, str]:
        """
        Executes the code and captures stdout and stderr.

        Args:
            language: The programming language.
            code: The code to execute.

        Returns:
            A dictionary containing the stdout and stderr of the execution.
        """
        if language.lower() != 'javascript':
            return {"stdout": "", "stderr": "Unsupported language. Only JavaScript is supported."}

        try:
            # We use 'node -e' to execute the JavaScript code directly
            result = subprocess.run(
                ['node', '-e', code],
                capture_output=True,
                text=True,
                timeout=10  # Add a timeout for safety
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except FileNotFoundError:
            return {"stdout": "", "stderr": "'node' command not found. Please ensure Node.js is installed and in your PATH."}
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": "Code execution timed out."}
        except Exception as e:
            return {"stdout": "", "stderr": f"An unexpected error occurred during execution: {e}"}

