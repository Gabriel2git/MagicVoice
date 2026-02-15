import os
import sys
import time
import json
import threading
import base64
import numpy as np
import sounddevice as sd
import keyboard
import pyperclip
import dashscope
import winsound
from PIL import Image, ImageDraw
import pystray
import logging

try:
    import tomli as tomllib
except ImportError:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        raise ImportError("需要安装 tomli: pip install tomli")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_api_key():
    secret_file = os.path.join(os.path.dirname(__file__), 'secret.toml')
    if os.path.exists(secret_file):
        with open(secret_file, 'rb') as f:
            config = tomllib.load(f)
            if 'dashscope' in config and 'MAGICVOICE_API_KEY' in config['dashscope']:
                return config['dashscope']['MAGICVOICE_API_KEY']
    return os.environ.get('MAGICVOICE_API_KEY') or os.environ.get('DASHSCOPE_API_KEY')

API_KEY = load_api_key()
if not API_KEY:
    print("错误: 未找到 API Key，请检查 secret.toml 或环境变量")
    sys.exit(1)

dashscope.api_key = API_KEY

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = np.int16

ASR_MODEL = "fun-asr-realtime"
LLM_MODEL = "qwen-turbo"

SYSTEM_PROMPT = '''你是一个智能语音助手，帮助用户回答问题、完成任务。

请遵循以下原则：
1. 回答简洁明了，避免冗长
2. 用中文回答，语言自然流畅
3. 如果问题不明确，请先询问清楚
4. 保持友好和专业的态度'''

is_recording_f2 = False
is_recording_f4 = False
audio_queue_f2 = []
audio_queue_f4 = []
stream = None
stop_event = threading.Event()

def create_icon():
    width, height = 64, 64
    image = Image.new('RGB', (width, height), color=(66, 133, 244))
    dc = ImageDraw.Draw(image)
    dc.ellipse([16, 16, 48, 48], fill=(255, 255, 255))
    dc.ellipse([24, 20, 40, 44], fill=(66, 133, 244))
    return image

def paste_text(text):
    old = pyperclip.paste()
    pyperclip.copy(text)
    keyboard.send('ctrl+v')
    time.sleep(0.1)
    pyperclip.copy(old)

def generate_response(text):
    try:
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        messages.append({'role': 'user', 'content': text})
        
        response = dashscope.Generation.call(
            model=LLM_MODEL,
            messages=messages
        )
        if response.status_code == 200:
            return response.output.text
        return None
    except Exception as e:
        print(f"AI 生成错误: {e}")
        return None

class ASRCallbackF2:
    def __init__(self):
        self.full_text = ""
        self.is_started = False
    
    def on_open(self):
        self.is_started = True
        print("F2 识别已启动")
    
    def on_close(self):
        self.is_started = False
        print("F2 识别已关闭")
    
    def on_complete(self):
        print("F2 识别完成")
    
    def on_error(self, result):
        print(f"F2 识别错误: {result.message}")
    
    def on_event(self, result):
        sentence = result.get_sentence()
        if sentence and 'text' in sentence:
            text = sentence['text']
            print(f"\r[{ASR_MODEL}] 识别中: {text}", end='')
            
            if result.is_sentence_end(sentence):
                # 累加而不是覆盖
                if self.full_text:
                    self.full_text += text
                else:
                    self.full_text = text
                print(f"\n[{ASR_MODEL}] 识别完成: {self.full_text}")

class ASRCallbackF4:
    def __init__(self):
        self.full_text = ""
        self.is_started = False
        self.manual_stop = False
    
    def on_open(self):
        self.is_started = True
        print("F4 识别已启动")
    
    def on_close(self):
        self.is_started = False
        print("F4 识别已关闭")
    
    def on_complete(self):
        if self.manual_stop and self.full_text:
            print(f"正在调用 AI ({LLM_MODEL})...")
            response = generate_response(self.full_text)
            if response:
                print(f"AI 回答: {response}")
                paste_text(response)
                winsound.Beep(600, 150)
    
    def on_error(self, result):
        print(f"F4 识别错误: {result.message}")
    
    def on_event(self, result):
        sentence = result.get_sentence()
        if sentence and 'text' in sentence:
            text = sentence['text']
            print(f"\r[{ASR_MODEL}] 识别中: {text}", end='')
            
            if result.is_sentence_end(sentence):
                self.full_text = text
                print(f"\n[{ASR_MODEL}] 识别完成: {self.full_text}")

from dashscope.audio.asr import Recognition, RecognitionCallback

