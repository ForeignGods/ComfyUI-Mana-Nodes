# ComfyUI-Mana-Nodes

- [Installation](#installation)
- [Demo](#demo)
- [To-Do](#to-do)
- [Nodes](#nodes)
  - [font2img Node](#font2img-node)
  - [video2audio Node](#video2audio-node)
  - [speech2text Node](#speech2text-node)
  - [text2speech Node](#text2speech-node)
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
- [x] text2speech
- [ ] SVG Loader/Animator
- [ ] font2image Alpha Channel
- [ ] add font support for other languages
- [ ] 3d effect for text, bevel/emboss, inner shading, fade in/out effect
- [ ] input scheduled values for the animation

## Nodes

## font2img Node

### Required Inputs

Configure the font2img node by setting the following parameters in ComfyUI:

- `font_file` fonts located in the <b>custom_nodes\ComfyUI-Mana-Nodes\font\example_font.ttf</b> directory (supports .ttf, .otf, .woff, .woff2).
- `font_color` Color of the text. (https://www.w3.org/wiki/CSS3/Color/Extended_color_keywords)
- `background_color` Background color of the image.
- `border_color` Color of the border around the text.
- `border_width` Width of the text border.
- `shadow_color` Width of the text border.
- `shadow_offset_x` Horizontal offset of the shadow.
- `shadow_offset_y` Vertical offset of the shadow.
- `line_spacing` Spacing between lines of text.
- `kerning` Spacing between characters of font.
- `padding` Padding between image border and font.
- `frame_count` Number of frames (images) to generate.
- `image_width` Width of the generated images.
- `image_height` Height of the generated images.
- `transcription_mode` Mode of text transcription ('word', 'line', 'fill').
- `text_alignment` Alignment of the text in the image.
- `text_interpolation_options` Mode of text interpolation ('strict', 'interpolation', 'cumulative').
- `text` The text to render in the images. (is ignored when optional input transcription is given)
- `animation_reset` Defines when the animation resets ('word', 'line', 'never').
- `animation_easing` Easing function for animation (e.g., 'linear', 'exponential').
- `animation_duration` Duration of the animation.
- `start_font_size`, `end_font_size` Starting and ending size of the font. 
- `start_x_offset`, `end_x_offset`, `start_y_offset`, `end_y_offset` Offsets for text positioning.
- `start_rotation`, `end_rotation` Rotation angles for the text.
- `rotation_anchor_x`, `rotation_anchor_y` offset of the rotation anchor point, relative to the texts initial position.

### Optional Inputs

- `input_images` Text will be overlayed on input_images instead of background_color.
- `transcription` Transcription from the speech2text node, contains dict with timestamps, framerate and transcribed words.

### Outputs

- `images` The generated images with the specified text and configurations.
- `transcription_framestamps` Outputs a string containing the framestamps, new line calculated based on image width. (Can be useful to manually correct mistakes by speech recognition)
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
- Negative values can be used to offset in opposite direction `start_x_offset = -100`, `end_x_offset = 0`

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

- `video` Path the video file.
- `frame_limit` Maximum number of frames to extract from the video.
- `frame_start` Starting frame number for extraction.
- `filename_prefix` Prefix for naming the extracted audio file. (relative to .\ComfyUI-Mana-Nodes)

### Outputs

- `frames` Extracted frames as image tensors.
- `frame_count` Total number of frames extracted.
- `audio` Path of the extracted audio file.
- `fps` Frames per second of the video.
- `height`, `width:` Dimensions of the extracted frames.

## speech2text Node

Converts spoken words in an audio file to text using a deep learning model.

### Required Inputs

- `audio` Audio file path or URL.
- `wav2vec2_model` The Wav2Vec2 model used for speech recognition. (https://huggingface.co/models?search=wav2vec2)
- `spell_check_language` Language for the spell checker.
- `framestamps_max_chars` Maximum characters allowed until new framestamp lines created.

### Optional Inputs

- `fps` Frames per second, used for synchronizing with video. (Default set to 30)

### Outputs

- `transcription` Text transcription of the audio. (Should only be used as font2img transcription input)
- `raw_string` Raw string of the transcription without timestamps.
- `framestamps_string` Frame-stamped transcription.
- `timestamps_string` Transcription with timestamps.

### Example Outputs

- `raw_string` Returns the transcribed text as one line.

```
THE GREATEST TRICK THE DEVIL EVER PULLED WAS CONVINCING THE WORLD HE DIDN'T EXIST
```

- `framestamps_string` Depending on the <b>framestamps_max_chars</b> parameter the sentece will be cleared and starts to build up again until max_chars is reached again. 
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

`timestamps_string` Returns all transcribed words, their start_time and end_time in json format as a string.

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
...
]
```


## text2speech Node

Converts text to speech and saves the output as an audio file.

### Required Inputs

- `text` The text to be converted into speech.
- `filename_prefix` Prefix for naming the audio file. (relative to .\ComfyUI-Mana-Nodes)

This node uses a text-to-speech pipeline to convert input text into spoken words, saving the result as a WAV file. The generated audio file is named using the provided filename prefix and is stored relative to the .\ComfyUI-Mana-Nodes directory.

Model: [https://huggingface.co/spaces/suno/bark](https://huggingface.co/suno/bark)

### Foreign Language

Bark supports various languages out-of-the-box and automatically determines language from input text. When prompted with code-switched text, Bark will even attempt to employ the native accent for the respective languages in the same voice.

Example:
<pre>Buenos días Miguel. Tu colega piensa que tu alemán es extremadamente malo. But I suppose your english isn't terrible.</pre>

### Non-Speech Sounds

Below is a list of some known non-speech sounds, but we are finding more every day.
<pre>
[laughter]
[laughs]
[sighs]
[music]
[gasps]
[clears throat]
— or … for hesitations
♪ for song lyrics
capitalization for emphasis of a word
MAN/WOMAN: for bias towards speaker
</pre>

Example:
<pre>" [clears throat] Hello, my name is Suno. And, uh — and I like pizza. [laughs] But I also have other interests such as... ♪ singing ♪."</pre>

### Music

Bark can generate all types of audio, and, in principle, doesn’t see a difference between speech and music. Sometimes Bark chooses to generate text as music, but you can help it out by adding music notes around your lyrics.

Example:
<pre>♪ In the jungle, the mighty jungle, the lion barks tonight ♪</pre>

### Speaker Prompts

You can provide certain speaker prompts such as NARRATOR, MAN, WOMAN, etc. Please note that these are not always respected, especially if a conflicting audio history prompt is given.

Example:
<pre>WOMAN: I would like an oatmilk latte please.
MAN: Wow, that's expensive!</pre>

## string2file Node

Writes a given string to a text file.

### Required Inputs

- `string` The string to be written to the file.
- `filename_prefix` Prefix for naming the text file. (relative to .\ComfyUI-Mana-Nodes)

## audio2video Node

Combines a sequence of images (frames) with an audio file to create a video.

### Required Inputs

- `audio` Audio file path or URL.
- `frames` Sequence of images to be used as video frames.
- `filename_prefix` Prefix for naming the video file. (relative to .\ComfyUI-Mana-Nodes)
- `fps` Frames per second for the video.

### Outputs

- `video_file_path` Path to the created video file.

## Example Workflows

### Font Animation 

These workflows are included in the example_workflows directory: 

#### example_workflow_1.json 

### Speech Recognition

![Screenshot 2024-03-05 at 15-54-43 ComfyUI](https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/91c8c306-761e-4fa9-a9a8-c0c0e3cc3c96)

#### example_workflow_2.json 

![Screenshot 2024-03-14 at 15-24-36 ComfyUI](https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/8caba06f-e24e-4096-96a4-21a91fdb6c5b)

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

