from .nodes.font2img_node import font2img
from .nodes.speech2text_node import speech2text
from .nodes.video2audio_node import video2audio
from .nodes.string2file_node import string2file
from .nodes.audio2video_node import audio2video
from .nodes.text2speech_node import text2speech
from .nodes.canvas_settings_node import canvas_settings
from .nodes.scheduled_values_node import scheduled_values
from .nodes.color_animations_node import color_animations
from .nodes.text_graphic_element_node import text_graphic_element
from .helpers.logger import logger

my_logger = logger()
my_logger.error("Mana Web")

WEB_DIRECTORY = "./web"

NODE_CLASS_MAPPINGS = {
    "font2img": font2img,
    "speech2text": speech2text,
    "video2audio": video2audio,
    "string2file": string2file,
    "audio2video": audio2video,
    "text2speech": text2speech,
    "canvas_settings": canvas_settings,
    "text_graphic_element": text_graphic_element,
    "scheduled_values": scheduled_values,
    "color_animations": color_animations
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "font2img": "✒️ Text to Image Generator",
    "speech2text": "🎤 Speech Recognition",
    "video2audio": "🎞️ Split Video",
    "string2file":"📝 Save/Preview Text",
    "audio2video":"🎥 Combine Video",
    "text2speech":"📣 Generate Audio",
    "canvas_settings":"🖼️ Canvas Properties",
    "text_graphic_element":"🆗 Font Properties",
    "scheduled_values":"⏰ Scheduled Values",
    "color_animations":"🌈 Preset Color Animations"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
