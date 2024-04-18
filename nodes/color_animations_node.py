class color_animations:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        animation_reset = ["word", "line", "never","looped","pingpong"]
        color_animations = ["rainbow", "sunset", "grey"]
        return {
            "required": {
                "animation_duration": ("INT", {"default": 30, "step": 1, "display": "number"}),
                "color_animations": (color_animations, {"default": "rainbow", "display": "dropdown"}),
                "animation_reset": (animation_reset, {"default": "word", "display": "dropdown"}),

            }         
        }

    CATEGORY = "Mana Nodes"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("scheduled_colors",)
    FUNCTION = "run"

    def run(self, **kwargs):
        color_animations = kwargs.get('color_animations')
        animation_reset = kwargs.get('animation_reset')
        animation_duration = kwargs.get('animation_duration')

        scheduled_values = self.generate_color_schedule(color_animations, animation_duration, animation_reset)
        return (scheduled_values,)

    def generate_color_schedule(self, color_type, duration, animation_reset):
        # Define colors for each type
        color_definitions = {
            "rainbow": [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)],
            "sunset": [(255, 76, 0), (255, 108, 0), (255, 139, 0), (255, 171, 0), (255, 203, 0)],
            "grey": [(50, 50, 50), (100, 100, 100), (150, 150, 150), (200, 200, 200), (250, 250, 250)]
            # TODO: add more color animations here
        }

        colors = color_definitions.get(color_type, [(0, 0, 0)])  # Default to black if type is unknown
        color_schedule = []
        
        for i in range(duration):
            # Interpolate color
            t = i / duration
            index = int(t * (len(colors) - 1))
            next_index = min(index + 1, len(colors) - 1)
            fraction = (t * (len(colors) - 1)) - index
            color = tuple(int((1 - fraction) * colors[index][j] + fraction * colors[next_index][j]) for j in range(3))
            
            color_schedule.append({'x': i + 1, 'y': color})

        return (color_schedule, animation_reset)