import os
from pathlib import Path

class string2file:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"default": None, "display": "string", "forceInput": True}),
                "filename_prefix": ("STRING", {"default": "text_files\\text"})
            }
        }

    CATEGORY = "Mana Nodes"
    RETURN_TYPES = ()
    FUNCTION = "run"
    OUTPUT_NODE = True

    def run(self, string, filename_prefix):
        try:
            script_dir = os.path.dirname(os.path.dirname(__file__))

            # Check if filename_prefix contains directory information
            if "\\" in filename_prefix or "/" in filename_prefix:
                # Normalize path
                file_name_with_path = os.path.normpath(filename_prefix)
                # Join with script directory
                full_path = os.path.join(script_dir, file_name_with_path)
                directory = os.path.dirname(full_path)
                # Create directory if it doesn't exist
                Path(directory).mkdir(parents=True, exist_ok=True)
            else:
                full_path = os.path.join(script_dir, filename_prefix)

            # Append .txt if not present
            if not full_path.endswith('.txt'):
                full_path += '.txt'

            # Write the string to the file
            with open(full_path, 'w') as file:
                file.write(string)
            return (None,)
        except Exception as e:
            return str(e),