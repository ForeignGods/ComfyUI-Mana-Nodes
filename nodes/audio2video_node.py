from torchvision.transforms.functional import to_tensor
import torch
import numpy as np
from moviepy.editor import AudioFileClip,ImageSequenceClip
import os
from ..helpers.utils import tensor2pil
from pathlib import Path

class audio2video:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio_file": ("STRING", {"display": "text", "forceInput": True}),
                "images": ("IMAGE", {"display": "text", "forceInput": True}),
                "filename_prefix": ("STRING", {"default": "video_files\\video"})
            },
            "optional": {
                "fps": ("INT", {"default": 30, "min": 1, "max": 60, "step": 1})
            }
        }

    CATEGORY = "Mana Nodes"
    RETURN_TYPES = ("STRING",) 
    RETURN_NAMES = ("video_file",)
    FUNCTION = "run"
    OUTPUT_NODE = True

    def run(self, **kwargs):
        
        fps = kwargs.get('fps',30)
        
        pil_frames = []
        for frame in kwargs['images']:
            # Convert frame to a tensor if it's not already
            if not isinstance(frame, torch.Tensor):
                frame = to_tensor(frame)

            frame.permute(2, 1, 0)

            pil_image = tensor2pil(frame)

            pil_frames.append(pil_image)

        # Convert PIL images to NumPy arrays and store in a list
        numpy_frames = [np.array(frame) for frame in pil_frames]
        
        script_dir = os.path.dirname(os.path.dirname(__file__))
        normalized_path = os.path.normpath(kwargs['filename_prefix'])
        full_path = os.path.join(script_dir, normalized_path)
        Path(os.path.dirname(full_path)).mkdir(parents=True, exist_ok=True)
        if not full_path.endswith('.mp4'):
            full_path += '.mp4'

        # Create a video clip from the list of NumPy array frames
        video_clip = ImageSequenceClip(numpy_frames, fps=fps)

        video_clip = video_clip.set_audio(AudioFileClip(kwargs['audio_file']))

        # Write the video file
        video_clip.write_videofile(full_path, codec="libx264", fps=fps)

        return full_path
