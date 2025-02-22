#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jack Wu. All rights reserved.
# Licensed under the BSD license. See LICENSE.md file in the project root for full license information.

# Modifications Copyright (c) 2025, White-Lulu
# - Added process output.
# - Changed keyword to "xiaofan tongxue".
# - Implemented a simple UI interface for Speaker, Notes, and Settings.
"""
Smart Speaker using Azure Speech SDK and DeepSeek / OpenAI ChatGPT API
"""
import azure.cognitiveservices.speech as speechsdk
from collections import namedtuple
import tiktoken
import asyncio
import psutil
import openai
import json
import time
import sys
import os

EOF = object() # End of file

PID_FILE = "speaking_script.pid"

voice = sys.argv[3]
chatname = sys.argv[4]
username = sys.argv[5]

# 0. Check PID
def get_previous_pid():
    """Read the previous process PID from file"""
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return None
    return None

def kill_previous_process(pid):
    """Try to terminate the previous process"""
    if pid:
        try:
            process = psutil.Process(pid)
            process.terminate()
            print(f"Successfully terminated process: {pid}")
        except psutil.NoSuchProcess:
            print(f"Process {pid} does not exist")
        except psutil.AccessDenied:
            print(f"Permission denied to terminate process {pid}")

def record_current_pid():
    """Record the previous process PID"""
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
            config = json.load(f, object_hook=lambda d: namedtuple('X', d.keys())(*d.values())) 
            if not config.AzureCognitiveServices.Key or not config.AzureCognitiveServices.Region or (not config.OpenAI.Key and not config.AzureOpenAI.Key): # 至少需要azure的key，region，openai的key或者azureopenai的key
                with open("output.txt", "a", encoding="utf-8") as file:
                    file.write("Missing required configuration.\n")
                raise ValueError("Missing required configuration.")
            return config
    except FileNotFoundError:
        with open("output.txt", "w", encoding="utf-8") as file:
            file.write("Error: config file not found.\n")

    except Exception as e:
        with open("output.txt", "w", encoding="utf-8") as file:
            file.write(f"Error loading config: {e}\n")

# 3. Create async client and GPT model
def create_aysnc_client(config):
    if config.OpenAI.Key:
        client = openai.AsyncClient(api_key=config.OpenAI.Key)
        if config.OpenAI.ApiBase:
            client.base_url = config.OpenAI.ApiBase 
        
        return client, config.OpenAI.Model
    elif config.AzureOpenAI.Key:
        client = openai.AsyncAzureOpenAI(api_key=config.AzureOpenAI.Key,
                                         api_version=config.AzureOpenAI.api_version,
                                         azure_endpoint=config.AzureOpenAI.Endpoint
        )
        return client, config.AzureOpenAI.Model

# 5.1 Detect keyword and wakeup
def detect_keyword(recognizer, model, keyword):
    done = False 

    def recognized_cb(evt):
        nonlocal done
        # Only a keyword phrase is recognized. The result cannot be 'NoMatch'
        # and there is no timeout. The recognizer runs until a keyword phrase
        # is detected or recognition is canceled (by stop_recognition_async()
        # or due to the end of an input file or stream).
        result = evt.result
        if result.reason == speechsdk.ResultReason.RecognizedKeyword:
            with open("output.txt", "a", encoding="utf-8") as file:
                file.write("RECOGNIZED KEYWORD √ Please wait a few seconds ^x^\n")
            
        nonlocal done
        done = True 

    def canceled_cb(evt):
        nonlocal done
        result = evt.result
        if result.reason == speechsdk.ResultReason.Canceled:
            with open("output.txt", "a", encoding="utf-8") as file:
                file.write('CANCELED: {}\n'.format(result.cancellation_details.reason))
        nonlocal done
        done = True

    # Ensure speech recognizer is idle.
    recognizer.stop_continuous_recognition()
    recognizer.stop_keyword_recognition()

    # Connect callbacks to the events fired by the keyword recognizer.
    recognizer.recognized.connect(recognized_cb) 
    recognizer.canceled.connect(canceled_cb) 

    # Start keyword recognition.
    recognizer.start_keyword_recognition(model)
    with open("output.txt", "a", encoding="utf-8") as file:
        file.write('Please start with "{}"\n'.format(keyword))
    
    
    while not done:
        time.sleep(.5)

    recognizer.recognized.disconnect_all()
    recognizer.canceled.disconnect_all()
    recognizer.stop_keyword_recognition()

    # Read result audio (incl. the keyword).
    return done

# 5.3 Prompts OpenAI with a request and async send sentences to queue.
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
    response = await client.chat.completions.create(model=model, messages=conversation,stream=True)
    
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

# If tokens greater than 4096, then remove history message
def truncate_conversation(conversation, max_tokens):
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

