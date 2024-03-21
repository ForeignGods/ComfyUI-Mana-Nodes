import os
from pathlib import Path
import folder_paths

class string2file:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"default": None, "display": "string", "forceInput": True}),
                "filename_prefix": ("STRING", {"default": "text\\text"})
            }
        }

    CATEGORY = "Mana Nodes"
    RETURN_TYPES = ()
    FUNCTION = "run"
    OUTPUT_NODE = True

    def run(self, string, **kwargs):
        try:
            
            full_path = os.path.join(folder_paths.get_output_directory(), os.path.normpath(kwargs['filename_prefix']))
            # Append .txt if not present
            if not full_path.endswith('.txt'):
                full_path += '.txt'
            Path(os.path.dirname(full_path)).mkdir(parents=True, exist_ok=True)

            # Write the string to the file
            with open(full_path, 'w') as file:
                file.write(string)
            return (None,)
        except Exception as e:
            return str(e),