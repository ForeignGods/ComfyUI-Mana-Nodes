from .font2img_node import font2img
from .speech2text_node import speech2text
from .video2audio_node import video2audio
from .string2file_node import string2file
from .audio2video_node import audio2video
from .text2speech_node import text2speech
from .logger import logger

my_logger = logger()
my_logger.error("Mana Web")

WEB_DIRECTORY = "./web"

NODE_CLASS_MAPPINGS = {
    "font2img": font2img,
    "speech2text": speech2text,
    "video2audio": video2audio,
    "string2file": string2file,
    "audio2video": audio2video,
    "text2speech": text2speech
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "font2img": "font2img",
    "speech2text": "speech2text",
    "video2audio": "video2audio",
    "string2file":"string2file",
    "audio2video":"audio2video",
    "text2speech":"text2speech"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
