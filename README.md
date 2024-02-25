# ComfyUI-Mana-Nodes
Collection of custom nodes for ComfyUI.

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

## font2img Node

Configure the font2img node by setting the following parameters in ComfyUI:

### Required Inputs
<b>font_file:</b> fonts located in the <b>custom_nodes\ComfyUI-Mana-Nodes\font\example_font.ttf</b> directory (supports .ttf, .otf, .woff, .woff2).
<b>font_size:</b> Size of the font.
<b>font_color:</b> Color of the text. (https://www.w3.org/wiki/CSS3/Color/Extended_color_keywords)
<b>background_color:</b> Background color of the image.
<b>text_alignment:</b> Alignment of the text in the image.
<b>line_spacing:</b> Spacing between lines of text.
<b>frame_count:</b> Number of frames (images) to generate.
<b>image_width:</b> Width of the generated images.
<b>image_height:</b> Height of the generated images.
<b>text:</b> The text to render in the images.
<b>text_interpolation_options:</b> Mode of text interpolation ('strict', 'interpolation', 'cumulative').
<b>start_x_offset, end_x_offset, start_y_offset, end_y_offset:</b> Offsets for text positioning.
<b>start_rotation, end_rotation:</b> Rotation angles for the text.

### Optional Inputs

<b>images:</b> Text will be overlayed on input_images instead of background_color.

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
  - `"strict"`: Text is only inserted at specified frames.
  - `"interpolation"`: Gradually interpolates text characters between frames.
  - `"cumulative"`: Text set for a frame persists until updated in a subsequent frame.


#### `start_x_offset`, `end_x_offset`, `start_y_offset`, `end_y_offset`
- Sets the starting and ending offsets for text positioning on the X and Y axes, allowing for text transition across the image.
- Input as integers. Example: `start_x_offset = 10`, `end_x_offset = 50` moves the text from 10 pixels from the left to 50 pixels from the left across frames.

#### `start_rotation`, `end_rotation`
- Defines the starting and ending rotation angles for the text, enabling it to rotate between these angles.
- Input as integers in degrees. Example: `start_rotation = 0`, `end_rotation = 180` rotates the text from 0 to 180 degrees across frames.

## Contributing
Your contributions to improve Mana Nodes are welcome! If you have suggestions or enhancements, feel free to fork this repository, apply your changes, and create a pull request. For significant modifications or feature requests, please open an issue first to discuss what you'd like to change.