<<<<<<< HEAD
from flask import Flask, jsonify ,request,send_from_directory
=======
from flask import Flask, jsonify ,request
>>>>>>> f918746 (1.0 speaker notes setting)
from flask_cors import CORS
import subprocess
import os
import json
<<<<<<< HEAD
from pathlib import Path

app = Flask(__name__, static_folder="static")

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

=======

app = Flask(__name__)
>>>>>>> f918746 (1.0 speaker notes setting)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

<<<<<<< HEAD
# Cache data
data_cache = {}
data_cache["voice"] = "zh-CN-XiaochenNeural"
data_cache["chatname"] = "😊"
data_cache["username"] = "😎"
data_cache["deepseekmodel"] = "deepseek-chat"
data_cache["openaimodel"] = "gpt-4o"

# Get project root directory
BASE_DIR = Path(__file__).parent.absolute()

class Config:
    """Application Configuration Class"""
    VENV_PYTHON = os.path.join(".venv", "Scripts", "python")
    CONFIG1_PATH = "config1.json"
    CONFIG2_PATH = "config2.json"
    OUTPUT_PATH = "output.txt"
    SERVER_PID = "server.pid"

# Record current Python process PID
pid = os.getpid()
with open(os.path.join(BASE_DIR, Config.SERVER_PID), "w") as f:
    f.write(str(pid))

# Receive data from speaking.html (model and prompt)
@app.route("/submit_model_prompt", methods=["POST"])
def submit_model_prompt():
    data = request.json  # Get data from request body
    data_cache["model"] = data.get("model")  # Cache model
    data_cache["prompt"] = data.get("prompt")  # Cache prompt

    # Check if all data is ready
    if all(key in data_cache for key in ["model", "prompt", "voice", "chatname", "deepseekmodel", "openaimodel"]):
        # All data is ready, start speaking_script.py
        env = os.environ.copy()  # Get current environment variables
        env["PYTHONUNBUFFERED"] = "1"  # Set environment variable for unbuffered Python output

        result = subprocess.run(
            [
                os.path.join(BASE_DIR, Config.VENV_PYTHON),
                "-u",
                "speaking_script.py",
                data_cache["model"],
                data_cache["prompt"],
                data_cache["voice"],
                data_cache["chatname"],
                data_cache["username"]
            ],
            capture_output=True,
            text=True,
            cwd=BASE_DIR,
=======
# 缓存数据
data_cache = {}
data_cache["voice"] = "zh-CN-XiaochenNeural"  # 缓存 voice
data_cache["chatname"] = "😊"   # 缓存 chatname
data_cache["username"] = "😎"
data_cache["deepseekmodel"] = "deepseek-chat" # 缓存 deepseekmodel
data_cache["openaimodel"] = "gpt-4o"  # 缓存 openaimodel

# 记录当前 Python 进程 PID
pid = os.getpid()
with open("server.pid", "w") as f:
    f.write(str(pid))

# 接收来自第一个页面的数据（model 和 prompt）
@app.route("/submit_model_prompt", methods=["POST"])
def submit_model_prompt():
    data = request.json  # 获取请求体中的数据
    data_cache["model"] = data.get("model")  # 缓存 model
    data_cache["prompt"] = data.get("prompt")  # 缓存 prompt

    # 检查是否所有数据都已准备好
    if all(key in data_cache for key in ["model", "prompt", "voice", "chatname", "deepseekmodel", "openaimodel"]):
        # 所有数据已准备好，启动 script1.py
        python_path = "g:/gptspeaker/gptspeaker/.venv/Scripts/python"  # 替换为虚拟环境中的 Python 路径
        env = os.environ.copy()  # 获取当前环境变量
        env["PYTHONUNBUFFERED"] = "1"  # 设置环境变量，使 Python 输出不缓冲
        script_dir = "G:/gptspeaker/gptspeaker"  # 替换为 script1.py 的实际路径

        result = subprocess.run(
            [python_path, "-u", "script1.py", data_cache["model"], data_cache["prompt"], data_cache["voice"], data_cache["chatname"], data_cache["username"]],
            capture_output=True,
            text=True,
            cwd=script_dir,
>>>>>>> f918746 (1.0 speaker notes setting)
            env=env
        )

        if result.returncode != 0:
            return jsonify({
<<<<<<< HEAD
                "message": "speaking_script execution failed",
                "error": result.stderr,
                "output": result.stdout
            })
        return jsonify({"message": "speaking_script execution completed", "output": result.stdout})
=======
                "message": "script1 执行失败",
                "error": result.stderr,
                "output": result.stdout  # 返回标准输出以供调试
            })
        return jsonify({"message": "script1 执行完成", "output": result.stdout})
