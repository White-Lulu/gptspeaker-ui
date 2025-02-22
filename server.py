from flask import Flask, jsonify ,request,send_from_directory
from flask_cors import CORS
import subprocess
import os
import json
from pathlib import Path

app = Flask(__name__, static_folder="static")

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

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
            env=env
        )

        if result.returncode != 0:
            return jsonify({
                "message": "speaking_script execution failed",
                "error": result.stderr,
                "output": result.stdout
            })
        return jsonify({"message": "speaking_script execution completed", "output": result.stdout})
    else:
        return jsonify({"message": "Settings received, waiting for model and prompt"})
    

# Receive data from setting.html (voice, chatname, deepseekmodel and openaimodel)
@app.route("/submit_settings", methods=["POST"])
def submit_settings():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        # Update cache
        data_cache["voice"] = data.get("voice")
        data_cache["chatname"] = data.get("chatname")
        data_cache["username"] = data.get("username")
        data_cache["deepseekmodel"] = data.get("deepseekmodel")
        data_cache["openaimodel"] = data.get("openaimodel")

        # Handle config1.json(DeepSeek)
        try:
            config1_path = os.path.join(BASE_DIR, Config.CONFIG1_PATH)
            with open(config1_path, "r", encoding="utf-8") as f1:
                config1 = json.load(f1)
                config1["OpenAI"]["Model"] = data_cache["deepseekmodel"]
                with open(config1_path, "w", encoding="utf-8") as f1:
                    json.dump(config1, f1, indent=4, ensure_ascii=False)
        except Exception as e:
            return jsonify({"error": f"Config1 error: {str(e)}"}), 500

        # Handle config2.json(OpenAI)
        try:
            config2_path = os.path.join(BASE_DIR, Config.CONFIG2_PATH)
            with open(config2_path, "r", encoding="utf-8") as f2:
                config2 = json.load(f2)
                config2["OpenAI"]["Model"] = data_cache["openaimodel"]
                with open(config2_path, "w", encoding="utf-8") as f2:
                    json.dump(config2, f2, indent=4, ensure_ascii=False)
        except Exception as e:
            return jsonify({"error": f"Config2 error: {str(e)}"}), 500

        return jsonify({"message": "Settings updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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

if __name__ == "__main__":
    app.run(debug=True, port=5000)