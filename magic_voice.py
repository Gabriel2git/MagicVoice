import os
import sys
import time
import threading
import json

# 核心模块优先导入

# 防止多实例运行
import ctypes

# 配置文件路径
if getattr(sys, 'frozen', False):
    # 打包后，使用应用所在目录
    CONFIG_FILE = os.path.join(os.path.dirname(sys.executable), 'config.toml')
    CONFIG_JSON = os.path.join(os.path.dirname(sys.executable), 'config.json')
else:
    # 开发模式，使用当前文件所在目录
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.toml')
    CONFIG_JSON = os.path.join(os.path.dirname(__file__), 'config.json')

# 加载 TOML 库
try:
    import tomli as tomllib
except ImportError:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        raise ImportError("需要安装 tomli: pip install tomli")

# 使用 Windows 互斥锁防止多实例
try:
    # 定义 Windows API 常量
    ERROR_ALREADY_EXISTS = 183
    
    # 创建互斥锁
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    mutex_name = 'Global\\MagicVoiceMutex_Test'
    
    # 创建互斥锁
    mutex = kernel32.CreateMutexW(None, True, mutex_name)
    
    # 检查是否成功创建
    if mutex == 0:
        print(f"创建互斥锁失败，错误代码: {ctypes.get_last_error()}")
    else:
        # 检查是否已有实例
        last_error = ctypes.get_last_error()
        if last_error == ERROR_ALREADY_EXISTS:
            print("MagicVoice 已经在运行中...")
            # 导入 tkinter 并显示提示窗口
            import tkinter as tk
            from tkinter import messagebox
            
            # 创建一个临时窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            # 显示提示信息
            messagebox.showinfo("提示", "MagicVoice 已经在运行中，请检查系统托盘图标。")
            
            # 退出程序
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

# 配置文件路径
if getattr(sys, 'frozen', False):
    # 打包后，使用应用所在目录
    CONFIG_FILE = os.path.join(os.path.dirname(sys.executable), 'config.toml')
    CONFIG_JSON = os.path.join(os.path.dirname(sys.executable), 'config.json')
else:
    # 开发模式，使用当前文件所在目录
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.toml')
    CONFIG_JSON = os.path.join(os.path.dirname(__file__), 'config.json')

# 加载 TOML 库
try:
    import tomli as tomllib
except ImportError:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        raise ImportError("需要安装 tomli: pip install tomli")

# 保存 API Key 到 config.json
def save_api_key(api_key):
    try:
        # 确保目录存在
        config_dir = os.path.dirname(CONFIG_JSON)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # 写入配置
        config = {
            'DASHSCOPE_API_KEY': api_key
        }
        
        # 写入 config.json
        with open(CONFIG_JSON, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"API Key 已保存到: {CONFIG_JSON}")
        return True
    except Exception as e:
        print(f"保存 API Key 失败: {e}")
        return False

