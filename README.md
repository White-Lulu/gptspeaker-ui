# gptspeaker-ui

[![English](https://img.shields.io/badge/lang-en-blue.svg)](https://github.com/White-Lulu/gptspeaker-ui/blob/main/README_zh-CN.md)

This project is a modified version of the following project:

- **Original Project**: gptspeaker
- **Original Author**: jackwuwei
- **Original Project Link**: [https://github.com/jackwuwei/gptspeaker](https://github.com/jackwuwei/gptspeaker)

For the main usage, please refer to the original project.

## Major Changes

1. **Process Output**: Added some process-related outputs based on personal needs.
2. **Keyword Modification**: Changed `keyword` to `xiaofan tongxue` (4th tone fan).
3. **Simple UI Interface** (made by a beginner, please be kind if any experts notice):
   - **Speaker**: Select prompt and model, and take notes.
   - **Notes**: Display notes.
   - **Setting**: Set themes, voice, specific model versions, and delete notes.

![Speaker](/image/3.png "Speaker")

![Notes](/image/4.png "Notes")

![Setting](/image/2.png "Setting")

## Usage

1. Refer to the original project ([link](https://github.com/jackwuwei/gptspeaker)) to set up the environment and configure API keys.
   - `config1.json` in this project is for DeepSeek configuration.
   - `config2.json` in this project is for OpenAI ChatGPT configuration.
2. On Windows, run `start.bat` (run `stop.bat` when finished).
   - This is equivalent to running `server.py` and opening any `./static/xxx.html`.

## License

This project is released under the BSD 2-Clause License. For details, please see the [LICENSE](LICENSE) file.
