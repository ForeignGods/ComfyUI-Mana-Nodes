from .font2img_node import font2img
from .speech2text_node import speech2text
from .video2audio_node import video2audio
from .string2file_node import string2file
from .audio2video_node import audio2video

NODE_CLASS_MAPPINGS = {
    "font2img": font2img,
    "speech2text": speech2text,
    "video2audio": video2audio,
    "string2file": string2file,
    "audio2video": audio2video
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "font2img": "font2img",
    "speech2text": "speech2text",
    "video2audio": "video2audio",
    "string2file":"string2file",
    "audio2video":"audio2video"
}