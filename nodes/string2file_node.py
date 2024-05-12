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
    CATEGORY = "💠 Mana Nodes"
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "run"
    OUTPUT_NODE = True

    def run(self, string,unique_id = None, extra_pnginfo=None, **kwargs):

        full_path = self.construct_text_path(kwargs)

        # Write the string to the file
        with open(full_path, 'w') as file:
            file.write(string[0])

        if unique_id and extra_pnginfo and "workflow" in extra_pnginfo[0]:
            workflow = extra_pnginfo[0]["workflow"]
            node = next((x for x in workflow["nodes"] if str(x["id"]) == unique_id[0]), None)
            if node:
                node["widgets_values"] = [string]

        return {"ui": {"text": string}, "result": (string,)}
    
    def construct_text_path(self, kwargs):
        base_directory = folder_paths.get_output_directory()
        filename_prefix = os.path.normpath(kwargs['filename_prefix'][0])
        full_path = os.path.join(base_directory, filename_prefix)

        # Ensure the path ends with .mp4
        if not full_path.endswith('.txt'):
            full_path += '.txt'

        # Increment filename if it already exists
        counter = 1
        while os.path.exists(full_path):
            # Construct a new path with an incremented number
            new_filename = f"{filename_prefix}_{counter}.txt"
            full_path = os.path.join(base_directory, new_filename)
            counter += 1

        # Create the directory if it does not exist
        Path(os.path.dirname(full_path)).mkdir(parents=True, exist_ok=True)

        return full_path