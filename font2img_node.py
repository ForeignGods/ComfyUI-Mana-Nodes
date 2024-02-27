import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
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
                "frame_count": ("INT", {"default": 1, "min": 1, "max": 1000, "step": 1}),
                "image_width": ("INT", {"default": 100, "step": 1, "display": "number"}),
                "image_height": ("INT", {"default": 100, "step": 1, "display": "number"}),
                "invert_mask": ("BOOLEAN", {"default": False}),
                "text": ("STRING", {"multiline": True, "placeholder": "Text"}),
                "text_interpolation_options": (text_interpolation_options, {"default": "strict", "display": "dropdown"}),
                "start_font_size": ("INT", {"default": 20, "min": 1, "max": 300, "step": 1, "display": "number"}),
                "end_font_size": ("INT", {"default": 20, "min": 1, "max": 300, "step": 1, "display": "number"}),
                "start_x_offset": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "end_x_offset": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "start_y_offset": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "end_y_offset": ("INT", {"default": 0, "step": 1, "display": "number"}),
                "start_rotation": ("INT", {"default": 0, "min": -360, "max": 360, "step": 1}),
                "end_rotation": ("INT", {"default": 0, "min": -360, "max": 360, "step": 1})        
            },
            "optional": {
                "input_images": ("IMAGE", {"default": None, "display": "image_upload"})
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("images","masks")

    FUNCTION = "run"

    CATEGORY = "font2img"

    def run(self, invert_mask, end_font_size, start_font_size, text_interpolation_options, line_spacing, start_x_offset, end_x_offset, start_y_offset, end_y_offset, start_rotation, end_rotation, font_file, frame_count, text, font_color, background_color, image_width, image_height, text_alignment, **kwargs):
        frame_text_dict, is_structured_input = self.parse_text_input(text, frame_count)
        frame_text_dict = self.process_text_mode(frame_text_dict, text_interpolation_options, is_structured_input, frame_count)

        rotation_increment = (end_rotation - start_rotation) / max(frame_count - 1, 1)
        x_offset_increment = (end_x_offset - start_x_offset) / max(frame_count - 1, 1)
        y_offset_increment = (end_y_offset - start_y_offset) / max(frame_count - 1, 1)
        font_size_increment = (end_font_size - start_font_size) / max(frame_count - 1, 1)

        input_images = kwargs.get('input_image', [None] * frame_count)

        images, masks = self.generate_images(start_font_size, font_size_increment, frame_text_dict, rotation_increment, x_offset_increment, y_offset_increment, font_file, font_color, background_color, image_width, image_height, text_alignment, line_spacing, frame_count, input_images)

        # Invert masks if needed
        if invert_mask:
            masks = [1.0 - mask for mask in masks]

        masks = [torch.from_numpy(mask).unsqueeze(0) for mask in masks]

        image_batch = torch.cat(images, dim=0)
        mask_batch = torch.cat(masks, dim=0)

        return (image_batch, mask_batch,)
    
    def generate_mask(self, image_width, image_height, text_position, text_size):
        mask = np.zeros((image_height, image_width))
        # Example: draw a simple rectangle where the text would be
        x, y = text_position
        mask[y:y+text_size[1], x:x+text_size[0]] = 1
        return mask

    def calculate_text_position(self, image_width, image_height, text_width, text_height, text_alignment):
        # Calculate text position based on text_alignment
        if text_alignment == "left top":
            return 0, 0
        elif text_alignment == "left center":
            return 0, (image_height - text_height) // 2
        elif text_alignment == "left bottom":
            return 0, image_height - text_height
        elif text_alignment == "center top":
            return (image_width - text_width) // 2, 0
        elif text_alignment == "center center":
            return (image_width - text_width) // 2, (image_height - text_height) // 2
        elif text_alignment == "center bottom":
            return (image_width - text_width) // 2, image_height - text_height
        elif text_alignment == "right top":
            return image_width - text_width, 0
        elif text_alignment == "right center":
            return image_width - text_width, (image_height - text_height) // 2
        elif text_alignment == "right bottom":
            return image_width - text_width, image_height - text_height
        # Default to center center
        return (image_width - text_width) // 2, (image_height - text_height) // 2
    
    def process_image_for_output(self, image):
        i = ImageOps.exif_transpose(image)
        if i.mode == 'I':
            i = i.point(lambda i: i * (1 / 255))
        image = i.convert("RGB")
        image_np = np.array(image).astype(np.float32) / 255.0
        return torch.from_numpy(image_np)[None,]
    
    def prepare_image(self, input_image, image_width, image_height, background_color):
        if input_image is not None:
            # Normalize if necessary (assuming the values are in range [0, 1])
            if input_image.dtype == torch.float:
                input_image = (input_image * 255).byte()

            # Remove the batch dimension
            tensor_image = input_image.squeeze(0)

            # Permute the dimensions to match PIL format
            tensor_image = tensor_image.permute(2, 0, 1)

            # Convert to PIL Image
            transform = transforms.ToPILImage()
            try:
                pil_image = transform(tensor_image)
            except Exception as e:
                print("Error during conversion:", e)
                raise

            # Resize image if necessary
            return pil_image.resize((image_width, image_height))
        else:
            # Create a new image with specified dimensions and background color
            return Image.new('RGB', (image_width, image_height), color=background_color)
    
    def get_font(self, font_file, font_size, script_dir):
        if font_file == "default":
            return ImageFont.load_default()
        else:
            full_font_file = os.path.join(script_dir, 'font', font_file)
            return ImageFont.truetype(full_font_file, font_size)
        
    def calculate_text_block_size(self, draw, text, font, line_spacing):
        lines = text.split('\n')

        # Initialize the maximum width and total height of the text block
        max_width = 0
        total_height = 0

        for line in lines:
            # Get width and height of each line
            line_width, line_height = draw.textsize(line, font=font)

            # Update the maximum width if this line is wider
            max_width = max(max_width, line_width)

            # Add the height of this line to the total height
            total_height += line_height

            # Add line spacing after each line except the last one
            if line != lines[-1]:
                total_height += line_spacing

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
    
    def generate_images(self, start_font_size, font_size_increment, frame_text_dict, rotation_increment, x_offset_increment, y_offset_increment, font_file, font_color, background_color, image_width, image_height, text_alignment, line_spacing, frame_count, input_images):
        images = []
        masks = []

        for i in range(1, frame_count + 1):
            text = frame_text_dict.get(str(i), "")
            current_font_size = int(start_font_size + font_size_increment * (i - 1))
            font = self.get_font(font_file, current_font_size, os.path.dirname(__file__))
            
            # Prepare image and draw text
            image = self.prepare_image(None, image_width, image_height, background_color)  # Assuming no input images for simplicity
            draw = ImageDraw.Draw(image)
            text_width, text_height = self.calculate_text_block_size(draw, text, font, line_spacing)
            text_position = self.calculate_text_position(image_width, image_height, text_width, text_height, text_alignment)
            
            # Process image and generate mask
            processed_image, mask = self.process_single_image(image, text, font, font_color, rotation_increment * i, x_offset_increment * i, y_offset_increment * i, text_alignment, line_spacing, image_width, image_height)            
            images.append(processed_image)
            masks.append(mask)

        return images, masks

    def process_single_image(self, image, text, font, font_color, rotation_angle, x_offset, y_offset, text_alignment, line_spacing, image_width, image_height):        
        draw = ImageDraw.Draw(image)
        text_block_width, text_block_height = self.calculate_text_block_size(draw, text, font, line_spacing)
        
        # Create an overlay for text drawing and a mask
        overlay = Image.new('RGBA', (text_block_width, text_block_height), (255, 255, 255, 0))
        mask = Image.new('L', (text_block_width, text_block_height), 0)  # L mode for mask
        draw_overlay = ImageDraw.Draw(overlay)
        draw_mask = ImageDraw.Draw(mask)

        # Draw text on overlay and mask
        self.draw_text_on_overlay(draw_overlay, draw_mask, text, font, font_color, line_spacing)
        
        # Rotate overlay and mask
        rotated_overlay = overlay.rotate(rotation_angle, expand=1)
        rotated_mask = mask.rotate(rotation_angle, expand=1)

        # Calculate position
        base_text_x, base_text_y = self.calculate_text_position(image_width, image_height, text_block_width, text_block_height, text_alignment)
        text_x = base_text_x + x_offset + (text_block_width - rotated_overlay.width) // 2
        text_y = base_text_y + y_offset + (text_block_height - rotated_overlay.height) // 2

        # Paste overlay and mask onto the main image
        image.paste(rotated_overlay, (int(text_x), int(text_y)), rotated_overlay)
        final_mask = Image.new('L', (image_width, image_height), 0)
        final_mask.paste(rotated_mask, (int(text_x), int(text_y)), rotated_mask)

        return self.process_image_for_output(image), np.array(final_mask)

    
    def draw_text_on_overlay(self, draw_overlay, draw_mask, text, font, font_color, line_spacing):
        y_text_overlay = 0
        for line in text.split('\n'):
            line_width, line_height = draw_overlay.textsize(line, font=font)
            draw_overlay.text((0, y_text_overlay), line, font=font, fill=font_color)
            draw_mask.text((0, y_text_overlay), line, font=font, fill="white")
            y_text_overlay += line_height + line_spacing