# 加载 API 密钥
def load_api_keys():
    secret_file = os.path.join(os.path.dirname(__file__), 'secret.toml')
    asr_api_key = None
    llm_api_key = None
    
    # 优先从 config.json 读取
    if os.path.exists(CONFIG_JSON):
        try:
            with open(CONFIG_JSON, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'DASHSCOPE_API_KEY' in config:
                    api_key = config['DASHSCOPE_API_KEY']
                    asr_api_key = api_key
                    llm_api_key = api_key
            print("从 config.json 加载 API Key 成功")
        except Exception as e:
            print(f"加载 config.json 失败: {e}")
    
    # 从 secret.toml 读取
    if not asr_api_key or not llm_api_key:
        if os.path.exists(secret_file):
            try:
                with open(secret_file, 'rb') as f:
                    config = tomllib.load(f)
                    if 'asr' in config and 'API_KEY' in config['asr']:
                        asr_api_key = config['asr']['API_KEY']
                    if 'llm' in config and 'API_KEY' in config['llm']:
                        llm_api_key = config['llm']['API_KEY']
                print("从 secret.toml 加载 API Key 成功")
            except Exception as e:
                print(f"加载 secret.toml 失败: {e}")
    
    # 环境变量作为备选
    if not asr_api_key:
        asr_api_key = os.environ.get('ASR_API_KEY') or os.environ.get('MAGICVOICE_API_KEY') or os.environ.get('DASHSCOPE_API_KEY')
        if asr_api_key:
            print("从环境变量加载 ASR API Key 成功")
    if not llm_api_key:
        llm_api_key = os.environ.get('LLM_API_KEY') or os.environ.get('MAGICVOICE_API_KEY') or os.environ.get('DASHSCOPE_API_KEY')
        if llm_api_key:
            print("从环境变量加载 LLM API Key 成功")
    
    return asr_api_key, llm_api_key

ASR_API_KEY, LLM_API_KEY = load_api_keys()

if not ASR_API_KEY:
    print("错误: 未找到 ASR API Key，请检查 secret.toml 或环境变量")
    sys.exit(1)
if not LLM_API_KEY:
    print("错误: 未找到 LLM API Key，请检查 secret.toml 或环境变量")
    sys.exit(1)

# 设置 API Key
def get_llm_api_key():
    return LLM_API_KEY

# 音频配置
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'  # 暂时使用字符串，稍后在需要时再导入 numpy

# 模型配置
ASR_MODELS = ["fun-asr-realtime", "fun-asr-flash-8k-realtime"]
LLM_MODELS = ["qwen-flash", "qwen-turbo"]

# 全局变量
ASR_MODEL = "fun-asr-realtime"
LLM_MODEL = "qwen-turbo"
is_recording_f2 = False
is_recording_f4 = False
audio_queue_f2 = []
audio_queue_f4 = []
# 音频队列大小限制
MAX_QUEUE_SIZE = 1000
stream = None
stop_event = threading.Event()
recognition_f2 = None
recognition_f4 = None
callback_f2 = None
callback_f4 = None
# 线程锁，用于保护全局状态
state_lock = threading.Lock()
# 操作时间戳，用于防抖动
last_f2_time = 0
last_f4_time = 0
# 防抖动时间间隔（毫秒）
DEBOUNCE_INTERVAL = 500
# 热键配置
HOTKEY_F2 = 'f2'
HOTKEY_F4 = 'f4'
HOTKEY_F2_FALLBACK = 'ctrl+shift+f2'
HOTKEY_F4_FALLBACK = 'ctrl+shift+f4'
HOTKEY_SUPPRESS = True
HOTKEY_HANDLES = []
LOG_FILE = os.path.join(os.path.dirname(CONFIG_FILE), 'magic_voice.log')

# 加载配置
def load_config():
    global ASR_MODEL, LLM_MODEL, HOTKEY_F2, HOTKEY_F4
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'rb') as f:
                config = tomllib.load(f)
                if 'asr' in config and 'model' in config['asr']:
                    ASR_MODEL = config['asr']['model']
                if 'llm' in config and 'model' in config['llm']:
                    LLM_MODEL = config['llm']['model']
                if 'hotkey' in config:
                    if 'f2' in config['hotkey']:
                        HOTKEY_F2 = config['hotkey']['f2']
                    if 'f4' in config['hotkey']:
                        HOTKEY_F4 = config['hotkey']['f4']
            print(f"配置加载成功: ASR={ASR_MODEL}, LLM={LLM_MODEL}, F2={HOTKEY_F2}, F4={HOTKEY_F4}")
        except Exception as e:
            print(f"加载配置失败: {e}")

# 保存配置
def save_config():
    try:
        # 确保目录存在
        config_dir = os.path.dirname(CONFIG_FILE)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # 直接写入TOML格式的文本
        config_content = f"[asr]\nmodel = \"{ASR_MODEL}\"\n\n[llm]\nmodel = \"{LLM_MODEL}\"\n\n[hotkey]\nf2 = \"{HOTKEY_F2}\"\nf4 = \"{HOTKEY_F4}\""
        
        # 写入配置文件
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"配置已保存到: {CONFIG_FILE}")
    except Exception as e:
        print(f"保存配置失败: {e}")

def write_runtime_log(message):
    try:
        log_dir = os.path.dirname(LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} {message}\n")
    except Exception:
        # 日志写入失败不应影响主流程
        pass

def safe_hotkey_call(name, callback):
    try:
        callback()
    except Exception as e:
        write_runtime_log(f"hotkey {name} callback failed: {e}")
        print(f"热键 {name} 执行失败: {e}")

