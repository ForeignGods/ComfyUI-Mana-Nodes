from matplotlib import font_manager
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageColor

class scheduled_element:

    FONTS = {}
    FONT_NAMES = []

    def __init__(self):
        pass

    @classmethod
    def system_font_names(self):
        mgr = font_manager.FontManager()
        return {font.name: font.fname for font in mgr.ttflist}

    @classmethod
    def get_font_files(self, font_dir):
        extensions = ['.ttf', '.otf', '.woff', '.woff2']
        return [os.path.join(font_dir, f) for f in os.listdir(font_dir)
                if os.path.isfile(os.path.join(font_dir, f)) and f.endswith(tuple(extensions))]
    
    @classmethod
    def setup_font_directories(self):
        script_dir = os.path.dirname(os.path.dirname(__file__))
        custom_font_files = []
        for dir_name in ['font', 'font_files']:
            font_dir = os.path.join(script_dir, dir_name)
            if os.path.exists(font_dir):
                custom_font_files.extend(self.get_font_files(font_dir))
        return custom_font_files
    
    @classmethod
    def combined_font_list(self):
        system_fonts = self.system_font_names()
        custom_font_files = self.setup_font_directories()

        # Create a dictionary for custom fonts mapping font file base names to their paths
        custom_fonts = {os.path.splitext(os.path.basename(f))[0]: f for f in custom_font_files}

        # Merge system_fonts and custom_fonts dictionaries
        all_fonts = {**system_fonts, **custom_fonts}
        return all_fonts
    
    def get_font(self, font_name, font_size) -> ImageFont.FreeTypeFont:
        font_file = self.FONTS[font_name]
        return ImageFont.truetype(font_file, font_size)

    @classmethod
    def INPUT_TYPES(cls):
        cls.FONTS = cls.combined_font_list()
        cls.FONT_NAMES = sorted(cls.FONTS.keys())
        return {
            "required": {
                "font_file": (cls.FONT_NAMES, {"default": cls.FONT_NAMES[0]}),
                "font_color": ("STRING", {"default": "red", "display": "text"}),
                "kerning": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "line_spacing": ("INT", {"default": 5, "step": 1, "display": "number"}),
                "border_width": ("INT", {"default": 0, "min": 0, "step": 1, "display": "number"}),
                "border_color": ("INT", {"default": 0, "min": 0, "step": 1, "display": "number"}),
                "shadow_color": ("STRING", {"default": "red", "display": "text"}),
                "shadow_offset_x": ("INT", {"default": 0, "min": 0, "step": 1, "display": "number"}),
                "shadow_offset_y": ("INT", {"default": 0, "min": 0, "step": 1, "display": "number"}),
                "font_size": ("INT", {"default": 75, "min": 1, "step": 1, "display": "number"}),
                "x_offset": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "y_offset": ("SCHEDULED_VALUES", {"default": None,"forceInput": True}),
                "rotation": ("INT", {"default": 0, "min": -360, "max": 360, "step": 1}),
                "rotation_anchor_x": ("INT", {"default": 0, "step": 1}),
                "rotation_anchor_y": ("INT", {"default": 0, "step": 1}),
            },
        }

    CATEGORY = "Mana Nodes"
    RETURN_TYPES = ("TEXT_GRAPHIC_ELEMENT",)
    RETURN_NAMES = ("text_graphic_element",)
    FUNCTION = "run"

    def run(self, **kwargs):

        settings = {
            'font_file': kwargs.get('font_file'),
            'font_color': kwargs.get('font_color'),
            'kerning': kwargs.get('kerning'),
            'line_spacing': kwargs.get('line_spacing'),
            'border_width': kwargs.get('border_width'),
            'border_color': kwargs.get('border_color'),
            'shadow_color': kwargs.get('shadow_color'),
            'shadow_offset_x': kwargs.get('shadow_offset_x'),
            'shadow_offset_y': kwargs.get('shadow_offset_y'),
            'font_size': kwargs.get('font_size'),
            'x_offset': kwargs.get('x_offset'),
            'y_offset': kwargs.get('y_offset'),
            'rotation': kwargs.get('rotation'),
            'rotation_anchor_x': kwargs.get('rotation_anchor_x'),
            'rotation_anchor_y': kwargs.get('rotation_anchor_y')
        }

        return (settings,)

