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

# 防止多实例运行
import ctypes

# 使用 Windows 互斥锁防止多实例
try:
    # 定义 Windows API 常量
    ERROR_ALREADY_EXISTS = 183
    
    # 创建互斥锁
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    mutex_name = 'Global\\MagicVoiceMutex'
    
    # 创建互斥锁
    # 参数：
    # 1. lpMutexAttributes - None (默认安全属性)
    # 2. bInitialOwner - True (当前进程拥有)
    # 3. lpName - 互斥锁名称
    mutex = kernel32.CreateMutexW(None, True, mutex_name)
    
    # 检查是否成功创建
    if mutex == 0:
        print(f"创建互斥锁失败，错误代码: {ctypes.get_last_error()}")
    else:
        # 检查是否已有实例
        last_error = ctypes.get_last_error()
        if last_error == ERROR_ALREADY_EXISTS:
            print("MagicVoice 已经在运行中...")
            sys.exit(0)
        
        # 注册退出时释放互斥锁
        import atexit
        def release_mutex():
            try:
                if mutex != 0:
                    kernel32.CloseHandle(mutex)
            except:
                pass
        atexit.register(release_mutex)
except Exception as e:
    print(f"防多实例检查失败: {e}")
    # 继续运行，但可能会有多个实例



try:
    import tomli as tomllib
except ImportError:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        raise ImportError("需要安装 tomli: pip install tomli")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_api_keys():
    secret_file = os.path.join(os.path.dirname(__file__), 'secret.toml')
    asr_api_key = None
    llm_api_key = None
    
    if os.path.exists(secret_file):
        with open(secret_file, 'rb') as f:
            config = tomllib.load(f)
            if 'asr' in config and 'API_KEY' in config['asr']:
                asr_api_key = config['asr']['API_KEY']
            if 'llm' in config and 'API_KEY' in config['llm']:
                llm_api_key = config['llm']['API_KEY']
    
    # 环境变量作为备选
    if not asr_api_key:
        asr_api_key = os.environ.get('ASR_API_KEY') or os.environ.get('MAGICVOICE_API_KEY') or os.environ.get('DASHSCOPE_API_KEY')
    if not llm_api_key:
        llm_api_key = os.environ.get('LLM_API_KEY') or os.environ.get('MAGICVOICE_API_KEY') or os.environ.get('DASHSCOPE_API_KEY')
    
    return asr_api_key, llm_api_key

ASR_API_KEY, LLM_API_KEY = load_api_keys()

if not ASR_API_KEY:
    print("错误: 未找到 ASR API Key，请检查 secret.toml 或环境变量")
    sys.exit(1)
if not LLM_API_KEY:
    print("错误: 未找到 LLM API Key，请检查 secret.toml 或环境变量")
    sys.exit(1)

# 设置 API Key
dashscope.api_key = ASR_API_KEY  # ASR 默认使用
def get_llm_api_key():
    return LLM_API_KEY



SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = np.int16

# 模型配置
ASR_MODELS = ["fun-asr-realtime", "fun-asr-flash-8k-realtime"]
LLM_MODELS = ["qwen3.5-flash", "qwen-flash", "qwen-turbo"]

# 配置文件路径
if getattr(sys, 'frozen', False):
    # 打包后，使用应用所在目录
    CONFIG_FILE = os.path.join(os.path.dirname(sys.executable), 'config.toml')
else:
    # 开发模式，使用当前文件所在目录
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.toml')

# 加载配置
ASR_MODEL = "fun-asr-realtime"
LLM_MODEL = "qwen-turbo"

def load_config():
    global ASR_MODEL, LLM_MODEL
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'rb') as f:
            config = tomllib.load(f)
            if 'asr' in config and 'model' in config['asr']:
                ASR_MODEL = config['asr']['model']
            if 'llm' in config and 'model' in config['llm']:
                LLM_MODEL = config['llm']['model']

