# gptspeaker-ui

[![中文](https://img.shields.io/badge/lang-cn-yellow.svg)](https://github.com/White-Lulu/gptspeaker-ui/blob/main/README_zh-CN.md)

本项目是基于以下项目的修改版本：

- **原项目**: gptspeaker
- **原作者**: jackwuwei
- **原项目链接**: [https://github.com/jackwuwei/gptspeaker](https://github.com/jackwuwei/gptspeaker)

主要用法请参考原项目。

## 主要改动

1. **进程输出**：根据自己的需求添加了一些关于进程的输出。
2. **关键词修改**：将 `keyword` 改为 `xiaofan tongxue`（四声 fan）。
3. **简单的 UI 界面**（小白制作简单粗糙，如有大佬注意到，请手下留情）：
   - **Speaker**：选择 prompt 和 model，可记笔记。
   - **Notes**：展示笔记。
   - **Setting**：设置主题、人声、具体模型版本等，删除笔记。

![Speaker](/image/3.png "Speaker")

![Notes](/image/4.png "Notes")

![Setting](/image/2.png "Setting")

## 使用方法

1. 参考原项目（[链接](https://github.com/jackwuwei/gptspeaker)），搭建环境，配置 API Key。
   - 本项目的 `config1.json` 为 DeepSeek 配置。
   - 本项目的 `config2.json` 为 OpenAI ChatGPT 配置。
2. 在 Windows 上运行 `start.bat`（结束时运行 `stop.bat`）。
   - 相当于运行 `server.py` 并打开任意 `./static/xxx.html`。

## 许可证

本项目基于 BSD 2-Clause License 发布。详情请见 [LICENSE](LICENSE) 文件。