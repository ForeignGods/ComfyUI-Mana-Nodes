from torchvision.transforms.functional import to_tensor
import torch
import numpy as np
from moviepy.editor import AudioFileClip,ImageSequenceClip
import os
from .utils import tensor2pil
from pathlib import Path

class audio2video:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio_file": ("STRING", {"display": "text", "forceInput": True}),
                "frames": ("IMAGE", {"display": "text", "forceInput": True}),
                "filename_prefix": ("STRING", {"default": "video_files\\video"}),
                "fps": ("INT", {"default": 30, "min": 1, "max": 60, "step": 1, "forceInput": True})
            },
            "optional": {}
        }

    CATEGORY = "Mana Nodes"
    RETURN_TYPES = ("STRING",) 
    RETURN_NAMES = ("video_file",)
    FUNCTION = "run"
    OUTPUT_NODE = True

    def run(self, audio_file, frames, filename_prefix, fps):
        # Ensure output filename has .mp4 extension
        if not filename_prefix.endswith('.mp4'):
            filename_prefix += '.mp4'

        pil_frames = []
        for frame in frames:
            # Convert frame to a tensor if it's not already
            if not isinstance(frame, torch.Tensor):
                frame = to_tensor(frame)

            frame.permute(2, 1, 0)

            pil_image = tensor2pil(frame)

            pil_frames.append(pil_image)

        # Convert PIL images to NumPy arrays and store in a list
        numpy_frames = [np.array(frame) for frame in pil_frames]
        
        # Get the current working directory
        script_dir = os.path.dirname(__file__)

        # Normalize and construct full path
        normalized_path = os.path.normpath(filename_prefix)
        full_path = os.path.join(script_dir, normalized_path)

        # Create directory if it doesn't exist
        Path(os.path.dirname(full_path)).mkdir(parents=True, exist_ok=True)

        # Ensure the filename has a .wav extension
        if not full_path.endswith('.mp4'):
            full_path += '.mp4'
        # Create a video clip from the list of NumPy array frames
        video_clip = ImageSequenceClip(numpy_frames, fps=fps)

        # Add audio to video
        audio_clip = AudioFileClip(audio_file)
        video_clip = video_clip.set_audio(audio_clip)

        output_path = os.path.join(script_dir, filename_prefix)

        # Write the video file
        video_clip.write_videofile(output_path, codec="libx264", fps=fps)

        return output_path
