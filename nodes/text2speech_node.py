from transformers import pipeline
import scipy.io.wavfile
from pathlib import Path
import os

class text2speech:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"display": "text","placeholder": "Text","multiline": True}),
                "filename_prefix": ("STRING", {"display": "text", "default": "audio_files\\audio"})
            },
        }

    CATEGORY = "Mana Nodes"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("audio_file",)
    FUNCTION = "run"
    OUTPUT_NODE = True

    def run(self, text, filename_prefix):

        script_dir = os.path.dirname(os.path.dirname(__file__))
        normalized_path = os.path.normpath(filename_prefix)
        full_path = os.path.join(script_dir, normalized_path)
        if not full_path.endswith('.wav'):
            full_path += '.wav'  
        Path(os.path.dirname(full_path)).mkdir(parents=True, exist_ok=True)

        synthesizer = pipeline("text-to-speech", "suno/bark")
        speech = synthesizer(text, forward_params={"do_sample": True})

        audio_waveform = speech['audio']
        if audio_waveform.ndim == 2:
            # Transpose if it's in the wrong shape (num_channels, num_samples)
            audio_waveform = audio_waveform.T

        scipy.io.wavfile.write(full_path, rate=speech['sampling_rate'], data=audio_waveform)

        full_path_to_audio = os.path.abspath(full_path)
        return (full_path_to_audio,)

