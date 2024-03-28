import librosa
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import requests
import json

class speech2text:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        spell_check_options = ["English", "Spanish", "French", 
                "Portuguese", "German", "Italian", 
                "Russian", "Arabic", "Basque", "Latvian", "Dutch"]
        transcription_mode = ["word","line","fill"]
        return {
            "required": {
                "audio_file": ("STRING", {"display": "text","forceInput": True}),
                "wav2vec2_model": (cls.get_wav2vec2_models(), {"display": "dropdown", "default": "ailegends/xlsr-jonatasgrosman-wav2vec2-large-xlsr-53-english"}),
                "spell_check_language": (spell_check_options, {"default": "English", "display": "dropdown"}),
                "framestamps_max_chars": ("INT", {"default": 25, "step": 1, "display": "number"}),
                "fps": ("INT", {"default": 30, "min": 1, "max": 60, "step": 1}),
                "transcription_mode": (transcription_mode, {"default": "fill", "display": "dropdown"}),
                "uppercase": ("BOOLEAN", {"default": True})
            }          
        }

    CATEGORY = "Mana Nodes"
    RETURN_TYPES = ("TRANSCRIPTION", "STRING","STRING","STRING",)
    RETURN_NAMES = ("transcription", "raw_string","framestamps_string","timestamps_string",)
    FUNCTION = "run"
    OUTPUT_NODE = True

    def run(self, audio_file, wav2vec2_model, spell_check_language,framestamps_max_chars,**kwargs):
        fps = kwargs.get('fps',30)
        # Load and process with Wav2Vec2 model
        audio_array = self.audiofile_to_numpy(audio_file)
        raw_transcription = self.transcribe_with_timestamps(audio_array, wav2vec2_model)

        # Correct with spell checker
        corrected_transcription = self.correct_transcription_with_language_model(raw_transcription, spell_check_language)
        
        if kwargs['uppercase'] != True:
        # Assuming 'transcriptions' is a list of dictionaries
            corrected_transcription = [(word.lower(), start_time, end_time) for word, start_time, end_time in corrected_transcription]
        
        # Generate string formatted like JSON for transcription with timestamps
        frame_structure_transcription = self.transcription_to_frame_structure_string(corrected_transcription,fps,framestamps_max_chars)
        
        # Convert raw transcription to string format
        raw_transcription_string = self.transcription_to_string(corrected_transcription)
        
        # Convert raw transcription to string format
        json = self.transcription_to_json_string(corrected_transcription)

        print('corrected_transcription:',corrected_transcription,'type:',type(corrected_transcription))
        
        settings_dict = {
            "transcription_data": corrected_transcription,  # This is your list of tuples
            "fps": fps,                                    # Assuming fps is a variable holding the fps value
            "transcription_mode": kwargs['transcription_mode']       # Assuming transcription_mode is a variable holding the mode as a string
        }

        return (settings_dict, raw_transcription_string,frame_structure_transcription,json,)

    def transcription_to_string(self, raw_transcription):
        # Convert a list of (word, start_time, end_time) tuples to a string
        return ' '.join([word for word, start_time, end_time in raw_transcription])

    def transcription_to_frame_structure_string(self, corrected_transcription, fps, framestamps_max_chars):
        formatted_transcription = ""
        current_sentence = ""
        sentence_start_frame = -1

        for word, start_time, _ in corrected_transcription:
            frame_number = round(start_time * fps)

            if sentence_start_frame == -1:
                sentence_start_frame = frame_number  # Initialize start frame for the first word

            if len(current_sentence + " " + word) <= framestamps_max_chars:
                if current_sentence:  # Add space before word if sentence is not empty
                    current_sentence += " "
                current_sentence += word
                formatted_transcription += f'"{frame_number}": "{current_sentence}",\n'
            else:
                # Start a new sentence when max_chars is reached
                current_sentence = word
                sentence_start_frame = frame_number
                formatted_transcription += f'"{frame_number}": "{current_sentence}",\n'

        return formatted_transcription
    
    def transcription_to_json_string(self, raw_transcription):
        # Convert raw transcription with timestamps to a string formatted like JSON
        transcription_data = [{"word": word, "start_time": start_time, "end_time": end_time} for word, start_time, end_time in raw_transcription]
        return json.dumps(transcription_data, indent=2)

    def correct_transcription_with_language_model(self, raw_transcription,spell_check_language):
        
        # Mapping of full language names to their ISO language codes
        language_code_map = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "Portuguese": "pt",
            "German": "de",
            "Italian": "it",
            "Russian": "ru",
            "Arabic": "ar",
            "Basque": "eu",
            "Latvian": "lv",
            "Dutch": "nl"
        }
            
        language_code = language_code_map.get(spell_check_language, "en")  # Default to English if not found

        try:
            from spellchecker import SpellChecker
            spell = SpellChecker(language=language_code)  # Specify English language
        except ImportError:
            print("SpellChecker module is NOT accessible.")
            # Return the original transcription if spellchecker is not available
            return raw_transcription

        # Correct each word in the transcription
        corrected_transcription = []
        for word, start_time, end_time in raw_transcription:
            # Attempt to correct the word
            corrected_word = spell.correction(word)
            # Use the original word if no correction is found or if the correction returns None
            corrected_word = corrected_word if corrected_word else word
            corrected_transcription.append((corrected_word.upper(), start_time, end_time))

        return corrected_transcription


    def transcribe_with_timestamps(self, audio_array,wave2vec_model):
        model = Wav2Vec2ForCTC.from_pretrained(wave2vec_model)
        processor = Wav2Vec2Processor.from_pretrained(wave2vec_model)

        inputs = processor(audio_array, sampling_rate=16000, return_tensors="pt", padding=True)

        with torch.no_grad():
            logits = model(inputs.input_values).logits

        predicted_ids = torch.argmax(logits, dim=-1)

        # Calculate timestamps
        raw_timestamps = self.calculate_timestamps(predicted_ids, inputs.input_values.shape[1], processor)

        # Filter out padding tokens from timestamps
        timestamps = [(token, time) for token, time in raw_timestamps if token != "<pad>"]

        # Group tokens into words
        word_timestamps = self.group_timestamps_into_words(timestamps)

        return word_timestamps
    
    def group_timestamps_into_words(self, filtered_timestamps):
        words = []
        current_word = []
        for token, time in filtered_timestamps:
            if token == '|':
                if current_word:
                    start_time = current_word[0][1]
                    end_time = current_word[-1][1]
                    word_string = ''.join([t[0] for t in current_word])  # Concatenate tokens into a single string
                    words.append((word_string, start_time, end_time))
                    current_word = []
            else:
                current_word.append((token, time))

        # Check if there are remaining tokens in the last word
        if current_word:
            start_time = current_word[0][1]
            end_time = current_word[-1][1]
            word_string = ''.join([t[0] for t in current_word])  # Concatenate tokens into a single string
            words.append((word_string, start_time, end_time))

        return words
    
    def calculate_timestamps(self, predicted_ids, input_length, processor):
        # Approximate stride (20ms window for 16kHz audio)
        stride = int(0.02 * 16000)  

        timestamps = []
        current_time = 0.0

        for idx in range(predicted_ids.shape[1]):
            if predicted_ids[0, idx].item() != -100:  # Skip padding tokens
                current_time = (stride * idx) / 16000  # Convert from samples to seconds
                token = processor.tokenizer.convert_ids_to_tokens(predicted_ids[0, idx].item())
                timestamps.append((token, current_time))

        return timestamps
    
    def group_tokens_to_words(self, timestamps):
        word_timestamps = []
        current_word = ""
        word_start_time = None

        for token, time in timestamps:
            if token == "<pad>":
                continue

            if token.startswith("▁"):  # Indicates start of a new word
                if current_word:
                    # Complete the current word and reset for the next word
                    word_end_time = time
                    word_timestamps.append((current_word, word_start_time, word_end_time))
                    current_word = ""
                # Start a new word, remove the "▁" character
                current_word = token[1:]
                word_start_time = time
            else:
                # Continue building the current word
                current_word += token

        # Add the last word if present
        if current_word:
            word_timestamps.append((current_word, word_start_time, timestamps[-1][1]))

        return word_timestamps
    
    def get_wav2vec2_models():
        # Query Hugging Face Models API for Wav2Vec2 models
        url = "https://huggingface.co/api/models?search=wav2vec2"
        response = requests.get(url)
        models = response.json()

        # Extract model names
        model_names = [model['modelId'] for model in models]
        return model_names
    
    
    @staticmethod
    def audiofile_to_numpy(file_path, sr=16000):
        try:
            audio, _ = librosa.load(file_path, sr=sr)
            return audio
        except Exception as e:
            print("Error loading audio file:", e)
            return None
        
