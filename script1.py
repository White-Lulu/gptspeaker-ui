#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jack Wu. All rights reserved.
# Licensed under the BSD license. See LICENSE.md file in the project root for full license information.
"""
Smart Speaker using Azure Speech SDK and OpenAI ChatGPT API
"""
import azure.cognitiveservices.speech as speechsdk
import openai
import asyncio # 异步IO处理模块
import json
from collections import namedtuple # 命名元组工具
import tiktoken # OPENAI token计数工具
import time
import sys
import os
import psutil

EOF = object() # End of file 定义文件结束标记

PID_FILE = "script1.pid"

voice = sys.argv[3]
chatname = sys.argv[4]
username = sys.argv[5]

def get_previous_pid():
    """从文件读取上一次运行的PID"""
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return None
    return None

def kill_previous_process(pid):
    """尝试杀死上一个进程"""
    if pid:
        try:
            process = psutil.Process(pid)
            process.terminate()  # 终止进程
            print(f"成功终止进程: {pid}")
        except psutil.NoSuchProcess:
            print(f"进程 {pid} 不存在")
        except psutil.AccessDenied:
            print(f"无权限终止进程 {pid}")

def record_current_pid():
    """记录当前进程的PID"""
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))


# 2. Load config.json
def load_config():
    selected_model = sys.argv[1]
    if selected_model=='DeepSeek':
        config_file = 'config1.json'
    elif selected_model=='OpenAI':
        config_file = 'config2.json'
    
    try:
        with open(config_file, encoding='utf-8') as f:
            config = json.load(f, object_hook=lambda d: namedtuple('X', d.keys())(*d.values())) # 以特定格式读取json文件
            if not config.AzureCognitiveServices.Key or not config.AzureCognitiveServices.Region or (not config.OpenAI.Key and not config.AzureOpenAI.Key): # 至少需要azure的key，region，openai的key或者azureopenai的key
                with open("output.txt", "a", encoding="utf-8") as file:
                    file.write("Missing required configuration.\n")
                raise ValueError("Missing required configuration.") # 必要配置缺失异常
            return config
    except FileNotFoundError: # 找不到文件异常（请确认当前目录）
        with open("output.txt", "w", encoding="utf-8") as file:
            file.write("Error: config file not found.\n")

    except Exception as e: # 其他异常
        with open("output.txt", "w", encoding="utf-8") as file:
            file.write(f"Error loading config: {e}\n")
        
# If tokens greater than 4096, then remove history message
def truncate_conversation(conversation, max_tokens): # 截断对话历史
    total_tokens = 0
    truncated_conversation = []
    encoding = tiktoken.get_encoding("cl100k_base")

    for message in reversed(conversation):
        message_tokens = len(encoding.encode(message['content']))
        if total_tokens + message_tokens > max_tokens - 100: 
            with open("output.txt", "a", encoding="utf-8") as file:
                file.write(f'Total tokens is limit {total_tokens + message_tokens}\n')
            break
        total_tokens += message_tokens
        truncated_conversation.append(message)

    conversation = list(reversed(truncated_conversation))

# Prompts OpenAI with a request and async send sentences to queue.
async def ask_openai_async(client, model, prompt, max_token, conversation, queue, ending):
    # Append user questions
    conversation.append({"role":"user","content":sys.argv[2]+prompt}) 

    # Count token limit and remove early histroy conversation 
    truncate_conversation(conversation, max_token)
    #file.write(conversation)
    
    # Save one sentence
    collected_messages = ""

    # Save whole GPT answer
    full_answer = ""

    # Ask OpenAI
    response = await client.chat.completions.create(model=model, 
                                                   messages=conversation,
                                                   stream=True)
    
    # iterate through the stream of events
    async for chunk in response:
        if not chunk.choices:
            continue

        chunk_message = chunk.choices[0].delta.content
        if not chunk_message:
            continue
        else:
            chunk_message = chunk_message.replace('\n', ' ')  # extract the message

        collected_messages += chunk_message  # save the message
        if collected_messages.endswith(ending): # One sentence
            with open("output.txt", "a", encoding="utf-8") as file:
                file.write(f"{chatname}: {collected_messages}\n")
            
            await queue.put(collected_messages)
            full_answer += collected_messages
            collected_messages = ""

    # Save history message for continuous conversations
    conversation.append({"role":"assistant","content":full_answer})

# async read message from queue and synthesized speech
async def text_to_speech_async(speech_synthesizer, queue):
    while True:
        text = await queue.get()
        if text is EOF:
            break

        # Azure text to speech output
        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        # Check result
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            pass
            #file.write("Speech synthesized to speaker for text [{}]".format(text))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            with open("output.txt", "a", encoding="utf-8") as file:
                file.write("Speech synthesis canceled: {}\n".format(cancellation_details.reason))
            
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                with open("output.txt", "a", encoding="utf-8") as file:
                    file.write("Error details: {}\n".format(cancellation_details.error_details))
                

