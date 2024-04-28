class scheduled_values:

    def __init__(self):
        pass


    @classmethod
    def INPUT_TYPES(cls):
        animation_reset = ["word", "line", "never","looped","pingpong"]
        easing_types = [
            "linear",
            "easeInQuad",
            "easeOutQuad",
            "easeInOutQuad",
            "easeInCubic",
            "easeOutCubic",
            "easeInOutCubic",
            "easeInQuart",
            "easeOutQuart",
            "easeInOutQuart",
            "easeInQuint",
            "easeOutQuint",
            "easeInOutQuint",
            "exponential"
        ]        
        step_mode = ["single", "auto"]
        return {
            "required": {
                "frame_count": ("INT", {"default": 30, "step": 1, "display": "number"}),
                "value_range": ("INT", {"default": 15, "step": 1, "display": "number"}),
                "easing_type": (easing_types, {"default": "linear", "display": "dropdown"}),
                "step_mode": (step_mode, {"default": "single", "display": "dropdown"}),
                "animation_reset": (animation_reset, {"default": "word", "display": "dropdown"}),
                "id": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "scheduled_values": ("STRING", {"default": "[]", "display": "text","readOnly": True }),
            },            
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO"
            }
        }

    CATEGORY = "💠 Mana Nodes/📅 Value Scheduling"
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("scheduled_values",)
    FUNCTION = "run"

    def run(self, **kwargs):
        scheduled_values = str(kwargs['scheduled_values'])
        animation_reset = kwargs.get('animation_reset')
        # this should be ok but maybe change it  
        if scheduled_values == '[]':
            raise ValueError("scheduled_values is required and cannot be an empty list.")
        
        # this could also be more elegant
        scheduled_values = f"{scheduled_values}${animation_reset}"

        return (scheduled_values,)