callback_f2 = None
callback_f4 = None
recognition_f2 = None
recognition_f4 = None

def audio_callback(indata, frames, time_info, status):
    global is_recording_f2, is_recording_f4, audio_queue_f2, audio_queue_f4
    if status:
        print(status, file=sys.stderr)
    if is_recording_f2:
        audio_queue_f2.append(indata.copy())
    if is_recording_f4:
        audio_queue_f4.append(indata.copy())

def start_global_stream():
    global stream
    if stream is None:
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=audio_callback
        )
        stream.start()

def stop_global_stream():
    global stream
    if stream is not None:
        stream.stop()
        stream.close()
        stream = None

def audio_sender_f2():
    global recognition_f2, callback_f2
    while callback_f2 and callback_f2.is_started:
        if len(audio_queue_f2) > 0:
            data = audio_queue_f2.pop(0)
            audio_bytes = data.tobytes()
            recognition_f2.send_audio_frame(audio_bytes)
        else:
            time.sleep(0.02)
        if stop_event.is_set():
            break

def audio_sender_f4():
    global recognition_f4, callback_f4
    while callback_f4 and callback_f4.is_started:
        if len(audio_queue_f4) > 0:
            data = audio_queue_f4.pop(0)
            audio_bytes = data.tobytes()
            recognition_f4.send_audio_frame(audio_bytes)
        else:
            time.sleep(0.02)
        if stop_event.is_set():
            break

def toggle_f2():
    global is_recording_f2, recognition_f2, callback_f2, audio_queue_f2
    
    if not is_recording_f2:
        is_recording_f2 = True
        audio_queue_f2 = []
        stop_event.clear()
        start_global_stream()
        winsound.Beep(1000, 100)
        print("\nF2 开始录音...")
        
        callback_f2 = ASRCallbackF2()
        recognition_f2 = Recognition(
            model=ASR_MODEL,
            format='pcm',
            sample_rate=SAMPLE_RATE,
            callback=callback_f2
        )
        recognition_f2.start()
        
        sender_thread = threading.Thread(target=audio_sender_f2, daemon=True)
        sender_thread.start()
    else:
        is_recording_f2 = False
        winsound.Beep(800, 100)
        print("\nF2 停止录音...")
        
        if recognition_f2 and callback_f2:
            recognition_f2.stop()
            time.sleep(0.5)
            if callback_f2.full_text:
                paste_text(callback_f2.full_text)
                winsound.Beep(600, 150)
            stop_global_stream()
            recognition_f2 = None
            callback_f2 = None

def toggle_f4():
    global is_recording_f4, recognition_f4, callback_f4, audio_queue_f4
    
    if not is_recording_f4:
        is_recording_f4 = True
        audio_queue_f4 = []
        stop_event.clear()
        start_global_stream()
        winsound.Beep(1000, 100)
        print("\nF4 开始录音...")
        
        callback_f4 = ASRCallbackF4()
        recognition_f4 = Recognition(
            model=ASR_MODEL,
            format='pcm',
            sample_rate=SAMPLE_RATE,
            callback=callback_f4
        )
        recognition_f4.start()
        
        sender_thread = threading.Thread(target=audio_sender_f4, daemon=True)
        sender_thread.start()
    else:
        is_recording_f4 = False
        winsound.Beep(800, 100)
        print("\nF4 停止录音...")
        
        if recognition_f4 and callback_f4:
            callback_f4.manual_stop = True
            recognition_f4.stop()
            time.sleep(1)
            stop_global_stream()
            recognition_f4 = None
            callback_f4 = None

def on_quit(icon, item):
    global recognition_f2, recognition_f4
    if recognition_f2:
        recognition_f2.stop()
    if recognition_f4:
        recognition_f4.stop()
    stop_global_stream()
    icon.stop()
    os._exit(0)

def main():
    keyboard.add_hotkey('f2', toggle_f2)
    keyboard.add_hotkey('f4', toggle_f4)
    
    icon = pystray.Icon(
        "ali_voice_assistant",
        create_icon(),
        "阿里云语音助手",
        menu=pystray.Menu(
            pystray.MenuItem("退出", on_quit)
        )
    )
    
    print("阿里云语音助手已启动")
    print(f"ASR模型: {ASR_MODEL}")
    print(f"大模型: {LLM_MODEL}")
    print("按 F2: 听写模式（按一次开始，说完按一次结束，自动粘贴）")
    print("按 F4: 上帝模式（按一次开始，说完按一次结束，AI 回答）")
    print("右键托盘图标退出")
    
    icon.run()

if __name__ == "__main__":
    main()