def save_config():
    try:
        # 确保目录存在
        config_dir = os.path.dirname(CONFIG_FILE)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # 直接写入TOML格式的文本
        config_content = f"[asr]\nmodel = \"{ASR_MODEL}\"\n\n[llm]\nmodel = \"{LLM_MODEL}\""
        
        # 写入配置文件
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"配置已保存到: {CONFIG_FILE}")
        print(f"保存的配置: {config_content}")
    except Exception as e:
        print(f"保存配置失败: {e}")

# 加载配置
load_config()

SYSTEM_PROMPT = '''你是一个智能语音助手，帮助用户回答问题、完成任务。

请严格遵循以下原则：
1. 回答极其简洁，直接给出核心信息，避免任何冗余和解释
2. 对于事实性问题（如数学计算、日期等），直接给出准确答案
3. 对于列举类问题（如诗词、例子等），只列出3-5个选项，不做任何解释
4. 用中文回答，语言简洁专业
5. 控制回答长度，最多2-3句话，绝不冗长
6. 不要添加任何开场白或结束语
7. 只关注问题本身，不进行任何扩展或追问'''

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
        
        # 使用 LLM API Key
        original_api_key = dashscope.api_key
        dashscope.api_key = get_llm_api_key()
        
        try:
            response = dashscope.Generation.call(
                model=LLM_MODEL,
                messages=messages
            )
        finally:
            # 恢复原来的 API Key
            dashscope.api_key = original_api_key
        
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

def on_toggle_f2(icon, item):
    toggle_f2()

def on_toggle_f4(icon, item):
    toggle_f4()

# 模型选择函数
def on_select_asr_model(icon, item):
    global ASR_MODEL, recognition_f2, recognition_f4, is_recording_f2, is_recording_f4
    
    # 停止任何正在运行的语音识别实例
    if recognition_f2:
        recognition_f2.stop()
        recognition_f2 = None
    if recognition_f4:
        recognition_f4.stop()
        recognition_f4 = None
    
    # 停止音频流
    stop_global_stream()
    
    # 重置录音状态
    is_recording_f2 = False
    is_recording_f4 = False
    
    # 更新模型
    ASR_MODEL = item.text
    print(f"ASR模型已切换为: {ASR_MODEL}")
    
    # 保存配置
    save_config()
    
    # 重启应用以更新菜单
    icon.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)

def on_select_llm_model(icon, item):
    global LLM_MODEL
    LLM_MODEL = item.text
    print(f"LLM模型已切换为: {LLM_MODEL}")
    # 保存配置
    save_config()
    
    # 重启应用以更新菜单
    icon.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)

def create_menu():
    # 创建模型子菜单
    asr_menu_items = []
    for model in ASR_MODELS:
        # 使用闭包来捕获当前的model值
        def create_checked_func(model_name):
            return lambda item: ASR_MODEL == model_name
        asr_menu_items.append(pystray.MenuItem(model, on_select_asr_model, checked=create_checked_func(model)))
    asr_menu = pystray.Menu(*asr_menu_items)
    
    llm_menu_items = []
    for model in LLM_MODELS:
        # 使用闭包来捕获当前的model值
        def create_checked_func(model_name):
            return lambda item: LLM_MODEL == model_name
        llm_menu_items.append(pystray.MenuItem(model, on_select_llm_model, checked=create_checked_func(model)))
    llm_menu = pystray.Menu(*llm_menu_items)
    
    return pystray.Menu(
        pystray.MenuItem("F2: 听写模式", on_toggle_f2),
        pystray.MenuItem("F4: 上帝模式", on_toggle_f4),
        pystray.MenuItem(
            "语音模型",
            asr_menu
        ),
        pystray.MenuItem(
            "大语言模型",
            llm_menu
        ),
        pystray.MenuItem("退出", on_quit)
    )

def main():
    keyboard.add_hotkey('f2', toggle_f2)
    keyboard.add_hotkey('f4', toggle_f4)
    
    icon = pystray.Icon(
        "ali_voice_assistant",
        create_icon(),
        "阿里云语音助手",
        menu=create_menu()
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