def normalize_hotkey(value):
    if not value:
        return ''
    return value.strip().lower()

def build_hotkey_candidates(primary, fallback):
    candidates = []
    for hotkey in (primary, fallback):
        normalized = normalize_hotkey(hotkey)
        if normalized and normalized not in candidates:
            candidates.append(normalized)
    return candidates

def clear_registered_hotkeys():
    global HOTKEY_HANDLES
    if not HOTKEY_HANDLES:
        return
    try:
        import keyboard
        for handle in HOTKEY_HANDLES:
            try:
                keyboard.remove_hotkey(handle)
            except Exception:
                pass
    except Exception:
        pass
    HOTKEY_HANDLES = []

def register_hotkeys():
    global HOTKEY_HANDLES
    import keyboard

    clear_registered_hotkeys()
    HOTKEY_HANDLES = []
    registered = []
    failures = []

    hotkey_specs = [
        ("F2", HOTKEY_F2, HOTKEY_F2_FALLBACK, toggle_f2),
        ("F4", HOTKEY_F4, HOTKEY_F4_FALLBACK, toggle_f4),
    ]

    for name, primary, fallback, callback in hotkey_specs:
        for hotkey in build_hotkey_candidates(primary, fallback):
            try:
                handle = keyboard.add_hotkey(
                    hotkey,
                    lambda n=name, cb=callback: safe_hotkey_call(n, cb),
                    suppress=HOTKEY_SUPPRESS
                )
                HOTKEY_HANDLES.append(handle)
                registered.append(f"{name}={hotkey}")
            except Exception as e:
                failures.append(f"{name}={hotkey}: {e}")

    if not registered:
        raise RuntimeError("未成功注册任何热键")

    if failures:
        write_runtime_log("partial hotkey registration failures: " + " | ".join(failures))
        print("部分热键注册失败，请检查日志文件。")

    print("热键注册成功: " + ", ".join(registered))
    write_runtime_log("hotkeys registered: " + ", ".join(registered))

# 加载配置
load_config()

# 创建设置窗口
def create_settings_window():
    import tkinter as tk
    from tkinter import messagebox
    
    def on_save():
        api_key = entry.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入 API Key")
            return
        
        if save_api_key(api_key):
            # 更新全局 API Key
            global ASR_API_KEY, LLM_API_KEY
            ASR_API_KEY = api_key
            LLM_API_KEY = api_key
            import dashscope
            dashscope.api_key = api_key
            
            messagebox.showinfo("成功", "API Key 保存成功，程序将继续运行")
            root.destroy()
        else:
            messagebox.showerror("错误", "保存 API Key 失败")
    
    def on_cancel():
        root.destroy()
        # 如果没有 API Key，退出程序
        if not ASR_API_KEY or not LLM_API_KEY:
            print("未输入 API Key，程序退出")
            os._exit(0)
    
    def test_api_key():
        api_key = entry.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入 API Key")
            return
        
        # 测试 API Key 是否有效
        import dashscope
        original_api_key = dashscope.api_key
        dashscope.api_key = api_key
        
        try:
            # 发送一个简单的请求来测试 API Key
            test_result = dashscope.Generation.call(
                model="qwen-turbo",
                messages=[{"role": "user", "content": "测试"}],
                max_tokens=1
            )
            
            if test_result.status_code == 200:
                messagebox.showinfo("成功", "API Key 有效")
            else:
                messagebox.showerror("错误", f"API Key 无效: {test_result.message}")
        except Exception as e:
            messagebox.showerror("错误", f"API Key 测试失败: {e}")
        finally:
            # 恢复原来的 API Key
            dashscope.api_key = original_api_key
    
    root = tk.Tk()
    root.title("Magic Voice 设置")
    root.geometry("400x250")
    root.resizable(False, False)
    
    # 居中显示
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 400) // 2
    y = (screen_height - 250) // 2
    root.geometry(f"400x250+{x}+{y}")
    
    # 创建框架
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # 说明文本
    label = tk.Label(frame, text="请输入您的阿里云百炼 API Key。若无，请前往阿里云官网免费获取。", wraplength=360, justify=tk.LEFT)
    label.pack(pady=(0, 15))
    
    # 输入框
    entry = tk.Entry(frame, width=40, show="*")
    entry.pack(pady=(0, 10))
    
    # 显示当前 API Key（部分隐藏）
    if ASR_API_KEY:
        hidden_key = ASR_API_KEY[:4] + "*" * (len(ASR_API_KEY) - 8) + ASR_API_KEY[-4:]
        current_key_label = tk.Label(frame, text=f"当前 API Key: {hidden_key}", fg="gray")
        current_key_label.pack(pady=(0, 15))
    
    # 按钮框架
    button_frame = tk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=(10, 0))
    
    # 测试按钮
    test_button = tk.Button(button_frame, text="测试 API Key", command=test_api_key, width=12)
    test_button.pack(side=tk.LEFT, padx=(0, 10))
    
    # 保存按钮
    save_button = tk.Button(button_frame, text="保存并启动", command=on_save, width=12)
    save_button.pack(side=tk.LEFT, padx=(0, 10))
    
    # 取消按钮
    cancel_button = tk.Button(button_frame, text="取消", command=on_cancel, width=12)
    cancel_button.pack(side=tk.LEFT)
    
    # 运行窗口
    root.mainloop()