# 5.1 Detect keyword and wakeup
def detect_keyword(recognizer, model, keyword, audio_config):
    done = False  # 结果标志先设置为False

    def recognized_cb(evt): # 识别回调
        nonlocal done
        # Only a keyword phrase is recognized. The result cannot be 'NoMatch'
        # and there is no timeout. The recognizer runs until a keyword phrase
        # is detected or recognition is canceled (by stop_recognition_async()
        # or due to the end of an input file or stream).
        result = evt.result # 获取结果
        if result.reason == speechsdk.ResultReason.RecognizedKeyword: # 如果识别到关键词
            with open("output.txt", "a", encoding="utf-8") as file:
                file.write("RECOGNIZED KEYWORD √ Please wait a few seconds ^x^\n") # 输出识别标志
            
        nonlocal done
        done = True # 结果标志为True

    def canceled_cb(evt): # 取消回调
        nonlocal done
        result = evt.result # 获取结果
        if result.reason == speechsdk.ResultReason.Canceled: # 如果取消
            with open("output.txt", "a", encoding="utf-8") as file:
                file.write('CANCELED: {}\n'.format(result.cancellation_details.reason)) # 输出取消原因
        nonlocal done
        done = True # 结果标志为True

    # 确保语音识别器处于空闲状态
    recognizer.stop_continuous_recognition()
    recognizer.stop_keyword_recognition()

    # Connect callbacks to the events fired by the keyword recognizer.
    recognizer.recognized.connect(recognized_cb) # 连接识别回调（但还未执行）
    recognizer.canceled.connect(canceled_cb) # 连接取消回调（但还未执行）

    # Start keyword recognition.
    recognizer.start_keyword_recognition(model) # 开始关键词识别
    with open("output.txt", "a", encoding="utf-8") as file:
        file.write('Please start with "{}"\n'.format(keyword))
    
    
    while not done: # 等待激发结果标志为True
        time.sleep(.5)

    recognizer.recognized.disconnect_all() # 断开识别连接
    recognizer.canceled.disconnect_all() # 断开取消连接
    recognizer.stop_keyword_recognition() # 停止关键词识别

    # Read result audio (incl. the keyword).
    return done # 返回结果标志（一定为True）

# 3. 创建异步客户端和GPT模型
def create_aysnc_client(config): # 传入配置
    # Create async OpenAI Client
    if config.OpenAI.Key: # 先尝试OpenAIkey
        client = openai.AsyncClient(api_key=config.OpenAI.Key) # 使用openai的函数创建异步客户端
        if config.OpenAI.ApiBase:  # 如果有API基础地址
            client.base_url = config.OpenAI.ApiBase  # 设置客户端的基础地址
        #file.write('成功创建openai异步客户端Client')
        return client, config.OpenAI.Model # 返回客户端和模型
    elif config.AzureOpenAI.Key:
        client = openai.AsyncAzureOpenAI(api_key=config.AzureOpenAI.Key, # 使用AzureOpenAI的函数创建异步客户端
                                         api_version=config.AzureOpenAI.api_version, # 设置api版本
                                         azure_endpoint=config.AzureOpenAI.Endpoint # 设置Azure的终结点
        )
        return client, config.AzureOpenAI.Model # 返回客户端和模型

