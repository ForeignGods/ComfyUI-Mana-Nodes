import math
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageSequence

import numpy as np
import torch
from torchvision import transforms

class font2img:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        alignment_options = ["left top", "left center", "left bottom", 
                             "center top", "center center", "center bottom", 
                             "right top", "right center", "right bottom"]
        script_dir = os.path.dirname(__file__)
        print(script_dir)
        font_dir = os.path.join(script_dir, 'font')
        font_files = [f for f in os.listdir(font_dir) if os.path.isfile(os.path.join(font_dir, f)) and (f.endswith('.ttf') or f.endswith('.otf') or f.endswith('.woff') or f.endswith('.woff2'))]
        return {
            "required": {
                "font_path": (font_files, {"default": font_files[0] if font_files else "default", "display": "dropdown"}),
                "text": ("STRING", {"display": "text"}),
                "font_size": ("INT", {"default": 20, "step": 1, "display": "number"}),
                "color": ("STRING", {"default": "black", "display": "text"}),
                "image_width": ("INT", {"default": 100, "step": 1, "display": "number"}),
                "image_height": ("INT", {"default": 100, "step": 1, "display": "number"}),
                "alignment": (alignment_options, {"default": "center center", "display": "dropdown"})
            },
            "optional": {
                "input_image": ("IMAGE", {"default": None, "display": "image_upload"})
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    FUNCTION = "run"

    CATEGORY = "font2img"

    def run(self, font_path, text, font_size, color, image_width, image_height,alignment, **kwargs):
        script_dir = os.path.dirname(__file__)
        print(script_dir)
        input_image = kwargs.get('input_image', None)
        if font_path == "default":
            font = ImageFont.load_default()
        else:
            font_path = os.path.join(script_dir,'font', font_path)
            font = ImageFont.truetype(font_path, font_size)

        # Process the input image or create a new one
        if input_image is not None:
            # Normalize if necessary (assuming the values are in range [0, 1])
            if input_image.dtype == torch.float:
                input_image = (input_image * 255).byte()

            # Remove the batch dimension
            tensor_image = input_image.squeeze(0)

            # Debugging information
            print("Tensor shape:", tensor_image.shape)
            print("Tensor type:", tensor_image.dtype)
            print("Tensor values sample:", tensor_image[0, 0, :])

            tensor_image = tensor_image.permute(2, 0, 1)

            # Convert to PIL Image
            transform = transforms.ToPILImage()
            try:
                pil_image = transform(tensor_image)
            except Exception as e:
                print("Error during conversion:", e)
                raise

            # Resize image if necessary
            image = pil_image.resize((image_width, image_height))

        else:
            # Create a new image
            image = Image.new('RGB', (image_width, image_height), color=(255, 255, 255))

        draw = ImageDraw.Draw(image)
        text_width, text_height = draw.textsize(text, font=font)
        
        text_x = (image.width - text_width) // 2
        text_y = (image.height - text_height) // 2
        
        # Determine text position based on alignment
        if alignment == "left top":
            text_x, text_y = 0, 0
        elif alignment == "left center":
            text_x, text_y = 0, (image_height - text_height) // 2
        elif alignment == "left bottom":
            text_x, text_y = 0, image_height - text_height
        elif alignment == "center top":
            text_x, text_y = (image_width - text_width) // 2, 0
        elif alignment == "center center":
            text_x, text_y = (image_width - text_width) // 2, (image_height - text_height) // 2
        elif alignment == "center bottom":
            text_x, text_y = (image_width - text_width) // 2, image_height - text_height
        elif alignment == "right top":
            text_x, text_y = image_width - text_width, 0
        elif alignment == "right center":
            text_x, text_y = image_width - text_width, (image_height - text_height) // 2
        elif alignment == "right bottom":
            text_x, text_y = image_width - text_width, image_height - text_height
        draw.text((text_x, text_y), text, fill=color, font=font)

        # Process the image similarly to ImageSequence.Iterator in LoadImage
        i = ImageOps.exif_transpose(image)
        if i.mode == 'I':
            i = i.point(lambda i: i * (1 / 255))
        image = i.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]

        return (image,)