# AI 提示词
SYSTEM_PROMPT = '''你是一个智能语音助手，帮助用户回答问题、完成任务。

请严格遵循以下原则：
1. 回答极其简洁，直接给出核心信息，避免任何冗余和解释
2. 对于事实性问题（如数学计算、日期等），直接给出准确答案
3. 对于列举类问题（如诗词、例子等），只列出3-5个选项，不做任何解释
4. 用中文回答，语言简洁专业
5. 控制回答长度，最多2-3句话，绝不冗长
6. 不要添加任何开场白或结束语
7. 只关注问题本身，不进行任何扩展或追问'''

# 创建托盘图标
def create_icon():
    from PIL import Image, ImageDraw
    width, height = 64, 64
    image = Image.new('RGB', (width, height), color=(66, 133, 244))
    dc = ImageDraw.Draw(image)
    dc.ellipse([16, 16, 48, 48], fill=(255, 255, 255))
    dc.ellipse([24, 20, 40, 44], fill=(66, 133, 244))
    return image

# 粘贴文本
def paste_text(text):
    import pyperclip
    import keyboard
    old = pyperclip.paste()
    pyperclip.copy(text)
    keyboard.send('ctrl+v')
    time.sleep(0.1)
    pyperclip.copy(old)

# 生成 AI 响应
def generate_response(text):
    import dashscope
    try:
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        messages.append({'role': 'user', 'content': text})
        
        # 使用 LLM API Key
        original_api_key = dashscope.api_key
        dashscope.api_key = get_llm_api_key()
        
        print(f"正在调用 LLM 模型: {LLM_MODEL}")
        print(f"请求内容: {text}")
        
        try:
            # 设置超时时间为30秒
            import threading
            
            result = [None]
            exception = [None]
            
            def call_model():
                try:
                    # 为不同模型设置不同的参数
                    if LLM_MODEL in ["qwen3.5-flash", "qwen-flash"]:
                        # Flash 模型可能需要不同的参数
                        result[0] = dashscope.Generation.call(
                            model=LLM_MODEL,
                            messages=messages,
                            max_tokens=1024,
                            temperature=0.7,
                            top_p=0.9
                        )
                    else:
                        # 其他模型使用默认参数
                        result[0] = dashscope.Generation.call(
                            model=LLM_MODEL,
                            messages=messages
                        )
                except Exception as e:
                    exception[0] = e
            
            # 创建并启动线程
            thread = threading.Thread(target=call_model)
            thread.daemon = True
            thread.start()
            
            # 等待线程完成，最多等待30秒
            thread.join(30)
            
            # 检查线程是否超时
            if thread.is_alive():
                print("API 调用超时，请检查网络连接后重试")
                return None
            
            # 检查是否有异常
            if exception[0]:
                raise exception[0]
            
            response = result[0]
            
            print(f"响应状态码: {response.status_code}")
            
            # 打印完整的响应对象，以便更好地诊断问题
            print(f"完整响应对象: {response}")
            
            if hasattr(response, 'output') and response.output:
                if hasattr(response.output, 'text'):
                    print(f"响应内容: {response.output.text}")
                else:
                    print(f"响应输出对象: {response.output}")
                    print(f"响应输出属性: {dir(response.output)}")
            else:
                print(f"响应对象: {response}")
                print(f"响应属性: {dir(response)}")
                if hasattr(response, 'message'):
                    print(f"错误信息: {response.message}")
                    # 检查是否是API密钥无效或过期的错误
                    if 'API key' in response.message or 'api_key' in response.message:
                        print("提示: API密钥可能无效或过期，请检查secret.toml文件或环境变量")
                if hasattr(response, 'code'):
                    print(f"错误代码: {response.code}")
                if hasattr(response, 'request_id'):
                    print(f"请求ID: {response.request_id}")
        finally:
            # 恢复原来的 API Key
            dashscope.api_key = original_api_key
        
        if response.status_code == 200 and hasattr(response, 'output') and hasattr(response.output, 'text'):
            return response.output.text
        else:
            print(f"响应失败: 状态码={response.status_code}")
            return None
    except Exception as e:
        print(f"AI 生成错误: {e}")
        # 检查是否是网络连接错误
        if 'network' in str(e).lower() or 'connect' in str(e).lower():
            print("提示: 网络连接失败，请检查网络连接")
        # 检查是否是API密钥错误
        elif 'API key' in str(e) or 'api_key' in str(e):
            print("提示: API密钥可能无效或过期，请检查secret.toml文件或环境变量")
        import traceback
        traceback.print_exc()
        return None

