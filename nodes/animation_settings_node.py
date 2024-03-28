class animation_settings:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        animation_reset = ["word", "line", "never"]
        animation_easing = ["linear", "exponential", "quadratic","cubic", "elastic", "bounce","back","ease_in_out_sine","ease_out_back","ease_in_out_expo"]

        return {
            "required": {
                "animation_reset": (animation_reset, {"default": "word", "display": "dropdown"}),
                "animation_easing": (animation_easing, {"default": "linear", "display": "dropdown"}),
                "animation_duration": ("INT", {"default": 10, "min": 1, "step": 1, "display": "number"}),
                "frame_count": ("INT", {"default": 10, "min": 1, "step": 1, "display": "number"}),
            },
        }

    CATEGORY = "Mana Nodes"
    RETURN_TYPES = ("ANIMATION_SETTINGS",)
    RETURN_NAMES = ("animation_settings",)
    FUNCTION = "run"

    def run(self, **kwargs):

        settings = {
            'animation_reset': kwargs.get('animation_reset'),
            'animation_easing': kwargs.get('animation_easing'),
            'animation_duration': kwargs.get('animation_duration'),
            'frame_count': kwargs.get('frame_count')
        }

        return (settings,)

