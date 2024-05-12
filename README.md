![ezgif com-optimize(2)](https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/f48b37c2-c3db-408f-ada8-a6bf336b6549)

![Static Badge](https://img.shields.io/badge/release-v1.0.0-black?style=plastic&logo=GitHub&logoColor=white&color=green) 
[![Custom Badge](https://img.shields.io/badge/buy-coffe-orange?style=plastic&logo=buymeacoffee&logoColor=white&link=URL)](https://buymeacoffee.com/foreigngods)
<!-- 
<a href="https://github.com/ForeignGods/ComfyUI-Mana-Nodes/releases">
    <img alt="GitHub all releases" src="https://img.shields.io/github/downloads/ForeignGods/ComfyUI-Mana-Nodes/latest/total">
</a>
-->
Welcome to the ComfyUI-Mana-Nodes project! 

This collection of custom nodes is designed to supercharge text-based content creation within the ComfyUI environment. 

Whether you're working on dynamic captions, transcribing audio, or crafting engaging visual content, Mana Nodes has got you covered.

If you like Mana Nodes, give our repo a [⭐ Star](https://github.com/ForeignGods/ComfyUI-Mana-Nodes) and [👀 Watch](https://github.com/ForeignGods/ComfyUI-Mana-Nodes/subscription) our repository to stay updated.
  
## Installation
You can install Mana Nodes via the [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)

Or simply clone the repo into the `custom_nodes` directory with this command:

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

## Nodes

<details>
  <summary>✒️ <b>Text to Image Generator</b></summary>
  
#### Required Inputs

#### `font`

To set the font and its styling you need to input 🆗 <b>Font Properties</b> node here.

#### `canvas`

To configure the canvas input the 🖼️ <b>Canvas Properties</b>

#### `text`

Specifies the text to be rendered on the images. Supports multiline text input for rendering on separate lines.
- For simple text: Input the text directly as a string.
- For frame-specific text: Use a JSON-like format where each line specifies a frame number and the corresponding text. Example:
    ``` 
    "1": "Hello",
    "10": "World",
    "20": "End"
    ```

#### `frame_count`

Sets the amount of frames this node will output.

#### Optional Inputs

#### `transcription`

Input the transcription output from the <b>🎤 Speech Recognition</b> node here.
Based on this transcription data, 🖼️ <b>Canvas Properties</b> and 🆗 <b>Font Properties</b> the text should be formatted in a way that builds up lines of words until there is no space on the canvas left (transcription_mode: fill, line).

#### `highlight_font`

Input a secondary font 🆗 <b>Font Properties</b>, that is used to highlight the active caption (transcription_mode: fill, line). When manually setting the text the following syntax can be used to defined which word/character:
``` 
Hello <tag>World</tag>
``` 

#### Outputs

#### `images` 

The generated images with the specified text and configurations, in common ComfyUI format (compatible with other nodes).

#### `transcription_framestamps` 

Framestamps formatted based on canvas, font and transcription settings.
Can be useful to manually correct errors by 🎤 <b>Speech Recognition</b> node.
Example: Save this output with 📝 <b>Save/Preview Text</b> -> manually correct mistakes -> remove transcription input from ✒️ <b>Text to Image Generator</b> node -> paste corrected framestamps into text input field of ✒️ <b>Text to Image Generator</b> node.


</details>

<details>
  <summary>🆗 <b>Font Properties</b></summary>
  
#### Required Inputs

#### `font_file`

Fonts located in the custom_nodes\ComfyUI-Mana-Nodes\font_files\example_font.ttf or system font directories (supports .ttf, .otf, .woff, .woff2).

#### `font_size` 

Either set single value font_size or input animation definition via the ⏰ <b>Scheduled Values</b> node. (Convert font_size to input)

#### `font_color` 

Either set single color value (CSS3/Color/Extended color keywords) or input animation definition via the 🌈 <b>Preset Color Animations</b> node. (Convert font_color to input)

#### `x_offset`, `y_offset`  

Either set single horiontal and vertical offset value or input animation definition via the ⏰ <b>Scheduled Values</b> node. (Convert x_offset/y_offset to input)

#### `rotation` 

Either set single rotation value or input animation definition via the ⏰ <b>Scheduled Values</b> node. (Convert rotation to input)

#### `rotation_anchor_x`, `rotation_anchor_y` 

Horizontal and vertical offsets of the rotation anchor point, relative to the texts initial position.

#### `kerning` 

Spacing between characters of font.

#### `border_width` 

Width of the text border.

#### `border_color` 

Either set single color value (CSS3/Color/Extended color keywords) or input animation definition via the 🌈 <b>Preset Color Animations</b> node. (Convert border_color to input)

#### `shadow_color` 

Either set single color value (CSS3/Color/Extended color keywords) or input animation definition via the 🌈 <b>Preset Color Animations</b> node. (Convert shadow_color to input)

#### `shadow_offset_x`, `shadow_offset_y`  

Horizontal and vertical offset of the text shadow.

#### Outputs

#### `font` 

Used as input on ✒️ <b>Text to Image Generator</b> node for the font and highlight_font.

</details>

<details>
  <summary>🖼️ <b>Canvas Properties</b></summary>

#### Required Inputs

#### `height`, `width` 

Dimensions of the canvas.

#### `background_color`

Background color of the canvas. (CSS3/Color/Extended color keywords)

#### `padding` 

Padding between image border and font.

#### `line_spacing` 

Spacing between lines of text on the canvas.

#### Optional Inputs

#### `images`

Can be used to input images instead of using background_color. 

#### Outputs

#### `canvas` 

Used as input on ✒️ <b>Text to Image Generator</b> node to define the canvas settings.

</details>

<details>
  <summary>⏰ <b>Scheduled Values</b></summary>

![Screenshot 2024-04-27 at 17-07-10 ComfyUI](https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/ee456e65-9950-4138-8b37-23b007ec92d9)


#### Required Inputs

#### `frame_count`

Sets the range of the x axis of the chart. (always starts at 1)

#### `value_range`

Sets the range of the y axis of the chart. (Example: 25, will would be ranging from -25 to 25)
This can be changed by zooming via the mousewheel and will reset to the specified value if changed.

#### `easing_type` 

Is used to generate values in between of the manually added values by the user by clicking the <b>Generate Values</b> button.
            
The available easing functions are:

- linear
- easeInQuad
- easeOutQuad
- easeInOutQuad
- easeInCubic
- easeOutCubic
- easeInOutCubic
- easeInQuart
- easeOutQuart
- easeInOutQuart
- easeInQuint
- easeOutQuint
- easeInOutQuint
- exponential

#### `step_mode` 

The option <b>single</b> will force the chart to display every single tick/step on the chart.
The option <b>auto</b> will automatically remove ticks/step to prevent overlapping.

#### `animation_reset` 

Used to specify the reset behaviour of the animation.

- word: animation will be reset when a new word is displayed, stays on last value when animation finished before word change.
- line: animation will be reset when a new line is displayed, stays on last value when animation finished before line change.
- never: animation will just run once and stop on last value. (Not affected by word or line change)
- looped: animation will endlessly loop. (Not affected by word or line change)
- pingpong: animation will first play forward then back and so on. (Not affected by word or line change)

#### `scheduled_values` 

Adding Values: Click on the chart to add keyframes at specific points.
Editing Values: Double-click on a keyframe to edit its frame and value.
Deleting Values: Click on the delete button associated with each keyframe to remove it.
Generating Values: Click on the "Generate Values" button to interpolate values between existing keyframes.
Deleting Generated Values: Click on the "Delete Generated" button to remove all interpolated values.

#### Outputs

#### `scheduled_values` 

Outputs a list of frame and value pairs and the animation_reset option.
At the moment this output can be used to animate the following widgets (Convert property to input) of the 🆗 <b>Font Properties</b> node:
- font_size (font, higlight_font)
- x_offset (font)
- y_offset (font)
- rotation (font)

</details>

<details>
  <summary>🌈 <b>Preset Color Animations</b></summary>

#### Required Inputs

#### `color_preset` 

Currently the following color animation presets are available:
- rainbow
- sunset
- grey
- ocean
- forest
- fire
- sky
- earth

#### `animation_duration`

Sets the length of the animation measured as frames.

#### `animation_reset` 

Used to specify the reset behaviour of the animation.

- word: animation will be reset when a new word is displayed, stays on last value when animation finished before word change.
- line: animation will be reset when a new line is displayed, stays on last value when animation finished before line change.
- never: animation will just run once and stop on last value. (Not affected by word or line change)
- looped: animation will endlessly loop. (Not affected by word or line change)
- pingpong: animation will first play forward then back and so on. (Not affected by word or line change)
  
#### Outputs

#### `scheduled_colors` 

Outputs a list of frame and color definitions and the animation_reset option.
At the moment this output can be used to animate the following widgets (Convert property to input) of the 🆗 <b>Font Properties</b> node:
- font_color (font, higlight_font)
- border_color (font, higlight_font)
- shadow_color (font, higlight_font)

</details>

<details>
  <summary>🎤 <b>Speech Recognition</b></summary>

Converts spoken words in an audio file to text using a deep learning model.

#### Required Inputs

#### `audio` 
Audio file path or URL.
#### `wav2vec2_model` 
The Wav2Vec2 model used for speech recognition. (https://huggingface.co/models?search=wav2vec2)
#### `spell_check_language` 
Language for the spell checker.
#### `framestamps_max_chars` 
Maximum characters allowed until new framestamp line is created.

#### Optional Inputs

#### `fps` 
Frames per second, used for synchronizing with video. (Default set to 30)

#### Outputs

#### `transcription` 
Text transcription of the audio. (Should only be used as font2img transcription input)
#### `raw_string` 
Raw string of the transcription without timestamps.
### `framestamps_string` 
Frame-stamped transcription.
### `timestamps_string` 
Transcription with timestamps.

#### Example Outputs

#### `raw_string` 
Returns the transcribed text as one line.

```
THE GREATEST TRICK THE DEVIL EVER PULLED WAS CONVINCING THE WORLD HE DIDN'T EXIST
```

#### `framestamps_string` 
Depending on the <b>framestamps_max_chars</b> parameter the sentece will be cleared and starts to build up again until max_chars is reached again. 
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

#### `timestamps_string` 
Returns all transcribed words, their start_time and end_time in json format as a string.

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

</details>

<details>
  <summary>🎞️ <b>Split Video</b></summary>


#### Required Inputs

#### `video` 
Path the video file.
#### `frame_limit` 
Maximum number of frames to extract from the video.
#### `frame_start` 
Starting frame number for extraction.
#### `filename_prefix` 
Prefix for naming the extracted audio file. (relative to .\ComfyUI\output)

#### Outputs

#### `frames` 
Extracted frames as image tensors.
#### `frame_count` 
Total number of frames extracted.
#### `audio_file` 
Path of the extracted audio file.
#### `fps` 
Frames per second of the video.
#### `height`, `width:` 
Dimensions of the extracted frames.

</details>

<details>
  <summary>🎥 <b>Combine Video</b></summary>

#### Required Inputs

#### `frames` 
Sequence of images to be used as video frames.
#### `filename_prefix` 
Prefix for naming the video file. (relative to .\ComfyUI\output)
#### `fps` 
Frames per second for the video.

#### Optional Inputs

#### `audio_file` 
Audio file path or URL.

#### Outputs

#### `video_file` 
Path to the created video file.

</details>

<details>
  <summary>📣 <b>Generate Audio</b> (experimental)</summary>


Converts text to speech and saves the output as an audio file.

#### Required Inputs

#### `text` 
The text to be converted into speech.
#### `filename_prefix` 
Prefix for naming the audio file. (relative to .\ComfyUI\output)

This node uses a text-to-speech pipeline to convert input text into spoken words, saving the result as a WAV file. The generated audio file is named using the provided filename prefix and is stored relative to the .\ComfyUI-Mana-Nodes directory.

Model: [https://huggingface.co/spaces/suno/bark](https://huggingface.co/suno/bark)

#### Foreign Language

Bark supports various languages out-of-the-box and automatically determines language from input text. When prompted with code-switched text, Bark will even attempt to employ the native accent for the respective languages in the same voice.

Example:
<pre>Buenos días Miguel. Tu colega piensa que tu alemán es extremadamente malo. But I suppose your english isn't terrible.</pre>

#### Non-Speech Sounds

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

#### Music

Bark can generate all types of audio, and, in principle, doesn’t see a difference between speech and music. Sometimes Bark chooses to generate text as music, but you can help it out by adding music notes around your lyrics.

Example:
<pre>♪ In the jungle, the mighty jungle, the lion barks tonight ♪</pre>

#### Speaker Prompts

You can provide certain speaker prompts such as NARRATOR, MAN, WOMAN, etc. Please note that these are not always respected, especially if a conflicting audio history prompt is given.

Example:
<pre>WOMAN: I would like an oatmilk latte please.
MAN: Wow, that's expensive!</pre>



</details>
<details>
  <summary>📝 <b>Save/Preview Text</b></summary>

#### Required Inputs

#### `string` 
The string to be written to the file.
#### `filename_prefix` 
Prefix for naming the text file. (relative to .\output)

</details>

## Example Workflows

### LCM AnimateDiff Text Animation 

#### Demo

| Demo 1 | Demo 2 | Demo 3 |
| ------ | ------ | ------ |
|![demo1](https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/7b77b9cc-457f-4061-ac6c-2f78efb8bffc)|![demo2](https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/89bc4309-6c46-4d08-9d9c-521e00415e65)|![demo3](https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/ae2e09c5-459c-4b4d-ad71-4db31684573f)|


#### Workflow

[example_workflow_1.json](example_workflows/example_workflow_1.json)

The values for the ⏰ Scheduled Values node cannot be imported yet (you have to add them yourself).

![Screenshot 2024-04-28 at 19-18-01 ComfyUI](https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/fa739ab0-91e5-4df7-9bd9-727abb6fb86a)

### Speech Recognition Caption Generator 

#### Demo

Turn on audio.

https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/e5a39327-db61-46ad-abea-10e27e4551c1

#### Workflow

[example_workflow_2.json](example_workflows/example_workflow_2.json)

![TRANSCRIPTION](https://github.com/ForeignGods/ComfyUI-Mana-Nodes/assets/78089013/e4d6aa73-3a4b-483e-b763-73b88c8cb261)

## To-Do

- [ ] Improve Speech Recognition
- [ ] Improve Text to Speech
- [ ] Node to download fonts from DaFont.com
- [ ] SVG Loader/Animator
- [ ] Text to Image Generator Alpha Channel
- [ ] Add Font Support for non Latin Characters
- [ ] 3D Effects, Bevel/Emboss, Inner Shading, Fade in/out 
- [ ] Find a better way to define color animations
- [ ] Make more Font Properties animatable

## Contributing

Your contributions to improve Mana Nodes are welcome! 

If you have suggestions or enhancements, feel free to fork this repository, apply your changes, and create a pull request. For significant modifications or feature requests, please open an issue first to discuss what you'd like to change.

