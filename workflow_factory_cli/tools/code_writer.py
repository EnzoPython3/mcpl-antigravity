
import os
from typing import Dict, Any

class CodeWriterTool:
    """A tool for writing code or text to a file."""

    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        """Returns the OpenAPI schema for the code writer tool."""
        return {
            "name": "code_writer",
            "description": "Writes a given string content to a specified file. Use this to save generated code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The relative path to the file to be written (e.g., 'src/my_code.js')."
                    },
                    "content": {
                        "type": "string",
                        "description": "The string content to write to the file."
                    }
                },
                "required": ["file_path", "content"]
            }
        }

    def execute(self, file_path: str, content: str) -> str:
        """
        Executes the code writing tool.

        Args:
            file_path: The path to the file.
            content: The content to write.

        Returns:
            A string indicating success or failure.
        """
        try:
            # Create directories if they don't exist
            dir_name = os.path.dirname(file_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

            with open(file_path, 'w') as f:
                f.write(content)
            
            return f"Successfully wrote code to {file_path}."
        except Exception as e:
            return f"Error writing to file {file_path}: {e}"