>>>>>>> f918746 (1.0 speaker notes setting)
    else:
        return jsonify({"message": "Settings received, waiting for model and prompt"})
    

<<<<<<< HEAD
# Receive data from setting.html (voice, chatname, deepseekmodel and openaimodel)
=======
# 接收来自第二个页面的数据（voice、chatname、deepseekmodel 和 openaimodel）
>>>>>>> f918746 (1.0 speaker notes setting)
@app.route("/submit_settings", methods=["POST"])
def submit_settings():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

<<<<<<< HEAD
        # Update cache
=======
        # 更新缓存
>>>>>>> f918746 (1.0 speaker notes setting)
        data_cache["voice"] = data.get("voice")
        data_cache["chatname"] = data.get("chatname")
        data_cache["username"] = data.get("username")
        data_cache["deepseekmodel"] = data.get("deepseekmodel")
        data_cache["openaimodel"] = data.get("openaimodel")

<<<<<<< HEAD
        # Handle config1.json(DeepSeek)
        try:
            config1_path = os.path.join(BASE_DIR, Config.CONFIG1_PATH)
            with open(config1_path, "r", encoding="utf-8") as f1:
                config1 = json.load(f1)
                config1["OpenAI"]["Model"] = data_cache["deepseekmodel"]
                with open(config1_path, "w", encoding="utf-8") as f1:
=======
        # 处理 config1.json
        try:
            with open("config1.json", "r", encoding="utf-8") as f1:
                config1 = json.load(f1)
                config1["OpenAI"]["Model"] = data_cache["deepseekmodel"]
                with open("config1.json", "w", encoding="utf-8") as f1:
>>>>>>> f918746 (1.0 speaker notes setting)
                    json.dump(config1, f1, indent=4, ensure_ascii=False)
        except Exception as e:
            return jsonify({"error": f"Config1 error: {str(e)}"}), 500

<<<<<<< HEAD
        # Handle config2.json(OpenAI)
        try:
            config2_path = os.path.join(BASE_DIR, Config.CONFIG2_PATH)
            with open(config2_path, "r", encoding="utf-8") as f2:
                config2 = json.load(f2)
                config2["OpenAI"]["Model"] = data_cache["openaimodel"]
                with open(config2_path, "w", encoding="utf-8") as f2:
=======
        # 处理 config2.json
        try:
            with open("config2.json", "r", encoding="utf-8") as f2:
                config2 = json.load(f2)
                config2["OpenAI"]["Model"] = data_cache["openaimodel"]
                with open("config2.json", "w", encoding="utf-8") as f2:
>>>>>>> f918746 (1.0 speaker notes setting)
                    json.dump(config2, f2, indent=4, ensure_ascii=False)
        except Exception as e:
            return jsonify({"error": f"Config2 error: {str(e)}"}), 500

        return jsonify({"message": "Settings updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


<<<<<<< HEAD
# Read TXT file
@app.route("/read_txt", methods=["GET"])
def read_txt():
    try:
        output_path = os.path.join(BASE_DIR, Config.OUTPUT_PATH)
        with open(output_path, "r", encoding="utf-8") as file:
            content = file.read()
        return jsonify({"content": content})
    except FileNotFoundError:
        return jsonify({"content": "File not found"}), 404
=======
# 读取 TXT 文件
@app.route("/read_txt", methods=["GET"])
def read_txt():
    try:
        with open("output.txt", "r", encoding="utf-8") as file:
            content = file.read()
        return jsonify({"content": content})
    except FileNotFoundError:
        return jsonify({"content": "文件不存在"}), 404
>>>>>>> f918746 (1.0 speaker notes setting)

if __name__ == "__main__":
    app.run(debug=True, port=5000)