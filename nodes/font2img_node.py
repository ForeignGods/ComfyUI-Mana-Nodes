import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageColor
import PIL
import numpy as np
import torch
from torchvision import transforms
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
        #print('get_font()', font_file, 'font_size:', font_size)
        return ImageFont.truetype(font_file, font_size)

    @classmethod
    def INPUT_TYPES(self):

        self.FONTS = self.combined_font_list()
        self.FONT_NAMES = sorted(self.FONTS.keys())
        return {
            "required": {
                "font": ("TEXT_GRAPHIC_ELEMENT", {"default": None,"forceInput": True}),
                "text": ("STRING", {"multiline": True, "placeholder": "\"1\": \"Hello\",\n\"10\": \"Hello World\""}),
                "canvas": ("CANVAS_SETTINGS", {"default": None,"forceInput": True}),
                "frame_count": ("INT", {"default": 1, "min": 1, "step": 1, "display": "number"}),
            },
            "optional": {
                "transcription": ("TRANSCRIPTION", {"default": None,"forceInput": True}),
                "highlight_font": ("TEXT_GRAPHIC_ELEMENT", {"default": None,"forceInput": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("images", "framestamps_string",)
    FUNCTION = "run"
    CATEGORY = "💠 Mana Nodes"

    def run(self, **kwargs):
        frame_count = kwargs['frame_count']
        images = kwargs.get('canvas', {}).get('images', [None] * frame_count)
        transcription = kwargs.get('transcription', None)
        text = kwargs.get('text')

        if transcription != None:
            formatted_transcription = self.format_transcription(kwargs)
            text = formatted_transcription
        else:
            formatted_transcription = None

        frame_text_dict, is_structured_input = self.parse_text_input(text, kwargs)
        frame_text_dict = self.cumulative_text(frame_text_dict, frame_count)
        
        images = self.generate_images(frame_text_dict,images , kwargs)
        image_batch = torch.cat(images, dim=0)

        return (image_batch, formatted_transcription,)

    def format_transcription(self, kwargs):
        if not kwargs['transcription']:
            return ""
        
        highlight_font = kwargs.get('highlight_font', None)
        transcription_fps = kwargs['transcription']['fps']
        transcription_mode = kwargs['transcription']['transcription_mode']
        transcription_data = kwargs['transcription']['transcription_data']
        image_width = kwargs['canvas']['width']
        padding = kwargs['canvas']['padding']
        formatted_transcription = ""
        current_sentence = ""
        sentence_words = []
        sentence_frame_numbers = []

        for i, (word, start_time, end_time) in enumerate(transcription_data):
            frame_number = round(start_time * transcription_fps)

            if not current_sentence:
                current_sentence = word
                sentence_words = [word]
                sentence_frame_numbers = [frame_number]
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
                            if highlight_font is not None:
                                sentence = ' '.join(["<tag>{}</tag>".format(w) if j == k else w for k, w in enumerate(sentence_words)])
                            else:
                                sentence = ' '.join(sentence_words)
                            formatted_transcription += f'"{sentence_frame_numbers[j]}": "{sentence}",\n'
                        current_sentence = word
                        sentence_words = [word]
                        sentence_frame_numbers = [frame_number]
                    else:
                        current_sentence = word

            if transcription_mode == "fill":
                words = current_sentence.split()
                # Add tags around the last word in the sentence only if highlight_font is not None
                if words and highlight_font is not None:
                    words[-1] = f"<tag>{words[-1]}</tag>"
                tagged_sentence = ' '.join(words)
                formatted_transcription += f'"{frame_number}": "{tagged_sentence}",\n'

            if transcription_mode == "word":
                formatted_transcription += f'"{frame_number}": "{word}",\n'

        # Handle the last sentence for 'line' and 'fill' modes
        if current_sentence:
            if transcription_mode == "line":
                for j, sentence_word in enumerate(sentence_words):
                    if highlight_font is not None:
                        tagged_sentence = ' '.join(["<tag>{}</tag>".format(w) if j == k else w for k, w in enumerate(sentence_words)])
                    else:
                        tagged_sentence = ' '.join(sentence_words)
                    formatted_transcription += f'"{sentence_frame_numbers[j]}": "{tagged_sentence}",\n'

        return formatted_transcription
    
    def parse_animation_duration(self, anim_list):
        """Parse animatable property and return its duration, which is the highest frame number defined."""
        # Expecting a single string in list
        if isinstance(anim_list, list):
            # Find the highest 'x' value in the list, which represents the animation duration
            max_frame = max(item['x'] for item in anim_list)
            return max_frame
        else:
            return 1  # Default duration is 1 if the list is empty
        
    def calculate_pingpong_position(self, current_frame, duration):
        if duration <= 1:
            return 0
        cycle_length = duration * 2 - 2
        position = current_frame % cycle_length
        if position >= duration:
            return cycle_length - position
        return position
    
    def calculate_sequence_frame(self, current_frame, start_frame, duration, reset_mode):
        if reset_mode == 'word' or reset_mode == 'line':
            active = (current_frame - start_frame) < duration
            return (current_frame - start_frame) + 1 if active else duration 
        elif reset_mode == 'never':
            return current_frame + 1 if current_frame <= duration else duration 
        elif reset_mode == 'looped':
            return (current_frame % duration) + 1
        elif reset_mode == 'pingpong':
            return self.calculate_pingpong_position(current_frame, duration) 
        return 1  
    
    # Helper functions
    def animation_reset(self, animation_reset_mode, new_text, old_text, transcription_mode):
        if animation_reset_mode == 'word':
            return new_text.split() != old_text.split()
        elif animation_reset_mode == 'line':
            new_text = self.remove_tags(new_text)
            old_text = self.remove_tags(old_text)
            if transcription_mode == 'line':
                return new_text != old_text
            if transcription_mode == 'fill':
                return len(new_text.split()) < len(old_text.split())
        return False
    
    def remove_tags(self, text):
        # Regex to find <tag> and </tag>
        cleaned_text = re.sub(r"</?tag>", "", text)
        return cleaned_text

    def generate_images(self, frame_text_dict, input_images, kwargs):
        images = []
        
        # background images or color
        prepared_images = self.prepare_image(input_images, kwargs)
        
        transcription = kwargs.get('transcription', None)
        if transcription != None:
            transcription_mode = transcription['transcription_mode']
        else:
            transcription_mode = None

        main_font = kwargs.get('font', None)
        if main_font != None:
            main_font_file = main_font['font_file']

        rotation = kwargs['font']['rotation'][0]
        y_offset = kwargs['font']['y_offset'][0]
        x_offset = kwargs['font']['x_offset'][0]
        font_size = kwargs['font']['font_size'][0]
        #print('font_size',font_size)

        font_color = kwargs['font']['font_color'][0]
        border_color = kwargs['font']['border_color'][0]
        shadow_color = kwargs['font']['shadow_color'][0]

        animation_reset_rotation = kwargs['font']['rotation'][1]
        animation_reset_y_offset = kwargs['font']['y_offset'][1]
        animation_reset_x_offset = kwargs['font']['x_offset'][1]
        animation_reset_font_size = kwargs['font']['font_size'][1]
        
        animation_reset_font_color = kwargs['font']['font_color'][1]
        animation_reset_border_color = kwargs['font']['border_color'][1]
        animation_reset_shadow_color = kwargs['font']['shadow_color'][1]

        rotation_duration = self.parse_animation_duration(rotation)
        y_offset_duration = self.parse_animation_duration(y_offset)
        x_offset_duration = self.parse_animation_duration(x_offset)
        font_size_duration = self.parse_animation_duration(font_size)
        #print('font_size_duration',font_size_duration)
        font_color_duration = self.parse_animation_duration(font_color)
        shadow_color_duration = self.parse_animation_duration(shadow_color)
        border_color_duration = self.parse_animation_duration(border_color)

        highlight_font = kwargs.get('highlight_font', None)
        if highlight_font != None:
            tagged_font_file = highlight_font['font_file']

            tagged_font_size = highlight_font['font_size'][0]
            tagged_font_color = highlight_font['font_color'][0]
            tagged_border_color = highlight_font['border_color'][0]
            tagged_shadow_color = highlight_font['shadow_color'][0]

            animation_reset_tagged_font_size = highlight_font['font_size'][1]
            animation_reset_tagged_font_color = highlight_font['font_color'][1]
            animation_reset_tagged_border_color = highlight_font['border_color'][1]
            animation_reset_tagged_shadow_color = highlight_font['shadow_color'][1]

            tagged_font_size_duration = self.parse_animation_duration(tagged_font_size)
            tagged_font_color_duration = self.parse_animation_duration(tagged_font_color)
            tagged_border_color_duration = self.parse_animation_duration(tagged_border_color)
            tagged_shadow_color_duration = self.parse_animation_duration(tagged_shadow_color)

        frame_count = kwargs['frame_count']
        removed_tags_last_text= ''
        last_text = ""
        animation_started_frame_rotation = 1
        animation_started_frame_y_offset = 1
        animation_started_frame_x_offset = 1
        animation_started_frame_font_size = 1

        animation_started_frame_font_color = 1
        animation_started_frame_border_color = 1
        animation_started_frame_shadow_color = 1

        animation_started_frame_tagged_font_size = 1
        animation_started_frame_tagged_font_color = 1
        animation_started_frame_tagged_border_color = 1
        animation_started_frame_tagged_shadow_color = 1

        first_pass = True

        # Ensure prepared_images is a list
        if not isinstance(prepared_images, list):
            prepared_images = [prepared_images]

        for i in range(1, frame_count + 1):
            text = frame_text_dict.get(str(i), "")
            removed_tags_text = self.remove_tags(text)

            if self.animation_reset(animation_reset_rotation, removed_tags_text, removed_tags_last_text, transcription_mode) or first_pass == True:
                animation_started_frame_rotation = i
            if self.animation_reset(animation_reset_y_offset, removed_tags_text, removed_tags_last_text, transcription_mode) or first_pass == True:
                animation_started_frame_y_offset = i
            if self.animation_reset(animation_reset_x_offset, removed_tags_text, removed_tags_last_text, transcription_mode) or first_pass == True:
                animation_started_frame_x_offset = i
            if self.animation_reset(animation_reset_font_size, removed_tags_text, removed_tags_last_text, transcription_mode) or first_pass == True:
                animation_started_frame_font_size = i
            if self.animation_reset(animation_reset_font_color, removed_tags_text, removed_tags_last_text, transcription_mode) or first_pass == True:
                animation_started_frame_font_color = i
            if self.animation_reset(animation_reset_border_color, removed_tags_text, removed_tags_last_text, transcription_mode) or first_pass == True:
                animation_started_frame_border_color = i
            if self.animation_reset(animation_reset_shadow_color, removed_tags_text, removed_tags_last_text, transcription_mode) or first_pass == True:
                animation_started_frame_shadow_color = i

            if highlight_font is not None:
                if self.animation_reset(animation_reset_tagged_font_size, text, last_text, transcription_mode) or first_pass == True:
                    animation_started_frame_tagged_font_size = i
                if self.animation_reset(animation_reset_tagged_font_color, text, last_text, transcription_mode) or first_pass == True:
                    animation_started_frame_tagged_font_color = i
                if self.animation_reset(animation_reset_tagged_border_color, text, last_text, transcription_mode) or first_pass == True:
                    animation_started_frame_tagged_border_color = i
                if self.animation_reset(animation_reset_tagged_shadow_color, text, last_text, transcription_mode) or first_pass == True:
                    animation_started_frame_tagged_shadow_color = i                        

            first_pass = False
            last_text = text
            removed_tags_last_text = removed_tags_text
            #print('animation_started',animation_started_frame_y_offset)

            # Calculate sequence frames for each property
            sequence_frame_rotation = self.calculate_sequence_frame(i, animation_started_frame_rotation, rotation_duration, animation_reset_rotation)
            sequence_frame_y_offset = self.calculate_sequence_frame(i, animation_started_frame_y_offset, y_offset_duration, animation_reset_y_offset)
            sequence_frame_x_offset = self.calculate_sequence_frame(i, animation_started_frame_x_offset, x_offset_duration, animation_reset_x_offset)
            sequence_frame_font_size = self.calculate_sequence_frame(i, animation_started_frame_font_size, font_size_duration, animation_reset_font_size)

            #print('sequence_frame_font_size',sequence_frame_font_size)

            sequence_frame_font_color = self.calculate_sequence_frame(i, animation_started_frame_font_color, font_color_duration, animation_reset_font_color)
            sequence_frame_border_color = self.calculate_sequence_frame(i, animation_started_frame_border_color, border_color_duration, animation_reset_border_color)
            sequence_frame_shadow_color = self.calculate_sequence_frame(i, animation_started_frame_shadow_color, shadow_color_duration, animation_reset_shadow_color)

            if highlight_font is not None:
                sequence_frame_tagged_font_size = self.calculate_sequence_frame(i, animation_started_frame_tagged_font_size, tagged_font_size_duration, animation_reset_tagged_font_size)
                sequence_frame_tagged_font_color = self.calculate_sequence_frame(i, animation_started_frame_tagged_font_color, tagged_font_color_duration, animation_reset_tagged_font_color)
                sequence_frame_tagged_border_color = self.calculate_sequence_frame(i, animation_started_frame_tagged_border_color, tagged_border_color_duration, animation_reset_tagged_border_color)
                sequence_frame_tagged_shadow_color = self.calculate_sequence_frame(i, animation_started_frame_tagged_shadow_color, tagged_shadow_color_duration, animation_reset_tagged_shadow_color)

            current_rotation = self.get_frame_specific_value(sequence_frame_rotation, rotation) if isinstance(rotation, list) else rotation
            current_y_offset = self.get_frame_specific_value(sequence_frame_y_offset, y_offset) if isinstance(y_offset, list) else y_offset
            current_x_offset = self.get_frame_specific_value(sequence_frame_x_offset, x_offset) if isinstance(x_offset, list) else x_offset

            current_font_size = self.get_frame_specific_value(sequence_frame_font_size, font_size) if isinstance(font_size, list) else font_size
            #print('current_font_size:',current_font_size)

            font = self.get_font(main_font_file, current_font_size)

            current_font_color = self.get_frame_specific_value(sequence_frame_font_color, font_color) if isinstance(font_color, list) else font_color
            current_border_color = self.get_frame_specific_value(sequence_frame_border_color, border_color) if isinstance(border_color, list) else border_color
            current_shadow_color = self.get_frame_specific_value(sequence_frame_shadow_color, shadow_color) if isinstance(shadow_color, list) else shadow_color

            if highlight_font is not None:
                current_tagged_font_size = self.get_frame_specific_value(sequence_frame_tagged_font_size, tagged_font_size) if isinstance(tagged_font_size, list) else tagged_font_size
                tagged_font = self.get_font(tagged_font_file, current_tagged_font_size)

                current_tagged_font_color = self.get_frame_specific_value(sequence_frame_tagged_font_color, tagged_font_color) if isinstance(tagged_font_color, list) else tagged_font_color
                current_tagged_border_color = self.get_frame_specific_value(sequence_frame_tagged_border_color, tagged_border_color) if isinstance(tagged_border_color, list) else tagged_border_color
                current_tagged_shadow_color = self.get_frame_specific_value(sequence_frame_tagged_shadow_color, tagged_shadow_color) if isinstance(tagged_shadow_color, list) else tagged_shadow_color
            else:
                tagged_font = font

                current_tagged_font_color = current_font_color
                current_tagged_border_color = current_border_color
                current_tagged_shadow_color = current_shadow_color

            image_index = min(i - 1, len(prepared_images) - 1)
            selected_image = prepared_images[image_index]

            draw = ImageDraw.Draw(selected_image)
            text_block_width, text_block_height = self.calculate_text_block_size(draw, text, font, tagged_font, kwargs)
            text_position = self.calculate_text_position(text_block_width, text_block_height, current_x_offset, current_y_offset, kwargs)
            processed_image = self.process_single_image(selected_image, 
                                                        text, 
                                                        font, 
                                                        current_rotation, 
                                                        current_x_offset, 
                                                        current_y_offset, 
                                                        text_position, 
                                                        tagged_font, 
                                                        current_font_color, 
                                                        current_border_color, 
                                                        current_shadow_color, 
                                                        current_tagged_font_color,
                                                        current_tagged_border_color,
                                                        current_tagged_shadow_color,
                                                        kwargs)
            images.append(processed_image)
        return images
    
    def get_frame_specific_value(self, sequence_frame_number, value_list):
        if isinstance(value_list, list) and value_list:
            value_dict = {item['x']: item['y'] for item in value_list}
            current_value = value_dict.get(sequence_frame_number)

            if current_value is not None:
                return current_value
            else:
                # Find the last defined sequence value before the current sequence frame
                last_defined_frame = max((x for x in value_dict.keys() if x <= sequence_frame_number), default=1)
                return value_dict.get(last_defined_frame, value_list[0]['y'])
        else:
            return value_list
        
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
      
    def process_single_image(self, image, text, font, rotation_angle, x_offset, y_offset, text_position, tagged_font, font_color, border_color, shadow_color, tagged_font_color, tagged_border_color, tagged_shadow_color, kwargs ):
        rotation_anchor_x = kwargs['font']['rotation_anchor_x'][0]
        rotation_anchor_y = kwargs['font']['rotation_anchor_y'][0]
        border_width = kwargs['font']['border_width'][0]
        shadow_offset_x = kwargs['font']['shadow_offset_x'][0]

        # Create a larger canvas with the prepared image as the background
        orig_width, orig_height = image.size
        canvas_size = int(max(orig_width, orig_height) * 1.5)
        canvas = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))

        # Calculate text size and position
        draw = ImageDraw.Draw(canvas)
        text_block_width, text_block_height = self.calculate_text_block_size(draw, text, font, tagged_font, kwargs)
        text_x, text_y = text_position
        text_x += (canvas_size - orig_width) / 2 + x_offset
        text_y += (canvas_size - orig_height) / 2 + y_offset

        # Calculate the center of the text block
        text_center_x = text_x + text_block_width / 2
        text_center_y = text_y + text_block_height / 2

        total_kerning_width = sum(font.getlength(char) + kwargs['font']['kerning'][0] for char in text) - kwargs['font']['kerning'][0] * len(text)

        overlay = Image.new('RGBA', (int(text_block_width + border_width * 2 + shadow_offset_x + total_kerning_width), int(text_block_height + border_width * 2 + shadow_offset_x)), (255, 255, 255, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        # Draw text on overlays
        self.draw_text_on_overlay(draw_overlay, text, font, tagged_font, font_color, border_color, shadow_color, tagged_font_color, tagged_border_color, tagged_shadow_color, kwargs)
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

    def draw_text_on_overlay(self, draw_overlay, text, font, tagged_font, font_color, border_color, shadow_color, tagged_font_color, tagged_border_color, tagged_shadow_color, kwargs):
        highlight_font = kwargs.get('highlight_font', None)
        if highlight_font != None:
            tagged_border_width = highlight_font['border_width'][0]
            tagged_shadow_offset_x = highlight_font['shadow_offset_x'][0]
            tagged_shadow_offset_y = highlight_font['shadow_offset_y'][0]
        else:
            tagged_border_width = 1
            tagged_shadow_offset_x = 0
            tagged_shadow_offset_y = 0

        main_border_width = kwargs['font']['border_width'][0]
        main_border_color = border_color
        main_shadow_offset_x = kwargs['font']['shadow_offset_x'][0]
        main_shadow_offset_y = kwargs['font']['shadow_offset_y'][0]
        main_shadow_color = shadow_color

        main_font_color = font_color
        main_font_kerning = kwargs['font']['kerning'][0]
        line_spacing = kwargs['canvas']['line_spacing']

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
                    current_font = tagged_font
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

                # Draw the shadow, text, and borders
                shadow_x = x_text_overlay + shadow_offset_x
                shadow_y = y_text_overlay + shadow_offset_y + font_offset

                # Draw the shadow
                draw_overlay.text(
                    (x_text_overlay + shadow_offset_x, y_text_overlay + shadow_offset_y + font_offset),
                    char, font=current_font, fill=shadow_color
                )

                draw_overlay.text((shadow_x, shadow_y), char, font=current_font, fill=shadow_color)

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
            y_text_overlay +=  current_font.getbbox('Agy')[3] + line_spacing

        # Consider adding padding for the right border
        draw_overlay.text((x_text_overlay, y_text_overlay), '', font=font, fill=border_color)

    def get_text_width(self, text, kwargs):
        
        main_font = kwargs['font']
        main_font_size = main_font['font_size'][0]
        main_font_file = main_font['font_file']

        if isinstance(main_font_size, (list)):
            main_font_size = max(d['y'] for d in main_font_size)
        else:
            main_font_size = main_font_size

        # Load the font
        font = self.get_font(main_font_file, main_font_size)

        # Measure the size of the text rendered in the loaded font
        text_width = font.getlength(text)
        return text_width

    def calculate_text_position(self, text_width, text_height, x_offset, y_offset, kwargs):
        text_alignment = kwargs['canvas']['text_alignment'] 
        image_width = kwargs['canvas']['width']
        image_height = kwargs['canvas']['height']
        padding = kwargs['canvas']['padding']

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

    def calculate_text_block_size(self, draw, text, font, tagged_font, kwargs):
        lines = text.split('\n')
        max_width = 0
        font_height = font.getbbox('Agy')[3] # Height of a single line
        tagged_font_height = tagged_font.getbbox('Agy')[3]
        line_spacing = kwargs['canvas']['line_spacing']

        for line in lines:
            non_tagged_text, tagged_text = self.separate_text(line)
            line_width = draw.textlength(non_tagged_text, font=font)
            tagged_line_width = draw.textlength(tagged_text, font=tagged_font)

            total_line_width = line_width + tagged_line_width
            max_width = max(max_width, total_line_width)

        total_height = max(font_height, tagged_font_height) * len(lines) + line_spacing * (len(lines) - 1)
        return max_width, total_height

    def parse_text_input(self, text, kwargs):
        structured_format = False
        frame_text_dict = {}
        frame_count = kwargs['frame_count']

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

    # TODO: ugly method has to be refactored
    def prepare_image(self, input_image, kwargs):

        image_width = kwargs['canvas']['width']
        image_height = kwargs['canvas']['height']
        padding = kwargs['canvas']['padding']
        background_color = kwargs['canvas']['background_color'] 

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
            elif input_image != None:
                return input_image.resize((image_width, image_height), Image.ANTIALIAS)
            else:
                background_color_tuple = ImageColor.getrgb(background_color)
                return Image.new('RGB', (image_width, image_height), color=background_color_tuple)
        else:
            background_color_tuple = ImageColor.getrgb(background_color)
            return Image.new('RGB', (image_width, image_height), color=background_color_tuple)