import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageColor
import PIL
import numpy as np
import torch
from torchvision import transforms
import random
import math
from matplotlib import font_manager

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
        alignment_options = ["left top", "left center", "left bottom",
                             "center top", "center center", "center bottom",
                             "right top", "right center", "right bottom"]
        text_interpolation_options = ["strict","interpolation","cumulative"]
        transcription_mode = ["word","line","fill"]
        animation_reset = ["word", "line", "never"]
        animation_easing = ["linear", "exponential", "quadratic","cubic", "elastic", "bounce","back","ease_in_out_sine","ease_out_back","ease_in_out_expo"]
        self.FONTS = self.combined_font_list()
        self.FONT_NAMES = sorted(self.FONTS.keys())

        return {
            "required": {
                # "font_file": (font_files, {"default": font_files[0] if font_files else "default", "display": "dropdown"}),
                "font_file": (self.FONT_NAMES, {"default": self.FONT_NAMES[0]}),
                "font_color": ("STRING", {"default": "white", "display": "text"}),
                "background_color": ("STRING", {"default": "black", "display": "text"}),
                "border_color": ("STRING", {"default": "grey", "display": "text"}),
                "border_width": ("INT", {"default": 0, "min": 0, "step": 1, "display": "number"}),
                "shadow_color": ("STRING", {"default": "grey", "display": "text"}),
                "shadow_offset_x": ("INT", {"default": 0, "min": 0, "step": 1, "display": "number"}),
                "shadow_offset_y": ("INT", {"default": 0, "min": 0, "step": 1, "display": "number"}),
                "line_spacing": ("INT", {"default": 5, "step": 1, "display": "number"}),
                "kerning": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "padding": ("INT", {"default": 0, "min": 0, "step": 1, "display": "number"}),
                "frame_count": ("INT", {"default": 1, "min": 1, "max": 10000, "step": 1}),
                "image_height": ("INT", {"default": 512, "step": 1, "display": "number"}),
                "image_width": ("INT", {"default": 512, "step": 1, "display": "number"}),
                "rotation_anchor_x": ("INT", {"default": 0, "step": 1}),
                "rotation_anchor_y": ("INT", {"default": 0, "step": 1}),
                "transcription_mode": (transcription_mode, {"default": "fill", "display": "dropdown"}),
                "text_alignment": (alignment_options, {"default": "center center", "display": "dropdown"}),
                "text_interpolation_options": (text_interpolation_options, {"default": "cumulative", "display": "dropdown"}),
                "text": ("STRING", {"multiline": True, "placeholder": "Text"}),
                "animation_reset": (animation_reset, {"default": "word", "display": "dropdown"}),
                "animation_easing": (animation_easing, {"default": "linear", "display": "dropdown"}),
                "animation_duration": ("INT", {"default": 10, "min": 1, "step": 1, "display": "number"}),
                "start_font_size": ("INT", {"default": 75, "min": 1, "step": 1, "display": "number"}),
                "end_font_size": ("INT", {"default": 75, "min": 1, "step": 1, "display": "number"}),
                "start_x_offset": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "end_x_offset": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "start_y_offset": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "end_y_offset": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "start_rotation": ("INT", {"default": 0, "min": -360, "max": 360, "step": 1}),
                "end_rotation": ("INT", {"default": 0, "min": -360, "max": 360, "step": 1}),
            },
            "optional": {
                "images": ("IMAGE", {"default": None}),
                "transcription": ("TRANSCRIPTION", {"default": None,"forceInput": True})
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("images", "framestamps_string",)

    FUNCTION = "run"

    CATEGORY = "Mana Nodes"

    def run(self, **kwargs):
        if kwargs.get('transcription', None) != None:
            formatted_transcription = self.format_transcription(kwargs)
            text = formatted_transcription
        else:
            formatted_transcription = None
            text = kwargs.get('text')

        frame_text_dict, is_structured_input = self.parse_text_input(text, kwargs)
        frame_text_dict = self.process_text_mode(frame_text_dict, kwargs['text_interpolation_options'], is_structured_input, kwargs['frame_count'])

        images = self.generate_images(frame_text_dict, kwargs.get('images', [None] * kwargs['frame_count']), kwargs)
        image_batch = torch.cat(images, dim=0)

        return (image_batch, formatted_transcription,)

    # maybe make this line per line instead of all at once in the beginning
    # this way the dynamicaly changing font-size could be used in this method for more accurate formatting
    def format_transcription(self, kwargs):
        if not kwargs['transcription']:
            return ""

        # Extract fps from the first element and then discard it from further processing
        _, _, _, transcription_fps = kwargs['transcription'][0]

        formatted_transcription = ""
        current_sentence = ""
        first_transcribed_frame_number = None

        for i, (word, start_time, _, _) in enumerate(kwargs['transcription']):
            frame_number = round(start_time * transcription_fps)

            if not current_sentence:
                current_sentence = word
                if kwargs['transcription_mode'] == "line":
                    first_transcribed_frame_number = frame_number
            else:
                new_sentence = current_sentence + " " + word
                width = self.get_text_width(new_sentence, kwargs)
                if width <= kwargs['image_width'] - kwargs['padding']:
                    current_sentence = new_sentence
                else:
                    if kwargs['transcription_mode'] == "line":
                        formatted_transcription += f'"{first_transcribed_frame_number}": "{current_sentence}",\n'
                        first_transcribed_frame_number = frame_number
                    current_sentence = word

            if kwargs['transcription_mode'] == "fill":
                formatted_transcription += f'"{frame_number}": "{current_sentence}",\n'

            if kwargs['transcription_mode'] == "word":
                formatted_transcription += f'"{frame_number}": "{word}",\n'

        # Add the final sentence for 'line' and 'fill' modes
        if current_sentence:
            if kwargs['transcription_mode'] in ["fill"]:
                last_frame_number = round(kwargs['transcription'][-1][1] * transcription_fps)
                formatted_transcription += f'"{last_frame_number}": "{current_sentence}",\n'
            if kwargs['transcription_mode'] in ["line"]:
                formatted_transcription += f'"{first_transcribed_frame_number}": "{current_sentence}",\n'

        return formatted_transcription

    def generate_images(self,frame_text_dict,input_images, kwargs):
        images = []
        prepared_images = self.prepare_image(input_images, kwargs)

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
        if kwargs['animation_easing'] == 'linear':
            ease_function = linear_ease
        elif kwargs['animation_easing'] == 'exponential':
            ease_function = exponential_ease
        elif kwargs['animation_easing'] == 'quadratic':
            ease_function = quadratic_ease_in
        elif kwargs['animation_easing'] == 'cubic':
            ease_function = cubic_ease_in
        elif kwargs['animation_easing'] == 'elastic':
            ease_function = elastic_ease_in
        elif kwargs['animation_easing'] == 'bounce':
            ease_function = bounce_ease_out
        elif kwargs['animation_easing'] == 'back':
            ease_function = back_ease_in
        elif kwargs['animation_easing'] == 'ease_in_out_sine':
            ease_function = ease_in_out_sine
        elif kwargs['animation_easing'] == 'ease_out_back':
            ease_function = ease_out_back
        elif kwargs['animation_easing'] == 'ease_in_out_expo':
            ease_function = ease_in_out_expo

        for i in range(1, kwargs['frame_count'] + 1):
            text = frame_text_dict.get(str(i), "")
            current_text_length = len(text.split())

            if text != last_text:
                last_text = text

                if kwargs['animation_reset'] == 'word':
                    animation_started_frame = i

                if kwargs['animation_reset'] == 'line':
                    if current_text_length < last_text_length or first_pass == True or kwargs['transcription_mode'] == 'line':
                        animation_started_frame = i
                        first_pass = False
                    last_text_length = current_text_length

            if kwargs['animation_reset'] == 'never':
                is_animation_active = True
                # Reset animation if the length of the current text is less than the length of the previous text

            is_animation_active = (i - animation_started_frame) < kwargs['animation_duration']

            # Timed animation logic
            if is_animation_active:
                # Use easing function for animations
                animation_progress = ease_function(i - animation_started_frame, kwargs['animation_duration'])

                rotation = kwargs['start_rotation'] + (kwargs['end_rotation'] - kwargs['start_rotation']) * animation_progress
                current_font_size = int(kwargs['start_font_size'] + (kwargs['end_font_size'] - kwargs['start_font_size']) * animation_progress)
                x_offset = kwargs['start_x_offset'] + (kwargs['end_x_offset'] - kwargs['start_x_offset']) * animation_progress
                y_offset = kwargs['start_y_offset'] + (kwargs['end_y_offset'] - kwargs['start_y_offset']) * animation_progress
            else:
                # Maintain end values after animation
                current_font_size = kwargs['end_font_size']
                x_offset = kwargs['end_x_offset']
                y_offset = kwargs['end_y_offset']
                rotation = kwargs['end_rotation']

            # Common processing for both animation modes
            font = self.get_font(kwargs['font_file'], current_font_size)
            image_index = min(i - 1, len(prepared_images) - 1)
            selected_image = prepared_images[image_index]

            draw = ImageDraw.Draw(selected_image)
            text_width, text_height = self.calculate_text_block_size(draw, text, font, kwargs)
            text_position = self.calculate_text_position(text_width, text_height, x_offset, y_offset, kwargs)

            processed_image = self.process_single_image(selected_image, text, font, rotation, x_offset, y_offset, text_position, kwargs)
            images.append(processed_image)

        return images

    def process_single_image(self, image, text, font, rotation_angle, x_offset, y_offset, text_position,kwargs ):
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

        overlay = Image.new('RGBA', (int(text_block_width + kwargs['border_width'] * 2 + kwargs['shadow_offset_x']), int(text_block_height + kwargs['border_width'] * 2 + kwargs['shadow_offset_y'])), (255, 255, 255, 0))
        draw_overlay = ImageDraw.Draw(overlay)

        # Draw text on overlays
        self.draw_text_on_overlay(draw_overlay, text, font, kwargs)
        canvas.paste(overlay, (int(text_x), int(text_y)), overlay)
        anchor = (text_center_x + kwargs['rotation_anchor_x'], text_center_y + kwargs['rotation_anchor_y'])

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
        y_text_overlay = 0
        x_text_overlay = kwargs['border_width'] 

        for line in text.split('\n'):
            for char in line:
                # Draw the shadow
                draw_overlay.text(
                    (x_text_overlay + kwargs['shadow_offset_x'], y_text_overlay + kwargs['shadow_offset_y']),
                    char, font=font, fill=kwargs['shadow_color']
                )

                # Draw the border/stroke
                for dx in range(-kwargs['border_width'], kwargs['border_width'] + 1):
                    for dy in range(-kwargs['border_width'], kwargs['border_width'] + 1):
                        if dx == 0 and dy == 0:
                            continue  # Skip the character itself
                        draw_overlay.text(
                            (x_text_overlay + dx, y_text_overlay + dy),
                            char, font=font, fill=kwargs['border_color']
                        )

                # Draw the character
                draw_overlay.text(
                    (x_text_overlay, y_text_overlay),
                    char, font=font, fill=kwargs['font_color']
                )

                char_width = draw_overlay.textlength(char, font=font)
                x_text_overlay += char_width + kwargs['kerning']

            # Reset x position and increase y for next line, account for the border width
            x_text_overlay = kwargs['border_width']
            y_text_overlay += int(font.size) + kwargs['line_spacing']

        # Consider adding padding for the right border
        draw_overlay.text((x_text_overlay, y_text_overlay), '', font=font, fill=kwargs['border_color'])

    def get_text_width(self, text, kwargs):
        # Load the font
        font = self.get_font(kwargs['font_file'], kwargs['end_font_size'])
        # Measure the size of the text rendered in the loaded font
        text_width = font.getlength(text)
        return text_width

    def calculate_text_position(self, text_width, text_height, x_offset, y_offset, kwargs):
        # Adjust the base position based on text_alignment and margin
        if kwargs['text_alignment'] == "left top":
            base_x, base_y = kwargs['padding'], kwargs['padding']
        elif kwargs['text_alignment'] == "left center":
            base_x, base_y = kwargs['padding'], kwargs['padding'] + (kwargs['image_height'] - text_height) // 2
        elif kwargs['text_alignment'] == "left bottom":
            base_x, base_y = kwargs['padding'], kwargs['image_height'] - text_height - kwargs['padding']
        elif kwargs['text_alignment'] == "center top":
            base_x, base_y = (kwargs['image_width'] - text_width) // 2, kwargs['padding']
        elif kwargs['text_alignment'] == "center center":
            base_x, base_y = (kwargs['image_width'] - text_width) // 2, (kwargs['image_height'] - text_height) // 2
        elif kwargs['text_alignment'] == "center bottom":
            base_x, base_y = (kwargs['image_width'] - text_width) // 2, kwargs['image_height'] - text_height - kwargs['padding']
        elif kwargs['text_alignment'] == "right top":
            base_x, base_y = kwargs['image_width'] - text_width - kwargs['padding'], kwargs['padding']
        elif kwargs['text_alignment'] == "right center":
            base_x, base_y = kwargs['image_width'] - text_width - kwargs['padding'], (kwargs['image_height'] - text_height) // 2
        elif kwargs['text_alignment'] == "right bottom":
            base_x, base_y = kwargs['image_width'] - text_width - kwargs['padding'], kwargs['image_height'] - text_height - kwargs['padding']
        else:  # Default to center center
            base_x, base_y = (kwargs['image_width'] - text_width) // 2, (kwargs['image_height'] - text_height) // 2

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

        for line in lines:
            line_width = draw.textlength(line, font=font)  # Get the width of the line
            max_width = max(max_width, line_width)

        total_height = font_height * len(lines) + kwargs['line_spacing'] * (len(lines) - 1)

        return max_width, total_height

    def parse_text_input(self, text, kwargs):
        structured_format = False
        frame_text_dict = {}

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
            frame_text_dict = {str(i): text for i in range(1, kwargs['frame_count'] + 1)}

        return frame_text_dict, structured_format

    def interpolate_text(self, frame_text_dict, frame_count):
        sorted_frames = sorted(int(k) for k in frame_text_dict.keys())

        # If only one frame is specified, use its text for all frames
        if len(sorted_frames) == 1:
            single_frame_text = frame_text_dict[str(sorted_frames[0])]
            return {str(i): single_frame_text for i in range(1, frame_count + 1)}

        # Ensure the last frame is included
        sorted_frames.append(frame_count)

        interpolated_text_dict = {}
        for i in range(len(sorted_frames) - 1):
            start_frame, end_frame = sorted_frames[i], sorted_frames[i + 1]
            start_text = frame_text_dict[str(start_frame)]
            end_text = frame_text_dict.get(str(end_frame), start_text)

            for frame in range(start_frame, end_frame):
                interpolated_text_dict[str(frame)] = self.calculate_interpolated_text(start_text, end_text, frame - start_frame, end_frame - start_frame)

        last_frame_text = frame_text_dict.get(str(frame_count), end_text)
        interpolated_text_dict[str(frame_count)] = last_frame_text

        return interpolated_text_dict

    def calculate_interpolated_text(self, start_text, end_text, frame_delta, total_frames):
        # Determine the number of characters to interpolate
        start_len = len(start_text)
        end_len = len(end_text)
        interpolated_len = int(start_len + (end_len - start_len) * frame_delta / total_frames)

        # Interpolate content
        interpolated_text = ""
        for i in range(interpolated_len):
            if i < start_len and i < end_len:
                # Mix characters from start_text and end_text
                start_char_fraction = 1 - frame_delta / total_frames
                end_char_fraction = frame_delta / total_frames
                interpolated_char = self.interpolate_char(start_text[i], end_text[i], start_char_fraction, end_char_fraction)
                interpolated_text += interpolated_char
            elif i < end_len:
                # If beyond start_text, use end_text characters
                interpolated_text += end_text[i]
            else:
                # If beyond both, use a space or a default character
                interpolated_text += " "  # or some default character

        return interpolated_text

    def interpolate_char(self, start_char, end_char, start_fraction, end_fraction):
        # Simple character interpolation (can be replaced with a more complex logic if needed)
        if random.random() < start_fraction:
            return start_char
        else:
            return end_char

    def cumulative_text(self, frame_text_dict, frame_count):
        cumulative_text_dict = {}
        last_text = ""

        for i in range(1, frame_count + 1):
            if str(i) in frame_text_dict:
                last_text = frame_text_dict[str(i)]
            cumulative_text_dict[str(i)] = last_text

        return cumulative_text_dict

    def process_text_mode(self, frame_text_dict, mode, is_structured_input, frame_count):
        if mode == "interpolation" and is_structured_input:
            return self.interpolate_text(frame_text_dict, frame_count)
        elif mode == "cumulative" and is_structured_input:
            return self.cumulative_text(frame_text_dict, frame_count)
        return frame_text_dict

    def prepare_image(self, input_image, kwargs):
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
                            processed_images.append(pil_image.resize((kwargs['image_width'], kwargs['image_height']), Image.ANTIALIAS))
                        else:
                            processed_images.append(pil_image.resize((kwargs['image_width'], kwargs['image_height']), Image.LANCZOS))
                    return processed_images
                elif input_image.ndim == 3 and input_image.shape[0] in [3, 4]:
                    tensor_image = input_image.permute(1, 2, 0)
                    pil_image = transforms.ToPILImage()(tensor_image)

                    if float(PIL.__version__.split('.')[0]) < 10:
                        return pil_image.resize((kwargs['image_width'], kwargs['image_height']), Image.ANTIALIAS)
                    else:
                        return pil_image.resize((kwargs['image_width'], kwargs['image_height']), Image.LANCZOS)
                else:
                    raise ValueError(f"Input image tensor has an invalid shape or number of channels: {input_image.shape}")
            else:
                return input_image.resize((kwargs['image_width'], kwargs['image_height']), Image.ANTIALIAS)
        else:
            background_color_tuple = ImageColor.getrgb(kwargs['background_color'])
            return Image.new('RGB', (kwargs['image_width'], kwargs['image_height']), color=background_color_tuple)
