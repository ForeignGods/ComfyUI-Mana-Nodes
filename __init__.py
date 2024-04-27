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
    "Text to Image Generator": font2img,
    "Speech Recognition": speech2text,
    "Split Video": video2audio,
    "Save/Preview Text": string2file,
    "Combine Video": audio2video,
    "Generate Audio": text2speech,
    "Canvas Properties": canvas_settings,
    "Font Properties": text_graphic_element,
    "Scheduled Values": scheduled_values,
    "Preset Color Animations": color_animations
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Text to Image Generator": "✒️ Text to Image Generator",
    "Speech Recognition": "🎤 Speech Recognition",
    "Split Video": "🎞️ Split Video",
    "Save/Preview Text":"📝 Save/Preview Text",
    "Combine Video":"🎥 Combine Video",
    "Generate Audio":"📣 Generate Audio",
    "Canvas Properties":"🖼️ Canvas Properties",
    "Font Properties":"🆗 Font Properties",
    "Scheduled Values":"⏰ Scheduled Values",
    "Preset Color Animations":"🌈 Preset Color Animations"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