# 1. Main function
# Continuously listens for speech input to recognize and send as text to Azure OpenAI
async def chat_with_open_ai():
    
    # Load config.json
    file=open("output.txt", "w", encoding="utf-8")
    file.write('------------ Loading ------------\n')
    
    config = load_config() # 加载配置文件（见2.）
    file.write('config √ --- ')
    
    # Create async client
    client, gpt_model = create_aysnc_client(config=config) # 创建异步客户端和GPT模型（见3.）
    file.write('client √ --- ')
    # 4. 设置Azure语音服务的配置（根据config.json）

    speech_config = speechsdk.SpeechConfig(subscription=config.AzureCognitiveServices.Key, 
                                           region=config.AzureCognitiveServices.Region) # 设置Azure（api,region）
    audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True) # 设置音频输出配置（默认扬声器）
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True) # 设置音频输入配置（默认麦克风）
    file.write('audio √ --- ')

    # Should be the locale for the speaker's language.
    speech_config.speech_recognition_language = config.AzureCognitiveServices.SpeechRecognitionLanguage # 设置语音识别语言
    speech_recognizer1 = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config) # 设置语音识别器
    file.write('recognizer √ --- ')

    ending_punctuations = (".", "?", "!", ";") # 设置结束标点
    if (speech_config.speech_recognition_language == "zh-CN"): # 如果是中文
        ending_punctuations = ("。", "？", "！", "；", "”") # 设置中文结束标点
    file.write('punctuations √ --- ')
    # The language of the voice that responds on behalf of Azure OpenAI.
    speech_config.speech_synthesis_voice_name = voice # 设置语音合成语言
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config) # 设置语音合成器
    file.write('synthesizer √ --- ')

    # The phrase your keyword recognition model triggers on.
    kws_model = speechsdk.KeywordRecognitionModel(config.AzureCognitiveServices.WakePhraseModel) # 设置唤醒词模型
    conversation = [] # 保存对话历史
    file.write('conversation √ \n')
    file.write('------------- Ready -------------\n')
    file.close()
    

    # 初始化 WebSocket 连接
    #websocket = await websockets.connect('ws://localhost:8765')
    #file.write('webSocket √ ')

    # 5. 循环监听用户输入
    while True:
        #file.write("Azure is listening. Say '{}' to start.".format(config.AzureCognitiveServices.WakeWord))
        try:
            # 5.1 Detect keyword
            if (not detect_keyword(speech_recognizer1, kws_model, config.AzureCognitiveServices.WakeWord, audio_config)):
                with open("output.txt", "a", encoding="utf-8") as file:
                    file.write('没有检测到唤醒词')
                continue # 如果没有检测到唤醒词，重新开始循环

            # Get audio from the microphone and then send it to the TTS service.
            #file.write('检测到唤醒词')
            #await websocket.send(json.dumps({'type': 'wake', 'keyword': '杰克同学'}))
            #file.write('发送唤醒词')

            await asyncio.sleep(1)
            
            speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config) # 设置语音识别器
            
            with open("output.txt", "a", encoding="utf-8") as file:
                file.write('Talk with me ! ^o^\n')
                file.write('-------------- Go ---------------\n')

            # await asyncio.sleep(1)

            speech_recognition_result = speech_recognizer.recognize_once_async().get() # 获取语音识别结果
            #file.write("识别内容:",speech_recognition_result)
            #await websocket.send(json.dumps({'type': 'speech', 'text': speech_recognition_result.text}))

            #file.write('End of speech recognition --------------------')
            # If speech is recognized, send it to OpenAI and listen for the response.
            if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech: # 如果识别到语音
                if speech_recognition_result.text == config.AzureCognitiveServices.StopWord: # 且如果识别到停止词
                    with open("output.txt", "a", encoding="utf-8") as file:
                        file.write("Conversation ended.\n") # 结束对话
                    break # 退出循环
                
                with open("output.txt", "a", encoding="utf-8") as file:
                    file.write("{}: {}\n".format(username,speech_recognition_result.text)) # 打印识别到的语音

                # Create queue for save GPT messages
                queue = asyncio.Queue() # 创建异步队列

                # Create async task for ask openai
                task_ask_gpt = asyncio.create_task(ask_openai_async(client, # 创建异步任务（传入客户端，GPT模型，识别到的语音，最大token，对话历史，队列，结束标点）
                                                                    gpt_model, 
                                                                    speech_recognition_result.text, 
                                                                    config.OpenAI.MaxTokens, 
                                                                    conversation, 
                                                                    queue,
                                                                    ending_punctuations))

                # Add task done callback, add a EOF message to end
                task_ask_gpt.add_done_callback(lambda _: queue.put_nowait(EOF)) # 添加任务完成回调，添加EOF消息以结束

                # Create async task for Text-to-Speech
                task_ask_tts = asyncio.create_task(text_to_speech_async(speech_synthesizer, queue)) # 创建异步任务（传入语音合成器，队列）

                # Wait all task completed
                await asyncio.gather(task_ask_gpt, task_ask_tts) # 等待所有任务完成
            elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch: # 如果没有匹配
                with open("output.txt", "a", encoding="utf-8") as file:
                    file.write("No speech could be recognized O.o: {}\n".format(speech_recognition_result.no_match_details)) # 打印无法识别的原因
                    file.write('One more time ~\n')
            elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled: # 如果取消
                cancellation_details = speech_recognition_result.cancellation_details # 获取取消详情
                file.write("Speech Recognition canceled: {}\n".format(cancellation_details.reason)) # 打印取消原因
                if cancellation_details.reason == speechsdk.CancellationReason.Error: # 如果是错误
                    with open("output.txt", "a", encoding="utf-8") as file:
                        file.write("Error details: {}\n".format(cancellation_details.error_details)) # 打印错误详情
        except EOFError: # 如果遇到EOF错误
            continue # 继续

if __name__ == '__main__':
     # 1. 读取并杀死上一个进程
    previous_pid = get_previous_pid()
    print(previous_pid)
    print(os.getpid())
    if previous_pid != os.getpid():
        kill_previous_process(previous_pid)

    # 2. 记录当前进程的PID
    record_current_pid()
    print(f"当前进程 PID: {os.getpid()}")
    
    # Main
    try:
        asyncio.run(chat_with_open_ai()) # 运行主异步任务
    except Exception as err:
        with open("output.txt", "w", encoding="utf-8") as file:
            file.write("Encountered exception. {}\n".format(err))

    
