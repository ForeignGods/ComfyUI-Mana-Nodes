from torchvision.transforms.functional import to_tensor
import torch
import numpy as np
from moviepy.editor import AudioFileClip,ImageSequenceClip
import os
from ..helpers.utils import tensor2pil
from pathlib import Path
import folder_paths

class audio2video:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"display": "text", "forceInput": True}),
                "filename_prefix": ("STRING", {"default": "video\\video"})
            },
            "optional": {
                "audio_file": ("STRING", {"display": "text", "forceInput": True}),
                "fps": ("INT", {"default": 30, "min": 1, "max": 60, "step": 1})
            },
            "hidden": {
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            }

        }

    CATEGORY = "💠 Mana Nodes"
    RETURN_TYPES = ("STRING",) 
    RETURN_NAMES = ("video_file",)
    FUNCTION = "run"
    OUTPUT_NODE = True

    def run(self, **kwargs):
        fps = kwargs.get('fps', 30)
        
        # Prepare frames
        pil_frames = self.prepare_frames(kwargs['images'])

        # Construct video path
        full_path = self.construct_video_path(kwargs)
        
        # Create and save the video clip
        video_clip = self.create_video_clip(pil_frames, fps, kwargs.get('audio_file',None), full_path)

        # Generate preview metadata
        preview = self.generate_preview_metadata(full_path)

        #return {"ui": {"videos": preview}}
        return {"ui": {"videos": preview}, "result": ((True, full_path),)}

    
    def prepare_frames(self, images):
        pil_frames = []
        for frame in images:
            if not isinstance(frame, torch.Tensor):
                frame = to_tensor(frame)
            frame.permute(2, 1, 0)
            pil_image = tensor2pil(frame)
            pil_frames.append(pil_image)
        return pil_frames
    
    def construct_video_path(self, kwargs):
        base_directory = folder_paths.get_output_directory()
        filename_prefix = os.path.normpath(kwargs['filename_prefix'])
        full_path = os.path.join(base_directory, filename_prefix)

        # Ensure the path ends with .mp4
        if not full_path.endswith('.mp4'):
            full_path += '.mp4'

        # Increment filename if it already exists
        counter = 1
        while os.path.exists(full_path):
            # Construct a new path with an incremented number
            new_filename = f"{filename_prefix}_{counter}.mp4"
            full_path = os.path.join(base_directory, new_filename)
            counter += 1

        # Create the directory if it does not exist
        Path(os.path.dirname(full_path)).mkdir(parents=True, exist_ok=True)

        return full_path

    # def create_video_clip(self, frames, fps, audio_file_path, output_path):
    #     numpy_frames = [np.array(frame) for frame in frames]
    #     video_clip = ImageSequenceClip(numpy_frames, fps=fps)
    #     video_clip = video_clip.set_audio(AudioFileClip(audio_file_path))
    #     video_clip.write_videofile(output_path, codec="libx264", fps=fps)
    #     return video_clip
    
    def create_video_clip(self, pil_frames, fps, audio_file, full_path):
        numpy_frames = [np.array(frame) for frame in pil_frames]
        video_clip = ImageSequenceClip(numpy_frames, fps=fps)

        # Add audio to the video clip if audio_file is not None
        if audio_file is not None:
            audio_clip = AudioFileClip(audio_file)
            video_clip = video_clip.set_audio(audio_clip)

        # Write the video clip to a file
        video_clip.write_videofile(full_path, codec='libx264')

        return video_clip
    
    def generate_preview_metadata(self, full_path):
        filename = os.path.basename(full_path)
        parent_folder = os.path.dirname(full_path)

        # Check if the parent folder is the output folder
        if os.path.basename(parent_folder) == 'output':
            subfolder = ''  # No subfolder
        else:
            subfolder = os.path.basename(parent_folder)  # Subfolder exists

        return [
            {
                "filename": filename,
                "subfolder": subfolder,
                "type": "output",
                "format": "video/mp4",
            }
        ]
    
    #@classmethod
    #def IS_CHANGED(cls, video, *args, **kwargs):
    #    video_path = folder_paths.get_annotated_filepath(video)
    #    m = hashlib.sha256()
    #    with open(video_path, "rb") as f:
    #        m.update(f.read())
    #    return m.digest().hex()

    #@classmethod
    #def VALIDATE_INPUTS(cls, video, *args, **kwargs):
    #    if not folder_paths.exists_annotated_filepath(video):
    #        return "Invalid video file: {}".format(video)
    #    return True
