import os
import cv2
import torch
import hashlib
import folder_paths
from .utils import ensure_opencv, pil2tensor
from PIL import Image
from pathlib import Path
from moviepy.editor import VideoFileClip

class video2audio:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        input_dir = os.path.join(folder_paths.get_input_directory(), "video")
        os.makedirs(input_dir, exist_ok=True)
        files = [f"video/{f}" for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {
            "required": {
                "video": (sorted(files), {"mana_video_upload": True}),
                "frame_limit": ("INT", {"default": 16, "min": 1, "max": 10240, "step": 1}),
                "frame_start": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF, "step": 1}),
                "filename_prefix": ("STRING", {"default": "audio_files\\audio"})
            },
            "optional": {}
        }

    CATEGORY = "Mana Nodes"
    RETURN_TYPES = ("IMAGE", "INT", "STRING", "INT", "INT","INT",) 
    RETURN_NAMES = ("frames", "frame_count", "audio","fps", "height", "width",)
    FUNCTION = "run"

    def run(self, video, frame_start, frame_limit, filename_prefix):
        video_path = folder_paths.get_annotated_filepath(video)
        frames, width, height = self.extract_frames(video_path, frame_start, frame_limit)        
        video_path = Path(video_path)
        audio, fps = self.extract_audio_with_moviepy(video_path, frame_start, frame_limit, filename_prefix)
        if not frames:
            raise ValueError("No frames could be extracted from the video.")
        if not audio:
            raise ValueError("No audio could be extracted from the video.")
        return (torch.cat(frames, dim=0), len(frames), audio, fps, height, width,)

    def extract_audio_with_moviepy(self, video_file_path, frame_start, frame_limit, filename_prefix):

        # Convert WindowsPath object to string
        video_file_path_str = str(video_file_path)

        # Load the video file
        video = VideoFileClip(video_file_path_str)

        # Calculate start and end time in seconds
        fps = video.fps  # frames per second
        start_time = frame_start / fps
        end_time = (frame_start + frame_limit) / fps

        # Get the current working directory
        script_dir = os.path.dirname(__file__)

        # Normalize and construct full path
        normalized_path = os.path.normpath(filename_prefix)
        full_path = os.path.join(script_dir, normalized_path)

        # Create directory if it doesn't exist
        Path(os.path.dirname(full_path)).mkdir(parents=True, exist_ok=True)

        # Ensure the filename has a .wav extension
        if not full_path.endswith('.wav'):
            full_path += '.wav'

        # Extract the specific audio segment
        audio = video.subclip(start_time, end_time).audio
        audio.write_audiofile(full_path)
        print("Audio file saved:", full_path)

        # Get full path to the audio file
        full_path_to_audio = os.path.abspath(full_path)
        print("Full path to the audio file:", full_path_to_audio)
        fps = video.fps

        return full_path_to_audio, fps

    def extract_frames(self, video_path, frame_start, frame_limit):
        ensure_opencv()
        video = cv2.VideoCapture(video_path)
        
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        video.set(cv2.CAP_PROP_POS_FRAMES, frame_start)

        frames = []
        for i in range(frame_limit):
            ret, frame = video.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(pil2tensor(Image.fromarray(frame)))
            else:
                break

        video.release()
        return frames, width, height

    @classmethod
    def IS_CHANGED(cls, video, *args, **kwargs):
        video_path = folder_paths.get_annotated_filepath(video)
        m = hashlib.sha256()
        with open(video_path, "rb") as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(cls, video, *args, **kwargs):
        if not folder_paths.exists_annotated_filepath(video):
            return "Invalid video file: {}".format(video)
        return True
