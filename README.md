# ComfyUI-Mana-Nodes
Collection of custom nodes for ComfyUI.

- [Installation](#installation)
- [Nodes](#nodes)
  - [font2img Node](#font2img-node)
    - [Example Workflow](#example-workflow)
    - [Font Licences](#font-licences)
- [Contributing](#contributing)
  
## Installation
Simply clone the repo into the `custom_nodes` directory with this command:

```
git clone https://github.com/ForeignGods/ComfyUI-Mana-Nodes.git
```

and install the requirements using:
```
.\python_embed\python.exe -s -m pip install -r requirements.txt
```

If you are using a venv, make sure you have it activated before installation and use:
```
pip install -r requirements.txt
```

## Nodes

## font2img Node

### Demo

<img src="https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/5a35d2d6-ae15-4ee1-ba81-582975633a93" width="200" height="300" alt="gif_00008-ezgif com-optimize">
<img src="https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/ca8a5636-7d82-4f72-82a7-f21dacfb4d01" width="200" height="300" alt="gif_00008-ezgif com-optimize">
<img src="https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/82e418bb-07d3-47a0-b329-d312c376dab3" width="200" height="300" alt="gif_00008-ezgif com-optimize">
<img src="https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/b45ae2c0-60f7-4a32-87af-80b7a26783ab" width="200" height="300" alt="gif_00008-ezgif com-optimize">

### Required Inputs

Configure the font2img node by setting the following parameters in ComfyUI:

- <b>font_file:</b> fonts located in the <b>custom_nodes\ComfyUI-Mana-Nodes\font\example_font.ttf</b> directory (supports .ttf, .otf, .woff, .woff2).
- <b>font_color:</b> Color of the text. (https://www.w3.org/wiki/CSS3/Color/Extended_color_keywords)
- <b>background_color:</b> Background color of the image.
- <b>text_alignment:</b> Alignment of the text in the image.
- <b>line_spacing:</b> Spacing between lines of text.
- <b>kerning:</b> Spacing between characters of font.
- <b>frame_count:</b> Number of frames (images) to generate.
- <b>image_width:</b> Width of the generated images.
- <b>image_height:</b> Height of the generated images.
- <b>text:</b> The text to render in the images.
- <b>text_interpolation_options:</b> Mode of text interpolation ('strict', 'interpolation', 'cumulative').
- <b>start_font_size, end_font_size:</b> Starting and ending size of the font. 
- <b>start_x_offset, end_x_offset, start_y_offset, end_y_offset:</b> Offsets for text positioning.
- <b>start_rotation, end_rotation:</b> Rotation angles for the text.
- <b>anchor_x, anchor_y:</b> offset of the rotation anchor point, relative to the text.

### Optional Inputs

- <b>input_images:</b> Text will be overlayed on input_images instead of background_color.

### Outputs

- images: The generated images with the specified text and configurations.

### Parameters Explanation

#### `text`
- Specifies the text to be rendered on the images. Supports multiline text input for rendering on separate lines.
  - For simple text: Input the text directly as a string.
  - For frame-specific text (in modes like 'strict' or 'cumulative'): Use a JSON-like format where each line specifies a frame number and the corresponding text. Example:
    ``` 
    "1": "Hello",
    "10": "World",
    "20": "End"
    ```

#### `text_interpolation_options`
- Defines the mode of text interpolation between frames.
  - `strict`: Text is only inserted at specified frames.
  - `interpolation`: Gradually interpolates text characters between frames.
  - `cumulative`: Text set for a frame persists until updated in a subsequent frame.


#### `start_x_offset`, `end_x_offset`, `start_y_offset`, `end_y_offset`
- Sets the starting and ending offsets for text positioning on the X and Y axes, allowing for text transition across the image.
- Input as integers. Example: `start_x_offset = 10`, `end_x_offset = 50` moves the text from 10 pixels from the left to 50 pixels from the left across frames.

#### `start_rotation`, `end_rotation`
- Defines the starting and ending rotation angles for the text, enabling it to rotate between these angles.
- Input as integers in degrees. Example: `start_rotation = 0`, `end_rotation = 180` rotates the text from 0 to 180 degrees across frames.

#### `start_font_size`, `end_font_size`

- Sets the starting and ending font sizes for the text, allowing the text size to dynamically change across frames.
- Input as integers representing the font size in points. Example: `start_font_size = 12`, `end_font_size = 24` will gradually increase the text size from 12 to 24 points across the frames.

### Example Workflow

![workflow](https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/38d91b00-01b5-4ab2-b874-5bf4753cbea3)

### Font Licences
- <b>Personal Use:</b> The included fonts are for personal, non-commercial use. Please refrain from using these fonts in any commercial project without obtaining the appropriate licenses.
- <b>License Compliance:</b> Each font may come with its own license agreement. It is the responsibility of the user to review and comply with these agreements. Some fonts may require a license for commercial use, modification, or distribution.
- <b>Removing Fonts:</b> If any font creator or copyright holder wishes their font to be removed from this repository, please contact us, and we will promptly comply with your request.

## Contributing
Your contributions to improve Mana Nodes are welcome! If you have suggestions or enhancements, feel free to fork this repository, apply your changes, and create a pull request. For significant modifications or feature requests, please open an issue first to discuss what you'd like to change.
