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
                "filename_prefix": ("STRING", {"default": "text\\text"}),
                "string": ("STRING", {"forceInput": True}),                
            },            
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO"
            }
            
        }
    
    INPUT_IS_LIST = True
    CATEGORY = "Mana Nodes"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_file",)
    FUNCTION = "run"
    OUTPUT_NODE = True

    def run(self, string, filename_prefix,unique_id = None, extra_pnginfo=None):
        full_path = os.path.join(folder_paths.get_output_directory(), os.path.normpath(filename_prefix[0]))
        if not full_path.endswith('.txt'):
            full_path += '.txt'
        Path(os.path.dirname(full_path)).mkdir(parents=True, exist_ok=True)

        # Write the string to the file
        with open(full_path, 'w') as file:
            file.write(string[0])

        if unique_id and extra_pnginfo and "workflow" in extra_pnginfo[0]:
            workflow = extra_pnginfo[0]["workflow"]
            node = next((x for x in workflow["nodes"] if str(x["id"]) == unique_id[0]), None)
            if node:
                node["widgets_values"] = [string]

        return {"ui": {"text": string}, "result": (string,)}