# F2 回调类
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

# F4 回调类
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
        print(f"F4 on_complete 被调用, full_text: {self.full_text[:50] if self.full_text else '空'}")
        if self.full_text:
            print(f"正在调用 AI ({LLM_MODEL})...")
            response = generate_response(self.full_text)
            if response:
                print(f"AI 回答: {response}")
                paste_text(response)
                import winsound
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

# 音频回调
def audio_callback(indata, frames, time_info, status):
    global is_recording_f2, is_recording_f4, audio_queue_f2, audio_queue_f4, MAX_QUEUE_SIZE
    if status:
        print(status, file=sys.stderr)
    if is_recording_f2:
        audio_queue_f2.append(indata.copy())
        # 限制队列大小，防止内存溢出
        if len(audio_queue_f2) > MAX_QUEUE_SIZE:
            audio_queue_f2.pop(0)  # 丢弃最旧的数据
    if is_recording_f4:
        audio_queue_f4.append(indata.copy())
        # 限制队列大小，防止内存溢出
        if len(audio_queue_f4) > MAX_QUEUE_SIZE:
            audio_queue_f4.pop(0)  # 丢弃最旧的数据

# 启动全局音频流
def start_global_stream():
    global stream
    if stream is None:
        try:
            import sounddevice as sd
            stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype=DTYPE,
                callback=audio_callback
            )
            stream.start()
        except Exception as e:
            print(f"启动音频流失败: {e}")
            print("请检查音频设备是否可用")
            stream = None

# 停止全局音频流
def stop_global_stream():
    global stream
    if stream is not None:
        try:
            stream.stop()
            stream.close()
        except Exception as e:
            print(f"停止音频流失败: {e}")
        finally:
            stream = None

# F2 音频发送线程
def audio_sender_f2():
    global recognition_f2, callback_f2
    while callback_f2 and callback_f2.is_started:
        try:
            if len(audio_queue_f2) > 0:
                data = audio_queue_f2.pop(0)
                audio_bytes = data.tobytes()
                recognition_f2.send_audio_frame(audio_bytes)
            else:
                time.sleep(0.02)
            if stop_event.is_set():
                break
        except Exception as e:
            print(f"F2 音频发送线程异常: {e}")
            break

# F4 音频发送线程
def audio_sender_f4():
    global recognition_f4, callback_f4
    while callback_f4 and callback_f4.is_started:
        try:
            if len(audio_queue_f4) > 0:
                data = audio_queue_f4.pop(0)
                audio_bytes = data.tobytes()
                recognition_f4.send_audio_frame(audio_bytes)
            else:
                time.sleep(0.02)
            if stop_event.is_set():
                break
        except Exception as e:
            print(f"F4 音频发送线程异常: {e}")
            break

