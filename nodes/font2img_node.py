import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageColor
import PIL
import numpy as np
import torch
from torchvision import transforms
import random
import math
from matplotlib import font_manager
import re

class font2img:

    FONTS = {}
    FONT_NAMES = []

    def __init__(self):
        pass

    @classmethod
    def system_font_names(self):
        mgr = font_manager.FontManager()
        return {font.name: font.fname for font in mgr.ttflist}

    @classmethod
    def get_font_files(self, font_dir):
        extensions = ['.ttf', '.otf', '.woff', '.woff2']
        return [os.path.join(font_dir, f) for f in os.listdir(font_dir)
                if os.path.isfile(os.path.join(font_dir, f)) and f.endswith(tuple(extensions))]
    
    @classmethod
    def setup_font_directories(self):
        script_dir = os.path.dirname(os.path.dirname(__file__))
        custom_font_files = []
        for dir_name in ['font', 'font_files']:
            font_dir = os.path.join(script_dir, dir_name)
            if os.path.exists(font_dir):
                custom_font_files.extend(self.get_font_files(font_dir))
        return custom_font_files
    
    @classmethod
    def combined_font_list(self):
        system_fonts = self.system_font_names()
        custom_font_files = self.setup_font_directories()

        # Create a dictionary for custom fonts mapping font file base names to their paths
        custom_fonts = {os.path.splitext(os.path.basename(f))[0]: f for f in custom_font_files}

        # Merge system_fonts and custom_fonts dictionaries
        all_fonts = {**system_fonts, **custom_fonts}
        return all_fonts
    
    def get_font(self, font_name, font_size) -> ImageFont.FreeTypeFont:
        font_file = self.FONTS[font_name]
        return ImageFont.truetype(font_file, font_size)

    @classmethod
    def INPUT_TYPES(self):

        self.FONTS = self.combined_font_list()
        self.FONT_NAMES = sorted(self.FONTS.keys())

        return {
            "required": {
                "main_font": ("TEXT_GRAPHIC_ELEMENT", {"default": None,"forceInput": True}),
                "text": ("STRING", {"multiline": True, "placeholder": "\"1\": \"Hello\",\n\"10\": \"Hello World\""}),
                "main_font": ("TEXT_GRAPHIC_ELEMENT", {"default": None,"forceInput": True}),
                "canvas_settings": ("CANVAS_SETTINGS", {"default": None,"forceInput": True}),
                "animation_settings": ("ANIMATION_SETTINGS", {"default": None,"forceInput": True}),
            },
            "optional": {
                "transcription": ("TRANSCRIPTION", {"default": None,"forceInput": True}),
                "highlight_font": ("TEXT_GRAPHIC_ELEMENT", {"default": None,"forceInput": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("images", "framestamps_string",)

    FUNCTION = "run"

    CATEGORY = "Mana Nodes"

    def run(self, **kwargs):
        if kwargs['transcription'] != None:
            formatted_transcription = self.format_transcription(kwargs)
            text = formatted_transcription
        else:
            formatted_transcription = None
            text = kwargs.get('text')

        frame_count = kwargs['animation_settings']['frame_count']

        frame_text_dict, is_structured_input = self.parse_text_input(text, kwargs)
        frame_text_dict = self.cumulative_text(frame_text_dict, frame_count)
        
        images = kwargs.get('canvas_settings', {}).get('images', [None] * frame_count)

        images = self.generate_images(frame_text_dict,images , kwargs)
        image_batch = torch.cat(images, dim=0)

        return (image_batch, formatted_transcription,)

    def format_transcription(self, kwargs):
        if not kwargs['transcription']:
            return ""

        transcription_fps = kwargs['transcription']['fps']

        transcription_mode = kwargs['transcription']['transcription_mode']
        transcription_data = kwargs['transcription']['transcription_data']
        image_width = kwargs['canvas_settings']['width']
        image_height = kwargs['canvas_settings']['height']
        padding = kwargs['canvas_settings']['padding']
        text_alignment = kwargs['canvas_settings']['text_alignment']

        formatted_transcription = ""
        current_sentence = ""
        first_transcribed_frame_number = None
        sentence_words = []  # To store the words of the current sentence
        sentence_frame_numbers = []  # To store frame numbers of each word in the current sentence
        print('transcription_data:',transcription_data)
        for i, (word, start_time, end_time) in enumerate(transcription_data):
            frame_number = round(start_time * transcription_fps)

            if not current_sentence:
                current_sentence = word
                sentence_words = [word]
                sentence_frame_numbers = [frame_number]
                if transcription_mode == "line":
                    first_transcribed_frame_number = frame_number
            else:
                new_sentence = current_sentence + " " + word
                width = self.get_text_width(new_sentence, kwargs)
                if width <= image_width - padding:
                    current_sentence = new_sentence
                    sentence_words.append(word)
                    sentence_frame_numbers.append(frame_number)
                else:
                    if transcription_mode == "line":
                        # Format each word in the sentence with tags and output with the corresponding frame number
                        for j, sentence_word in enumerate(sentence_words):
                            tagged_sentence = ' '.join(["<tag>{}</tag>".format(w) if j == k else w for k, w in enumerate(sentence_words)])
                            formatted_transcription += f'"{sentence_frame_numbers[j]}": "{tagged_sentence}",\n'
                        current_sentence = word
                        sentence_words = [word]
                        sentence_frame_numbers = [frame_number]
                    else:
                        current_sentence = word

            if transcription_mode == "fill":
                words = current_sentence.split()
                # Add tags around the last word in the sentence
                if words:
                    words[-1] = f"<tag>{words[-1]}</tag>"
                tagged_sentence = ' '.join(words)
                formatted_transcription += f'"{frame_number}": "{tagged_sentence}",\n'

            if transcription_mode == "word":
                formatted_transcription += f'"{frame_number}": "{word}",\n'

        # Handle the last sentence for 'line' and 'fill' modes
        if current_sentence:
            if transcription_mode == "line":
                for j, sentence_word in enumerate(sentence_words):
                    tagged_sentence = ' '.join(["<tag>{}</tag>".format(w) if j == k else w for k, w in enumerate(sentence_words)])
                    formatted_transcription += f'"{sentence_frame_numbers[j]}": "{tagged_sentence}",\n'

        return formatted_transcription

    def generate_images(self,frame_text_dict,input_images, kwargs):
        images = []
        prepared_images = self.prepare_image(input_images, kwargs)
        
        transcription_mode = kwargs['transcription']['transcription_mode']
        animation_easing = kwargs['animation_settings']['animation_easing']
        animation_reset = kwargs['animation_settings']['animation_reset']
        animation_duration = kwargs['animation_settings']['animation_duration']
        
        start_rotation = kwargs['main_font']['start_rotation']
        end_rotation = kwargs['main_font']['end_rotation']
        start_y_offset = kwargs['main_font']['start_y_offset']
        end_y_offset = kwargs['main_font']['end_y_offset']
        start_x_offset = kwargs['main_font']['start_x_offset']
        end_x_offset = kwargs['main_font']['end_x_offset']
        start_font_size = kwargs['main_font']['start_font_size']
        end_font_size = kwargs['main_font']['end_font_size']
        end_font_size = kwargs['main_font']['end_font_size']

        main_font_file = kwargs['main_font']['font_file']
        highlight_font_file = kwargs['highlight_font']['font_file']

        #implement start and end for highlight font here!!!!
        highlight_font_size = kwargs['highlight_font']['start_font_size']

        frame_count = kwargs['animation_settings']['frame_count']

        # Initialize variables
        last_text = ""
        animation_started_frame = 1
        last_text_length = 0  
        is_animation_active = True
        first_pass = True

        # Ensure prepared_images is a list
        if not isinstance(prepared_images, list):
            prepared_images = [prepared_images]

        def linear_ease(current_frame, total_frames):
            return current_frame / total_frames

        def exponential_ease(current_frame, total_frames):
            return (2**(10 * (current_frame / total_frames - 1)) - 0.001) if current_frame > 0 else 0

        def quadratic_ease_in(current_frame, total_frames):
            t = current_frame / total_frames
            return t * t

        def cubic_ease_in(current_frame, total_frames):
            t = current_frame / total_frames
            return t * t * t

        def elastic_ease_in(current_frame, total_frames):
            t = current_frame / total_frames
            if t == 0 or t == 1:
                return t
            p = 0.3
            s = p / 4
            return -(2**(10 * (t - 1)) * math.sin((t - 1 - s) * (2 * math.pi) / p))

        def bounce_ease_out(current_frame, total_frames):
            t = current_frame / total_frames
            if t < (1 / 2.75):
                return 7.5625 * t * t
            elif t < (2 / 2.75):
                t -= (1.5 / 2.75)
                return 7.5625 * t * t + 0.75
            elif t < (2.5 / 2.75):
                t -= (2.25 / 2.75)
                return 7.5625 * t * t + 0.9375
            else:
                t -= (2.625 / 2.75)
                return 7.5625 * t * t + 0.984375

        def back_ease_in(current_frame, total_frames):
            t = current_frame / total_frames
            s = 1.70158
            return t * t * ((s + 1) * t - s)

        def ease_in_out_sine(current_frame, total_frames):
            return -(math.cos(math.pi * current_frame / total_frames) - 1) / 2

        def ease_out_back(current_frame, total_frames):
            c1 = 1.70158
            c3 = c1 + 1
            t = current_frame / total_frames - 1
            return 1 + c3 * math.pow(t, 3) + c1 * math.pow(t, 2)

        def ease_in_out_expo(current_frame, total_frames):
            if current_frame == 0:
                return 0
            if current_frame == total_frames:
                return 1
            if current_frame < total_frames / 2:
                return math.pow(2, 10 * (current_frame / total_frames - 0.5)) / 2
            return (2 - math.pow(2, -10 * (current_frame / total_frames - 0.5))) / 2

        # Easing function selection
        if animation_easing == 'linear':
            ease_function = linear_ease
        elif animation_easing == 'exponential':
            ease_function = exponential_ease
        elif animation_easing == 'quadratic':
            ease_function = quadratic_ease_in
        elif animation_easing == 'cubic':
            ease_function = cubic_ease_in
        elif animation_easing == 'elastic':
            ease_function = elastic_ease_in
        elif animation_easing == 'bounce':
            ease_function = bounce_ease_out
        elif animation_easing == 'back':
            ease_function = back_ease_in
        elif animation_easing == 'ease_in_out_sine':
            ease_function = ease_in_out_sine
        elif animation_easing == 'ease_out_back':
            ease_function = ease_out_back
        elif animation_easing == 'ease_in_out_expo':
            ease_function = ease_in_out_expo

        for i in range(1, frame_count + 1):
            text = frame_text_dict.get(str(i), "")
            current_text_length = len(text.split())

            if text != last_text:
                if transcription_mode == 'line':
                    clean_current_text = re.sub(r"<tag>|</tag>", "", text)
                    clean_last_text = re.sub(r"<tag>|</tag>", "", last_text)

                if animation_reset == 'word':
                    animation_started_frame = i

                if animation_reset == 'line':
                    if transcription_mode == 'fill':
                        if current_text_length < last_text_length or first_pass == True:
                            animation_started_frame = i
                            first_pass = False

                    if transcription_mode == 'line': 
                        if clean_current_text != clean_last_text or first_pass == True:
                            animation_started_frame = i
                            first_pass = False

                    last_text_length = current_text_length

                last_text = text

            if animation_reset == 'never':
                is_animation_active = True
                # Reset animation if the length of the current text is less than the length of the previous text

            is_animation_active = (i - animation_started_frame) < animation_duration

            # Timed animation logic
            if is_animation_active:
                # Use easing function for animations
                animation_progress = ease_function(i - animation_started_frame, animation_duration)

                rotation = start_rotation + (end_rotation - start_rotation) * animation_progress
                current_font_size = int(start_font_size + (end_font_size - start_font_size) * animation_progress)
                x_offset = start_x_offset + (end_x_offset - start_x_offset) * animation_progress
                y_offset = start_y_offset + (end_y_offset - start_y_offset) * animation_progress
            else:
                # Maintain end values after animation
                current_font_size = end_font_size
                x_offset = end_x_offset
                y_offset = end_y_offset
                rotation = end_rotation

            # Common processing for both animation modes
            font = self.get_font(main_font_file, current_font_size)
            image_index = min(i - 1, len(prepared_images) - 1)
            selected_image = prepared_images[image_index]

            font_tagged = self.get_font(highlight_font_file,highlight_font_size)


            draw = ImageDraw.Draw(selected_image)
            text_width, text_height = self.calculate_text_block_size(draw, text, font_tagged, kwargs)
            text_position = self.calculate_text_position(text_width, text_height, x_offset, y_offset, kwargs)

            processed_image = self.process_single_image(selected_image, text, font, rotation, x_offset, y_offset, text_position, kwargs)
            images.append(processed_image)

        return images
    
    def separate_text(self, text):
        tag_start = "<tag>"
        tag_end = "</tag>"
        tagged_parts = []
        non_tagged_parts = []
        while text:
            start_index = text.find(tag_start)
            end_index = text.find(tag_end)
            if start_index != -1 and end_index != -1:
                non_tagged_parts.append(text[:start_index])
                tagged_parts.append(text[start_index + len(tag_start):end_index])
                text = text[end_index + len(tag_end):]
            else:
                non_tagged_parts.append(text)
                break
        return ' '.join(non_tagged_parts), ' '.join(tagged_parts)  
      
    def process_single_image(self, image, text, font, rotation_angle, x_offset, y_offset, text_position,kwargs ):
        
        rotation_anchor_x = kwargs['main_font']['rotation_anchor_x']
        rotation_anchor_y = kwargs['main_font']['rotation_anchor_y']
        border_width = kwargs['main_font']['border_width']
        shadow_offset_x = kwargs['main_font']['shadow_offset_x']


        orig_width, orig_height = image.size
        # Create a larger canvas with the prepared image as the background
        canvas_size = int(max(orig_width, orig_height) * 1.5)
        canvas = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))

        # Calculate text size and position
        draw = ImageDraw.Draw(canvas)
        text_block_width, text_block_height = self.calculate_text_block_size(draw, text, font, kwargs)
        text_x, text_y = text_position
        text_x += (canvas_size - orig_width) / 2 + x_offset
        text_y += (canvas_size - orig_height) / 2 + y_offset

        # Calculate the center of the text block
        text_center_x = text_x + text_block_width / 2
        text_center_y = text_y + text_block_height / 2

        overlay = Image.new('RGBA', (int(text_block_width + border_width * 2 + shadow_offset_x), int(text_block_height + border_width * 2 + shadow_offset_x)), (255, 255, 255, 0))
        draw_overlay = ImageDraw.Draw(overlay)

        # Draw text on overlays
        self.draw_text_on_overlay(draw_overlay, text, font, kwargs)
        canvas.paste(overlay, (int(text_x), int(text_y)), overlay)
        
        anchor = (text_center_x + rotation_anchor_x, text_center_y + rotation_anchor_y)

        rotated_canvas = canvas.rotate(rotation_angle, center=anchor, expand=0)

        # Create a new canvas to fill the background of the rotated image
        new_canvas = Image.new('RGBA', rotated_canvas.size, (0, 0, 0, 0))

        # Paste the input image as the background of the new canvas
        new_canvas.paste(image, (int((rotated_canvas.size[0] - orig_width) / 2), int((rotated_canvas.size[1] - orig_height) / 2)))

        # Paste the rotated image onto the new canvas, keeping the background color
        new_canvas.paste(rotated_canvas, (0, 0), rotated_canvas)

        # Crop the canvas back to the original image dimensions
        cropped_image = new_canvas.crop(((canvas_size - orig_width) / 2, (canvas_size - orig_height) / 2, (canvas_size + orig_width) / 2, (canvas_size + orig_height) / 2))

        return self.process_image_for_output(cropped_image)

    def draw_text_on_overlay(self, draw_overlay, text, font, kwargs):

        tagged_border_width = kwargs['highlight_font']['border_width']
        tagged_border_color = kwargs['highlight_font']['border_color']
        tagged_shadow_offset_x = kwargs['highlight_font']['shadow_offset_x']
        tagged_shadow_offset_y = kwargs['highlight_font']['shadow_offset_y']
        tagged_shadow_color = kwargs['highlight_font']['shadow_color']
        
        # this has to be addresses!!!
        tagged_font_size = kwargs['highlight_font']['start_font_size']
        
        tagged_font_color = kwargs['highlight_font']['font_color']
        main_border_width = kwargs['main_font']['border_width']
        main_border_color = kwargs['main_font']['border_color']
        main_shadow_offset_x = kwargs['main_font']['shadow_offset_x']
        main_shadow_offset_y = kwargs['main_font']['shadow_offset_y']
        main_shadow_color = kwargs['main_font']['shadow_color']

        # this has to be addresses!!!
        main_font_size = kwargs['main_font']['start_font_size']
        
        main_font_color = kwargs['main_font']['font_color']
        main_font_kerning = kwargs['main_font']['kerning']
        main_font_line_spacing = kwargs['main_font']['line_spacing']


        #border_color = kwargs['highlight_settings']
        #shadow_offset_x = kwargs['highlight_settings']
        #shadow_offset_y = kwargs['highlight_settings']
        #shadow_color = kwargs['highlight_settings']

        y_text_overlay = 0
        x_text_overlay = main_border_width

        tag_start = "<tag>"
        tag_end = "</tag>"

        is_inside_tag = False
        current_font = font

        for line in text.split('\n'):
            while line:
                if line.startswith(tag_start):
                    line = line[len(tag_start):]
                    is_inside_tag = True
                    current_font = ImageFont.truetype(font.path, tagged_font_size)
                    continue

                if line.startswith(tag_end):
                    line = line[len(tag_end):]
                    is_inside_tag = False
                    current_font = font
                    continue

                char = line[0]
                line = line[1:]

                # Adjust vertical position for tagged text
                if is_inside_tag:
                    ascent, descent = current_font.getmetrics()
                    font_offset = (font.getmetrics()[0] - ascent) + (descent - current_font.getmetrics()[1])
                else:
                    font_offset = 0

                if is_inside_tag:
                    border_width = tagged_border_width
                    border_color = tagged_border_color
                    shadow_offset_x = tagged_shadow_offset_x
                    shadow_offset_y = tagged_shadow_offset_y
                    shadow_color = tagged_shadow_color
                    font_color = tagged_font_color

                else:
                    border_width = main_border_width
                    border_color = main_border_color
                    shadow_offset_x = main_shadow_offset_x
                    shadow_offset_y = main_shadow_offset_y
                    shadow_color = main_shadow_color
                    font_color = main_font_color

                # Draw the shadow
                draw_overlay.text(
                    (x_text_overlay + shadow_offset_x, y_text_overlay + shadow_offset_y + font_offset),
                    char, font=current_font, fill=shadow_color
                )

                # Draw the border/stroke
                for dx in range(-border_width, border_width + 1):
                    for dy in range(-border_width, border_width + 1):
                        if dx == 0 and dy == 0:
                            continue  # Skip the character itself
                        draw_overlay.text(
                            (x_text_overlay + dx, y_text_overlay + dy + font_offset),
                            char, font=current_font, fill=border_color
                        )

                # Draw the character
                draw_overlay.text(
                    (x_text_overlay, y_text_overlay + font_offset),
                    char, font=current_font, fill=font_color
                )

                char_width = draw_overlay.textlength(char, font=current_font)
                x_text_overlay += char_width + main_font_kerning

            # Reset x position and increase y for next line
            x_text_overlay = main_border_width
            y_text_overlay += int(current_font.size) + main_font_line_spacing

        # Consider adding padding for the right border
        draw_overlay.text((x_text_overlay, y_text_overlay), '', font=font, fill=main_border_color)

    def get_text_width(self, text, kwargs):
        end_font_size = kwargs['main_font']['end_font_size']
        main_font_file = kwargs['main_font']['font_file']
        

        # Load the font
        font = self.get_font(main_font_file, end_font_size)
        # Measure the size of the text rendered in the loaded font
        text_width = font.getlength(text)
        return text_width

    def calculate_text_position(self, text_width, text_height, x_offset, y_offset, kwargs):
        text_alignment = kwargs['canvas_settings']['text_alignment'] 
        image_width = kwargs['canvas_settings']['width']
        image_height = kwargs['canvas_settings']['height']
        padding = kwargs['canvas_settings']['padding']

        # Adjust the base position based on text_alignment and margin
        if text_alignment == "left top":
            base_x, base_y = padding, padding
        elif text_alignment == "left center":
            base_x, base_y = padding, padding + (image_height - text_height) // 2
        elif text_alignment == "left bottom":
            base_x, base_y = padding, image_height - text_height - padding
        elif text_alignment == "center top":
            base_x, base_y = (image_width - text_width) // 2, padding
        elif text_alignment == "center center":
            base_x, base_y = (image_width - text_width) // 2, (image_height - text_height) // 2
        elif text_alignment == "center bottom":
            base_x, base_y = (image_width - text_width) // 2, image_height - text_height - padding
        elif text_alignment == "right top":
            base_x, base_y = image_width - text_width - padding, padding
        elif text_alignment == "right center":
            base_x, base_y = image_width - text_width - padding, (image_height - text_height) // 2
        elif text_alignment == "right bottom":
            base_x, base_y = image_width - text_width - padding, image_height - text_height - padding
        else:  # Default to center center
            base_x, base_y = (image_width - text_width) // 2, (image_height - text_height) // 2

        # Apply offsets
        final_x = base_x + x_offset
        final_y = base_y + y_offset

        return final_x, final_y

    def process_image_for_output(self, image) -> torch.Tensor:
        i = ImageOps.exif_transpose(image)
        if i.mode == 'I':
            i = i.point(lambda i: i * (1 / 255))
        image = i.convert("RGB")
        image_np = np.array(image).astype(np.float32) / 255.0
        return torch.from_numpy(image_np)[None,]

    def calculate_text_block_size(self, draw, text, font, kwargs):
        lines = text.split('\n')
        max_width = 0
        font_height = font.getbbox('Agy')[3] # Height of a single line

        line_spacing = kwargs['main_font']['line_spacing']

        for line in lines:
            line_width = draw.textlength(line, font=font)  # Get the width of the line
            max_width = max(max_width, line_width)

        total_height = font_height * len(lines) + line_spacing * (len(lines) - 1)

        return max_width, total_height

    def parse_text_input(self, text, kwargs):
        structured_format = False
        frame_text_dict = {}
        frame_count = kwargs['animation_settings']['frame_count']

        # Filter out empty lines
        lines = [line for line in text.split('\n') if line.strip()]

        # Check if the input is in the structured format
        if all(':' in line and line.split(':')[0].strip().replace('"', '').isdigit() for line in lines):
            structured_format = True
            for line in lines:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    frame_number = parts[0].strip().replace('"', '')
                    text = parts[1].strip().replace('"', '').replace(',', '')
                    frame_text_dict[frame_number] = text
        else:
            # If not in structured format, use the input text for all frames
            frame_text_dict = {str(i): text for i in range(1, frame_count + 1)}

        return frame_text_dict, structured_format

    def cumulative_text(self, frame_text_dict, frame_count):
        cumulative_text_dict = {}
        last_text = ""

        for i in range(1, frame_count + 1):
            if str(i) in frame_text_dict:
                last_text = frame_text_dict[str(i)]
            cumulative_text_dict[str(i)] = last_text

        return cumulative_text_dict

    def prepare_image(self, input_image, kwargs):

        image_width = kwargs['canvas_settings']['width']
        image_height = kwargs['canvas_settings']['height']
        padding = kwargs['canvas_settings']['padding']
        background_color = kwargs['canvas_settings']['background_color'] 


        if not isinstance(input_image, list):
            if isinstance(input_image, torch.Tensor):
                if input_image.dtype == torch.float:
                    input_image = (input_image * 255).byte()

                if input_image.ndim == 4:
                    processed_images = []
                    for img in input_image:
                        tensor_image = img.permute(2, 0, 1)
                        transform = transforms.ToPILImage()

                        try:
                            pil_image = transform(tensor_image)
                        except Exception as e:
                            print("Error during conversion:", e)
                            raise

                        if float(PIL.__version__.split('.')[0]) < 10:
                            processed_images.append(pil_image.resize((image_width, image_height), Image.ANTIALIAS))
                        else:
                            processed_images.append(pil_image.resize((image_width, image_height), Image.LANCZOS))
                    return processed_images
                elif input_image.ndim == 3 and input_image.shape[0] in [3, 4]:
                    tensor_image = input_image.permute(1, 2, 0)
                    pil_image = transforms.ToPILImage()(tensor_image)

                    if float(PIL.__version__.split('.')[0]) < 10:
                        return pil_image.resize((image_width, image_height), Image.ANTIALIAS)
                    else:
                        return pil_image.resize((image_width, image_height), Image.LANCZOS)
                else:
                    raise ValueError(f"Input image tensor has an invalid shape or number of channels: {input_image.shape}")
            else:
                return input_image.resize((image_width, image_height), Image.ANTIALIAS)
        else:
            background_color_tuple = ImageColor.getrgb(background_color)
            return Image.new('RGB', (image_width, image_height), color=background_color_tuple)
