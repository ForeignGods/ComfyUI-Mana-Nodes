class scheduled_values:

    def __init__(self):
        self.line_spacing = 5

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frame_count": ("INT", {"default": 30, "step": 1, "display": "number"}),
                "value_range": ("INT", {"default": 15, "step": 1, "display": "number"}),
            },            
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO"
            }
        }

    CATEGORY = "Mana Nodes"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("scheduled_values",)
    FUNCTION = "run"

    def run(self, **kwargs):
        scheduled_values = str(kwargs['frame_count'])
        return (scheduled_values,)