# 5.4 async read message from queue and synthesized speech
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
                
# 1. Main function
# Continuously listens for speech input to recognize and send as text to Azure OpenAI
async def chat_with_open_ai():
    # 2. Load config
    file=open("output.txt", "w", encoding="utf-8")
    file.write('------------ Loading ------------\n')
    
    config = load_config()
    file.write('config √ --- ')
    
    # 3. Create async client
    client, gpt_model = create_aysnc_client(config=config)
    file.write('client √ --- ')

    # 4. Set the config of AzureSpeechSDK

    speech_config = speechsdk.SpeechConfig(subscription=config.AzureCognitiveServices.Key, 
                                           region=config.AzureCognitiveServices.Region)
    audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    file.write('audio √ --- ')

    # Should be the locale for the speaker's language.
    speech_config.speech_recognition_language = config.AzureCognitiveServices.SpeechRecognitionLanguage
    speech_recognizer1 = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    file.write('recognizer √ --- ')

    ending_punctuations = (".", "?", "!", ";")
    if (speech_config.speech_recognition_language == "zh-CN"):
        ending_punctuations = ("。", "？", "！", "；", "”")
    file.write('punctuations √ --- ')

    # The language of the voice that responds on behalf of Azure OpenAI.
    speech_config.speech_synthesis_voice_name = voice 
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)
    file.write('synthesizer √ --- ')

    # The phrase your keyword recognition model triggers on.
    kws_model = speechsdk.KeywordRecognitionModel(config.AzureCognitiveServices.WakePhraseModel)
    
    conversation = []
    file.write('conversation √ \n')
    file.write('------------- Ready -------------\n')
    file.close()
    
    # 5. Recycle to detect keyword and speech recognition
    while True:
        try:
            # 5.1 Detect keyword
            if (not detect_keyword(speech_recognizer1, kws_model, config.AzureCognitiveServices.WakeWord)):
                with open("output.txt", "a", encoding="utf-8") as file:
                    file.write('Failed to recognize the keyword. Please try again.\n')
                continue

            await asyncio.sleep(1)
            
            # 5.2 Speech recognition
            speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config) # 设置语音识别器
            
            with open("output.txt", "a", encoding="utf-8") as file:
                file.write('Talk with me ! ^o^\n')
                file.write('-------------- Go ---------------\n')

            # await asyncio.sleep(1)

            speech_recognition_result = speech_recognizer.recognize_once_async().get()
           
            # 5.3 If speech is recognized, send it to OpenAI and listen for the response.
            if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                if speech_recognition_result.text == config.AzureCognitiveServices.StopWord:
                    with open("output.txt", "a", encoding="utf-8") as file:
                        file.write("Conversation ended.\n")
                    break
                
                with open("output.txt", "a", encoding="utf-8") as file:
                    file.write("{}: {}\n".format(username,speech_recognition_result.text))

                # Create queue for save GPT messages
                queue = asyncio.Queue()

                # Create async task for ask openai
                task_ask_gpt = asyncio.create_task(ask_openai_async(client,
                                                                    gpt_model, 
                                                                    speech_recognition_result.text, 
                                                                    config.OpenAI.MaxTokens, 
                                                                    conversation, 
                                                                    queue,
                                                                    ending_punctuations))

                # Add task done callback, add a EOF message to end
                task_ask_gpt.add_done_callback(lambda _: queue.put_nowait(EOF))

                # 5.4 Create async task for Text-to-Speech
                task_ask_tts = asyncio.create_task(text_to_speech_async(speech_synthesizer, queue))

                # Wait all task completed
                await asyncio.gather(task_ask_gpt, task_ask_tts)
            elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
                with open("output.txt", "a", encoding="utf-8") as file:
                    file.write("No speech could be recognized O.o: {}\n".format(speech_recognition_result.no_match_details))
                    file.write('One more time ~\n')
            elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_recognition_result.cancellation_details
                file.write("Speech Recognition canceled: {}\n".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    with open("output.txt", "a", encoding="utf-8") as file:
                        file.write("Error details: {}\n".format(cancellation_details.error_details))
        except EOFError:
            continue

if __name__ == '__main__':
    # 0. Read and kill previous process
    previous_pid = get_previous_pid()
    print(previous_pid)
    print(os.getpid())
    if previous_pid != os.getpid():
        kill_previous_process(previous_pid)

    # Record current process PID
    record_current_pid()
    print(f"Current process PID: {os.getpid()}")
    
    # Main
    try:
        asyncio.run(chat_with_open_ai())
    except Exception as err:
        with open("output.txt", "w", encoding="utf-8") as file:
            file.write("Encountered exception. {}\n".format(err))

    