# F2 模式切换
def toggle_f2():
    global is_recording_f2, recognition_f2, callback_f2, audio_queue_f2, state_lock, last_f2_time, DEBOUNCE_INTERVAL
    
    # 防抖动处理
    current_time = time.time() * 1000  # 转换为毫秒
    if current_time - last_f2_time < DEBOUNCE_INTERVAL:
        print("操作过于频繁，请稍后再试")
        return
    last_f2_time = current_time
    
    with state_lock:
        if not is_recording_f2:
            try:
                is_recording_f2 = True
                audio_queue_f2 = []
                stop_event.clear()
                start_global_stream()
                import winsound
                winsound.Beep(1000, 100)
                print("\nF2 开始录音...")
                
                callback_f2 = ASRCallbackF2()
                from dashscope.audio.asr import Recognition
                recognition_f2 = Recognition(
                    model=ASR_MODEL,
                    format='pcm',
                    sample_rate=SAMPLE_RATE,
                    callback=callback_f2
                )
                recognition_f2.start()
                
                sender_thread = threading.Thread(target=audio_sender_f2, daemon=True)
                sender_thread.start()
            except Exception as e:
                is_recording_f2 = False
                recognition_f2 = None
                callback_f2 = None
                stop_global_stream()
                write_runtime_log(f"toggle_f2 start failed: {e}")
                print(f"F2 启动失败: {e}")
                try:
                    import winsound
                    winsound.Beep(400, 300)
                except Exception:
                    pass
        else:
            is_recording_f2 = False
            import winsound
            winsound.Beep(800, 100)
            print("\nF2 停止录音...")
            
            if recognition_f2 and callback_f2:
                # 使用超时机制停止识别
                stop_result = [False]
                def stop_recognition():
                    try:
                        recognition_f2.stop()
                        stop_result[0] = True
                    except Exception as e:
                        print(f"停止识别失败: {e}")
                
                stop_thread = threading.Thread(target=stop_recognition, daemon=True)
                stop_thread.start()
                stop_thread.join(timeout=5)  # 5秒超时
                
                if not stop_result[0]:
                    print("识别停止超时，强制结束...")
                    import winsound
                    winsound.Beep(400, 500)  # 错误提示音
                
                time.sleep(0.5)
                
                # 处理识别结果
                if callback_f2 and callback_f2.full_text:
                    text = callback_f2.full_text
                    print(f"F2识别结果: {text[:50]}...")
                    paste_text(text)
                    import winsound
                    winsound.Beep(600, 150)
                else:
                    print("F2未识别到文本")
                    import winsound
                    winsound.Beep(400, 200)  # 提示音表示未识别
                
                stop_global_stream()
                recognition_f2 = None
                callback_f2 = None

# F4 模式切换
def toggle_f4():
    global is_recording_f4, recognition_f4, callback_f4, audio_queue_f4, state_lock, last_f4_time, DEBOUNCE_INTERVAL
    
    # 防抖动处理
    current_time = time.time() * 1000  # 转换为毫秒
    if current_time - last_f4_time < DEBOUNCE_INTERVAL:
        print("操作过于频繁，请稍后再试")
        return
    last_f4_time = current_time
    
    with state_lock:
        if not is_recording_f4:
            is_recording_f4 = True
            audio_queue_f4 = []
            stop_event.clear()
            start_global_stream()
            import winsound
            winsound.Beep(1000, 100)
            print("\nF4 开始录音...")
            
            callback_f4 = ASRCallbackF4()
            from dashscope.audio.asr import Recognition
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
            import winsound
            winsound.Beep(800, 100)
            print("\nF4 停止录音...")
            
            if recognition_f4 and callback_f4:
                callback_f4.manual_stop = True
                
                # 使用超时机制停止识别
                stop_result = [False]
                def stop_recognition():
                    try:
                        recognition_f4.stop()
                        stop_result[0] = True
                    except Exception as e:
                        print(f"停止识别失败: {e}")
                
                stop_thread = threading.Thread(target=stop_recognition, daemon=True)
                stop_thread.start()
                stop_thread.join(timeout=5)  # 5秒超时
                
                if not stop_result[0]:
                    print("识别停止超时，强制结束...")
                    import winsound
                    winsound.Beep(400, 500)  # 错误提示音
                
                time.sleep(1)
                
                # 如果on_complete没有被调用，手动处理
                if callback_f4 and callback_f4.full_text:
                    print(f"手动处理F4识别结果: {callback_f4.full_text[:50]}...")
                    print(f"正在调用 AI ({LLM_MODEL})...")
                    response = generate_response(callback_f4.full_text)
                    if response:
                        print(f"AI 回答: {response}")
                        paste_text(response)
                        import winsound
                        winsound.Beep(600, 150)
                
                stop_global_stream()
                
                recognition_f4 = None
                callback_f4 = None

