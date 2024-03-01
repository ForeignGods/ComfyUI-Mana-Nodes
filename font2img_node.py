import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageColor, ImageChops
import numpy as np
import torch
from torchvision import transforms
import random

class font2img:

    def __init__(self):
        pass
    
    def get_font_files(self,font_dir):
        extensions = ['.ttf', '.otf', '.woff', '.woff2']
        return [f for f in os.listdir(font_dir) 
                if os.path.isfile(os.path.join(font_dir, f)) and f.endswith(tuple(extensions))]

    @classmethod
    def INPUT_TYPES(self):

        script_dir = os.path.dirname(__file__)
        font_dir = os.path.join(script_dir, 'font')
        font_files = self.get_font_files(self,font_dir)

        alignment_options = ["left top", "left center", "left bottom", 
                             "center top", "center center", "center bottom", 
                             "right top", "right center", "right bottom"]
        text_interpolation_options = ["strict","interpolation","cumulative"]

        return {
            "required": {
                "font_file": (font_files, {"default": font_files[0] if font_files else "default", "display": "dropdown"}),
                "font_color": ("STRING", {"default": "white", "display": "text"}),
                "background_color": ("STRING", {"default": "black", "display": "text"}),
                "text_alignment": (alignment_options, {"default": "center center", "display": "dropdown"}),
                "line_spacing": ("INT", {"default": 5, "step": 1, "display": "number"}),
                "kerning": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "frame_count": ("INT", {"default": 1, "min": 1, "max": 1000, "step": 1}),
                "image_width": ("INT", {"default": 100, "step": 1, "display": "number"}),
                "image_height": ("INT", {"default": 100, "step": 1, "display": "number"}),
                "text": ("STRING", {"multiline": True, "placeholder": "Text"}),
                "text_interpolation_options": (text_interpolation_options, {"default": "strict", "display": "dropdown"}),
                "start_font_size": ("INT", {"default": 20, "min": 1, "step": 1, "display": "number"}),
                "end_font_size": ("INT", {"default": 20, "min": 1, "step": 1, "display": "number"}),
                "start_x_offset": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "end_x_offset": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "start_y_offset": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "end_y_offset": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "rotate_around_center": ("BOOLEAN", {"default": True}),
                "anchor_x": ("INT", {"default": 0, "step": 1}),
                "anchor_y": ("INT", {"default": 0, "step": 1}),
                "start_rotation": ("INT", {"default": 0, "min": -360, "max": 360, "step": 1}),
                "end_rotation": ("INT", {"default": 0, "min": -360, "max": 360, "step": 1})        
            },
            "optional": {
                "input_images": ("IMAGE", {"default": None, "display": "input_images"})
            }
        }

    RETURN_TYPES = ("IMAGE", )
    RETURN_NAMES = ("images",)

    FUNCTION = "run"

    CATEGORY = "Mana Nodes"

    def run(self, end_font_size, start_font_size, text_interpolation_options, line_spacing, start_x_offset, end_x_offset, start_y_offset, end_y_offset, start_rotation, end_rotation, font_file, frame_count, text, font_color, background_color, image_width, image_height, text_alignment, anchor_x, anchor_y, rotate_around_center,kerning, **kwargs):
        frame_text_dict, is_structured_input = self.parse_text_input(text, frame_count)
        frame_text_dict = self.process_text_mode(frame_text_dict, text_interpolation_options, is_structured_input, frame_count)

        rotation_increment = (end_rotation - start_rotation) / max(frame_count - 1, 1)
        x_offset_increment = (end_x_offset - start_x_offset) / max(frame_count - 1, 1)
        y_offset_increment = (end_y_offset - start_y_offset) / max(frame_count - 1, 1)
        font_size_increment = (end_font_size - start_font_size) / max(frame_count - 1, 1)

        input_images = kwargs.get('input_images', [None] * frame_count)
        images= self.generate_images(start_font_size, font_size_increment, frame_text_dict, rotation_increment, x_offset_increment, y_offset_increment, start_x_offset, end_x_offset, start_y_offset, end_y_offset, font_file, font_color, background_color, image_width, image_height, text_alignment, line_spacing, frame_count, input_images, anchor_x, anchor_y, rotate_around_center, kerning)

        image_batch = torch.cat(images, dim=0)

        return (image_batch,)

    def calculate_text_position(self, image_width, image_height, text_width, text_height, text_alignment, x_offset, y_offset):        # Calculate base position based on text_alignment
        if text_alignment == "left top":
            base_x, base_y = 0, 0
        elif text_alignment == "left center":
            base_x, base_y = 0, (image_height - text_height) // 2
        elif text_alignment == "left bottom":
            base_x, base_y = 0, image_height - text_height
        elif text_alignment == "center top":
            base_x, base_y = (image_width - text_width) // 2, 0
        elif text_alignment == "center center":
            base_x, base_y = (image_width - text_width) // 2, (image_height - text_height) // 2
        elif text_alignment == "center bottom":
            base_x, base_y = (image_width - text_width) // 2, image_height - text_height
        elif text_alignment == "right top":
            base_x, base_y = image_width - text_width, 0
        elif text_alignment == "right center":
            base_x, base_y = image_width - text_width, (image_height - text_height) // 2
        elif text_alignment == "right bottom":
            base_x, base_y = image_width - text_width, image_height - text_height
        else:  # Default to center center
            base_x, base_y = (image_width - text_width) // 2, (image_height - text_height) // 2

        # Apply offsets
        final_x = base_x + x_offset
        final_y = base_y + y_offset

        return final_x, final_y

    def process_image_for_output(self, image):
        i = ImageOps.exif_transpose(image)
        if i.mode == 'I':
            i = i.point(lambda i: i * (1 / 255))
        image = i.convert("RGB")
        image_np = np.array(image).astype(np.float32) / 255.0
        return torch.from_numpy(image_np)[None,]
    
    def get_font(self, font_file, font_size, script_dir):
        if font_file == "default":
            return ImageFont.load_default()
        else:
            full_font_file = os.path.join(script_dir, 'font', font_file)
            return ImageFont.truetype(full_font_file, font_size)
        
    def calculate_text_block_size(self, draw, text, font, line_spacing, kerning):
        lines = text.split('\n')
        max_width = 0
        font_size = int(font.size)  # Assuming PIL's ImageFont object with a size attribute

        for line in lines:
            line_width = sum(draw.textlength(char, font=font) + kerning for char in line)
            line_width -= kerning  # Remove the last kerning value as it's not needed after the last character
            max_width = max(max_width, line_width)

        total_height = font_size * len(lines) + line_spacing * (len(lines) - 1)

        return max_width, total_height
    
    def parse_text_input(self, text_input, frame_count):
        structured_format = False
        frame_text_dict = {}

        # Filter out empty lines
        lines = [line for line in text_input.split('\n') if line.strip()]

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
            frame_text_dict = {str(i): text_input for i in range(1, frame_count + 1)}

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
    
    def prepare_image(self, input_image, image_width, image_height, background_color):
        if not isinstance(input_image, list):
            # Check if the input image is a tensor
            if isinstance(input_image, torch.Tensor):
                # Normalize tensor if necessary
                if input_image.dtype == torch.float:
                    input_image = (input_image * 255).byte()

                # Handle different tensor shapes
                if input_image.ndim == 4:
                    # Batch of images: [Batch, Channels, Height, Width]
                    processed_images = []
                    for img in input_image:
                        # Remove the batch dimension
                        #tensor_image = input_image.squeeze(0)
                        # Permute the dimensions to match PIL format
                        tensor_image = img.permute(2, 0, 1)
                            # Convert to PIL Image
                        transform = transforms.ToPILImage()

                        try:
                            pil_image = transform(tensor_image)
                        except Exception as e:
                            print("Error during conversion:", e)
                            raise

                        processed_images.append(pil_image.resize((image_width, image_height), Image.ANTIALIAS))
                    return processed_images
                elif input_image.ndim == 3 and input_image.shape[0] in [3, 4]:
                    # Single image: [Channels, Height, Width]
                    tensor_image = input_image.permute(1, 2, 0)  # Permute to [Height, Width, Channels]
                    pil_image = transforms.ToPILImage()(tensor_image)
                    return pil_image.resize((image_width, image_height), Image.ANTIALIAS)
                else:
                    raise ValueError(f"Input image tensor has an invalid shape or number of channels: {input_image.shape}")
            else:
                # Assume input_image is already a PIL Image
                return input_image.resize((image_width, image_height), Image.ANTIALIAS)
        else:
            # Create a new image with specified dimensions and background color
            background_color_tuple = ImageColor.getrgb(background_color)
            return Image.new('RGB', (image_width, image_height), color=background_color_tuple)

    def generate_images(self, start_font_size, font_size_increment, frame_text_dict, rotation_increment, x_offset_increment, y_offset_increment, start_x_offset, end_x_offset, start_y_offset, end_y_offset, font_file, font_color, background_color, image_width, image_height, text_alignment, line_spacing, frame_count, input_images, anchor_x, anchor_y, rotate_around_center, kerning):        
        images = []
        prepared_images = self.prepare_image(input_images, image_width, image_height, background_color)

        # Ensure prepared_images is a list, even for a single image
        if not isinstance(prepared_images, list):
            prepared_images = [prepared_images]

        for i in range(1, frame_count + 1):
            text = frame_text_dict.get(str(i), "")
            current_font_size = int(start_font_size + font_size_increment * (i - 1))
            font = self.get_font(font_file, current_font_size, os.path.dirname(__file__))

            # Select image from prepared_images or the last image if index exceeds the list
            image_index = min(i - 1, len(prepared_images) - 1)
            selected_image = prepared_images[image_index]

            draw = ImageDraw.Draw(selected_image)
            text_width, text_height = self.calculate_text_block_size(draw, text, font, line_spacing, kerning)

            x_offset = start_x_offset + x_offset_increment * (i - 1)
            y_offset = start_y_offset + y_offset_increment * (i - 1)

            text_position = self.calculate_text_position(image_width, image_height, text_width, text_height, text_alignment, x_offset, y_offset)

            processed_image= self.process_single_image(selected_image, text, font, font_color, rotation_increment * i, x_offset, y_offset, text_alignment, line_spacing, text_position, anchor_x, anchor_y, rotate_around_center, background_color, kerning)

            images.append(processed_image)

        return images
    
    def process_single_image(self, image, text, font, font_color, rotation_angle, x_offset, y_offset, text_alignment, line_spacing, text_position, anchor_x, anchor_y, rotate_around_center, background_color, kerning):        
        orig_width, orig_height = image.size
        # Create a larger canvas with the prepared image as the background
        canvas_size = int(max(orig_width, orig_height) * 1.5)
        canvas = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))

        # Calculate text size and position
        draw = ImageDraw.Draw(canvas)
        text_block_width, text_block_height = self.calculate_text_block_size(draw, text, font, line_spacing, kerning)
        text_x, text_y = text_position
        text_x += (canvas_size - orig_width) / 2 + x_offset
        text_y += (canvas_size - orig_height) / 2 + y_offset

        # Calculate the center of the text block
        text_center_x = text_x + text_block_width / 2
        text_center_y = text_y + text_block_height / 2

        overlay = Image.new('RGBA', (int(text_block_width), int(text_block_height)), (255, 255, 255, 0))
        draw_overlay = ImageDraw.Draw(overlay)

        # Draw text on overlays
        self.draw_text_on_overlay(draw_overlay, text, font, font_color, line_spacing, kerning)

        # Paste overlays onto the canvas
        canvas.paste(overlay, (int(text_x), int(text_y)), overlay)


        # Determine anchor point for rotation
        anchor = (text_center_x, text_center_y) if rotate_around_center else (text_center_x + anchor_x, text_center_y + anchor_y)

        # Rotate canvas 
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

    def draw_text_on_overlay(self, draw_overlay, text, font, font_color, line_spacing, kerning):
        y_text_overlay = 0
        x_text_overlay = 0
        for line in text.split('\n'):
            for char in line:
                draw_overlay.text((x_text_overlay, y_text_overlay), char, font=font, fill=font_color)

                char_width = draw_overlay.textlength(char, font=font)

                x_text_overlay += char_width + kerning

            x_text_overlay = 0
            y_text_overlay += int(font.size) + line_spacing