# ComfyUI-Mana-Nodes

Collection of custom nodes for ComfyUI.

- [Installation](#installation)
- [Demo](#demo)
- [To-Do](#to-do)
- [Nodes](#nodes)
  - [font2img Node](#font2img-node)
  - [video2audio Node](#video2audio-node)
  - [speech2text Node](#speech2text-node)
  - [string2file Node](#string2file-node)
  - [audio2video Node](#audio2video-node)
- [Example Workflows](#example-workflows)
  - [Font Animation](#font-animation)
  - [Speech Reconition](#speech-recognition)
- [Font Licences](#font-licences)
  - [Font Links](#font-links)
- [Contributing](#contributing)
  
## Installation
Simply clone the repo into the `custom_nodes` directory with this command:

```
git clone https://github.com/ForeignGods/ComfyUI-Mana-Nodes.git
```

and install the requirements using:
```
.\python_embed\python.exe -s -m pip install -r requirements.txt --user
```

If you are using a venv, make sure you have it activated before installation and use:
```
pip install -r requirements.txt
```

## Demo

<img src="https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/5a35d2d6-ae15-4ee1-ba81-582975633a93" width="200" height="300" alt="gif_00008-ezgif com-optimize">
<img src="https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/ca8a5636-7d82-4f72-82a7-f21dacfb4d01" width="200" height="300" alt="gif_00008-ezgif com-optimize">
<img src="https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/82e418bb-07d3-47a0-b329-d312c376dab3" width="200" height="300" alt="gif_00008-ezgif com-optimize">
<img src="https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/b45ae2c0-60f7-4a32-87af-80b7a26783ab" width="200" height="300" alt="gif_00008-ezgif com-optimize">

https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/657330d9-4745-4acf-b1cc-de9336104f3d

## To-Do

- [x] font2image Batch Animation
- [x] Split Video to Frames and Audio
- [x] speech2text
- [ ] text2speech
- [ ] SVG Loader/Animator
- [ ] font2image Alpha Channel
- [ ] add font support for other languages
- [ ] 3d effect for text, bevel/emboss, inner shading, fade in/out effect
- [ ] input scheduled values for the animation

## Nodes

## font2img Node

### Required Inputs

Configure the font2img node by setting the following parameters in ComfyUI:

- <b>font_file:</b> fonts located in the <b>custom_nodes\ComfyUI-Mana-Nodes\font\example_font.ttf</b> directory (supports .ttf, .otf, .woff, .woff2).
- <b>font_color:</b> Color of the text. (https://www.w3.org/wiki/CSS3/Color/Extended_color_keywords)
- <b>background_color:</b> Background color of the image.
- <b>border_color:</b> Color of the border around the text.
- <b>border_width:</b> Width of the text border.
- <b>shadow_color:</b> Width of the text border.
- <b>shadow_offset_x:</b> Horizontal offset of the shadow.
- <b>shadow_offset_y:</b> Vertical offset of the shadow.
- <b>line_spacing:</b> Spacing between lines of text.
- <b>kerning:</b> Spacing between characters of font.
- <b>padding:</b> Padding between image border and font.
- <b>frame_count:</b> Number of frames (images) to generate.
- <b>image_width:</b> Width of the generated images.
- <b>image_height:</b> Height of the generated images.
- <b>transcription_mode:</b> Mode of text transcription ('word', 'line', 'fill').
- <b>text_alignment:</b> Alignment of the text in the image.
- <b>text_interpolation_options:</b> Mode of text interpolation ('strict', 'interpolation', 'cumulative').
- <b>text:</b> The text to render in the images. (is ignored when optional input transcription is given)
- <b>animation_reset:</b> Defines when the animation resets ('word', 'line', 'never').
- <b>animation_easing:</b> Easing function for animation (e.g., 'linear', 'exponential').
- <b>animation_duration:</b> Duration of the animation.
- <b>start_font_size, end_font_size:</b> Starting and ending size of the font. 
- <b>start_x_offset, end_x_offset, start_y_offset, end_y_offset:</b> Offsets for text positioning.
- <b>start_rotation, end_rotation:</b> Rotation angles for the text.
- <b>rotation_anchor_x, rotation_anchor_y:</b> offset of the rotation anchor point, relative to the texts initial position.

### Optional Inputs

- <b>input_images:</b> Text will be overlayed on input_images instead of background_color.
- <b>transcription:</b> Transcription from the speech2text node, contains dict with timestamps, framerate and transcribed words.

### Outputs

- <b>images:</b> The generated images with the specified text and configurations.
- <b>transcription_framestamps:</b> Outputs a string containing the framestamps, new line calculated based on image width. (Can be useful to manually correct mistakes by speech recognition)
  - <b>Example:</b> Save this output with string2file -> correct mistakes -> remove transcription input from font2img -> paste corrected framestamps into text input field of font2img node.

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


#### `animation_reset`

- Dictates when the animation effect resets to its starting conditions.
  - word: Resets animation with each new word.
  - line: Resets animation at the beginning of each new line of text.
  - never: The animation does not reset, but continues throughout.

#### `animation_easing`

- Controls the pacing of the animation.
  - Examples include linear, exponential, quadratic, cubic, elastic, bounce, back, ease_in_out_sine, ease_out_back, ease_in_out_expo.
  - Each option provides a different acceleration curve for the animation, affecting how the text transitions and rotates.

#### `animation_duration`

- The length of time each animation takes to complete, measured in frames.
- A larger value means a slower, more gradual transition, while a smaller value results in a quicker animation.

#### `transcription_mode`

- Determines how the transcribed text is applied across frames.
  - word: Each word appears on its corresponding frame based on the transcription timestamps.
  - line: Similar to word, but text is added line by line.
  - fill: Continuously fills the frame with text, adding new words at their specific timestamps.

## video2audio Node

Extracts frames and audio from a video file.

### Required Inputs

- <b>video:</b> Path the video file.
- <b>frame_limit:</b> Maximum number of frames to extract from the video.
- <b>frame_start:</b> Starting frame number for extraction.
- <b>filename_prefix:</b> Prefix for naming the extracted audio file. (relative to .\ComfyUI-Mana-Nodes)

### Outputs

- <b>frames:</b> Extracted frames as image tensors.
- <b>frame_count:</b> Total number of frames extracted.
- <b>audio:</b> Path of the extracted audio file.
- <b>fps:</b> Frames per second of the video.
- <b>height, width:</b> Dimensions of the extracted frames.

## speech2text Node

Converts spoken words in an audio file to text using a deep learning model.

### Required Inputs

- <b>audio:</b> Audio file path or URL.
- <b>wav2vec2_model:</b> The Wav2Vec2 model used for speech recognition. (https://huggingface.co/models?search=wav2vec2)
- <b>spell_check_language:</b> Language for the spell checker.
- <b>framestamps_max_chars:</b> Maximum characters allowed until new framestamp lines created.

### Optional Inputs

- <b>fps:</b> Frames per second, used for synchronizing with video. (Default set to 30)

### Outputs

- <b>transcription:</b> Text transcription of the audio. (Should only be used as font2img transcription input)
- <b>raw_string:</b> Raw string of the transcription without timestamps.
- <b>framestamps_string:</b> Frame-stamped transcription.
- <b>timestamps_string:</b> Transcription with timestamps.

### Example Outputs

- <b>raw_string:</b> Returns the transcribed text as one line.

```
THE GREATEST TRICK THE DEVIL EVER PULLED WAS CONVINCING THE WORLD HE DIDN'T EXIST
```

- <b>framestamps_string:</b> Depending on the <b>framestamps_max_chars</b> parameter the sentece will be cleared and starts to build up again until max_chars is reached again. 
  - In this example <b>framestamps_max_chars</b> is set to <b>25</b>.

```
"27": "THE",
"31": "THE GREATEST",
"43": "THE GREATEST TRICK",
"73": "THE GREATEST TRICK THE",
"77": "DEVIL",
"88": "DEVIL EVER",
"94": "DEVIL EVER PULLED",
"127": "DEVIL EVER PULLED WAS",
"133": "CONVINCING",
"150": "CONVINCING THE",
"154": "CONVINCING THE WORLD",
"167": "CONVINCING THE WORLD HE",
"171": "DIDN'T",
"178": "DIDN'T EXIST",
```

<b>timestamps_string:</b> Returns all transcribed words, their start_time and end_time in json format as a string.

```
[
  {
    "word": "THE",
    "start_time": 0.9,
    "end_time": 0.98
  },
  {
    "word": "GREATEST",
    "start_time": 1.04,
    "end_time": 1.36
  },
  {
    "word": "TRICK",
    "start_time": 1.44,
    "end_time": 1.68
  },
  {
    "word": "THE",
    "start_time": 2.42,
    "end_time": 2.5
  },
  {
    "word": "DEVIL",
    "start_time": 2.58,
    "end_time": 2.82
  },
  {
    "word": "EVER",
    "start_time": 2.92,
    "end_time": 3.04
  },
  {
    "word": "PULLED",
    "start_time": 3.14,
    "end_time": 3.44
  },
  {
    "word": "WAS",
    "start_time": 4.22,
    "end_time": 4.34
  },
  {
    "word": "CONVINCING",
    "start_time": 4.44,
    "end_time": 4.92
  },
  {
    "word": "THE",
    "start_time": 5.0,
    "end_time": 5.06
  },
  {
    "word": "WORLD",
    "start_time": 5.12,
    "end_time": 5.42
  },
  {
    "word": "HE",
    "start_time": 5.58,
    "end_time": 5.62
  },
  {
    "word": "DIDN'T",
    "start_time": 5.7,
    "end_time": 5.88
  },
  {
    "word": "EXIST",
    "start_time": 5.94,
    "end_time": 6.28
  }
]
```

## string2file Node

Writes a given string to a text file.

### Required Inputs

- <b>string:</b> The string to be written to the file.
- <b>filename_prefix:</b> Prefix for naming the text file. (relative to .\ComfyUI-Mana-Nodes)

## audio2video Node

Combines a sequence of images (frames) with an audio file to create a video.

### Required Inputs

- <b>audio:</b> Audio file path or URL.
- <b>frames:</b> Sequence of images to be used as video frames.
- <b>filename_prefix:</b> Prefix for naming the video file. (relative to .\ComfyUI-Mana-Nodes)
- <b>fps:</b> Frames per second for the video.

### Outputs

- <b>video_file_path:</b> Path to the created video file.

## Example Workflows

### Font Animation 

These workflows are included in the example_workflows directory: 

#### example_workflow_1.json 

![Screenshot 2024-03-05 at 15-54-43 ComfyUI](https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/91c8c306-761e-4fa9-a9a8-c0c0e3cc3c96)

#### example_workflow_2.json 

![Screenshot 2024-03-14 at 15-24-36 ComfyUI](https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/8caba06f-e24e-4096-96a4-21a91fdb6c5b)

### Speech Recognition 

## Font Licences
- <b>Personal Use:</b> The included fonts are for personal, non-commercial use. Please refrain from using these fonts in any commercial project without obtaining the appropriate licenses.
- <b>License Compliance:</b> Each font may come with its own license agreement. It is the responsibility of the user to review and comply with these agreements. Some fonts may require a license for commercial use, modification, or distribution.
- <b>Removing Fonts:</b> If any font creator or copyright holder wishes their font to be removed from this repository, please contact us, and we will promptly comply with your request.

### Font Links
- https://www.dafont.com/akira-expanded.font
- https://www.dafont.com/aurora-pro.font
- https://www.dafont.com/another-danger.font
- https://www.dafont.com/doctor-glitch.font
- https://www.dafont.com/ghastly-panic.font
- https://www.dafont.com/metal-gothic.font
- https://www.dafont.com/the-constellation.font
- https://www.dafont.com/the-augusta.font
- https://www.dafont.com/vogue.font
- https://www.dafont.com/wreckside.font

## Contributing
<a href="https://www.buymeacoffee.com/foreigngods" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

Your contributions to improve Mana Nodes are welcome! If you have suggestions or enhancements, feel free to fork this repository, apply your changes, and create a pull request. For significant modifications or feature requests, please open an issue first to discuss what you'd like to change.