# 退出函数
def on_quit(icon, item):
    global recognition_f2, recognition_f4
    if recognition_f2:
        recognition_f2.stop()
    if recognition_f4:
        recognition_f4.stop()
    clear_registered_hotkeys()
    stop_global_stream()
    icon.stop()
    os._exit(0)

# 菜单 F2 切换
def on_toggle_f2(icon, item):
    toggle_f2()

# 菜单 F4 切换
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

# 模型选择函数
def on_select_llm_model(icon, item):
    global LLM_MODEL
    LLM_MODEL = item.text
    print(f"LLM模型已切换为: {LLM_MODEL}")
    # 保存配置
    save_config()



# 测试不同的LLM模型
def test_llm_models():
    test_text = "一加一等于几？"
    
    # 测试 qwen-turbo
    global LLM_MODEL
    original_model = LLM_MODEL
    
    print("\n=== 测试 qwen-turbo ===")
    LLM_MODEL = "qwen-turbo"
    response = generate_response(test_text)
    print(f"响应: {response}")
    
    print("\n=== 测试 qwen-flash ===")
    LLM_MODEL = "qwen-flash"
    response = generate_response(test_text)
    print(f"响应: {response}")
    
    # 恢复原来的模型
    LLM_MODEL = original_model

# 菜单设置选项

def on_settings(icon, item):
    create_settings_window()

# 创建菜单
def create_menu():
    import pystray
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
        pystray.MenuItem("设置", on_settings),
        pystray.MenuItem("退出", on_quit)
    )

# 主函数
def main():
    global ASR_API_KEY, LLM_API_KEY
    # 检查是否存在 config.json 文件
    if not os.path.exists(CONFIG_JSON):
        print("未找到 config.json 文件，弹出设置窗口...")
        create_settings_window()
        # 重新加载 API Key
        ASR_API_KEY, LLM_API_KEY = load_api_keys()
        if not ASR_API_KEY or not LLM_API_KEY:
            print("仍然没有有效的 API Key，程序退出")
            return
        # 更新 dashscope.api_key
        import dashscope
        dashscope.api_key = ASR_API_KEY
    else:
        print("从 config.json 加载配置成功")
        # 设置 dashscope.api_key
        import dashscope
        dashscope.api_key = ASR_API_KEY
    
    # 提前创建托盘图标，让用户尽快看到应用程序已启动
    import pystray
    icon = pystray.Icon(
        "magic_voice",
        create_icon(),
        "Magic Voice",
        menu=create_menu()
    )
    
    # 打印启动信息
    print("Magic Voice 已启动")
    print(f"ASR模型: {ASR_MODEL}")
    print(f"大模型: {LLM_MODEL}")
    print(f"按 {HOTKEY_F2}: 听写模式（按一次开始，说完按一次结束，自动粘贴）")
    print(f"按 {HOTKEY_F4}: 上帝模式（按一次开始，说完按一次结束，AI 回答）")
    print(f"备用热键: F2={HOTKEY_F2_FALLBACK}, F4={HOTKEY_F4_FALLBACK}")
    print("右键托盘图标退出")
    
    # 注册热键（放在托盘图标创建后，因为这可能需要一些时间）
    try:
        register_hotkeys()
    except Exception as e:
        print(f"热键注册失败: {e}")
        write_runtime_log(f"hotkey register failed: {e}")
        print("请检查热键是否与其他应用冲突")
    
    # 运行图标
    icon.run()

if __name__ == "__main__":
    main()
