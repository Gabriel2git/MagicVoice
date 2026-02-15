# MagicVoice

Windows 语音转文字工具，基于阿里云 API。

## 功能特性

- **F2 键**：实时语音转文字模式，结束时自动粘贴
- **F4 键**：语音转文字 + AI 回答模式，AI 回答自动粘贴
- **系统托盘集成**：右键托盘图标退出程序
- **实时流式识别**：支持 fun-asr-realtime 模型，低延迟识别

## 安装使用

### 方式一：使用打包好的 exe（推荐）

1. 下载最新发布版本的 `MagicVoice.zip`
2. 解压到任意目录
3. 复制 `secret.toml.template` 为 `secret.toml`
4. 编辑 `secret.toml`，填写你的阿里云 API Key
5. 双击运行 `MagicVoice.exe`

### 方式二：从源代码运行

```bash
# 克隆仓库
git clone https://github.com/Gabriel2git/MagicVoice.git
cd MagicVoice

# 创建虚拟环境
python -m venv .venv

# 激活环境
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python ali_voice_assistant.py
```

## 配置说明

### 获取阿里云 API Key

1. 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
2. 登录后创建 API Key
3. 将 API Key 填入 `secret.toml` 文件

### 模型选择

编辑 `ali_voice_assistant.py` 中的 ASR_MODEL 和 LLM_MODEL 变量：

- ASR 模型：`fun-asr-realtime`、`fun-asr`、`qwen3-asr-flash`
- LLM 模型：`qwen-turbo`、`qwen-plus` 等

## 打包 exe

```bash
pyinstaller --onefile --noconsole --name "MagicVoice" ali_voice_assistant.py
```

打包后的文件在 `dist/MagicVoice.exe`

## 热键说明

| 按键 | 功能 |
|------|------|
| F2 | 听写模式（按一次开始，再按一次结束） |
| F4 | 上帝模式（转录 + AI 回答） |

## 注意事项

- 阿里云 API 是付费服务，请合理控制使用量
- 支持 Windows 10/11 64 位系统
- 首次运行可能需要安装 Visual C++ Redistributable
- 程序会在系统托盘运行，右键图标可退出

## 项目结构

```
MagicVoice/
├── ali_voice_assistant.py   # 主程序
├── secret.toml.template     # API Key 模板
├── requirements.txt          # 依赖列表
├── .gitignore               # Git 忽略文件
└── README.md                # 说明文档
```

## 依赖

- dashscope - 阿里云 API SDK
- sounddevice - 音频采集
- keyboard - 热键监听
- pyperclip - 剪贴板操作
- pystray - 系统托盘
- numpy - 数值计算

## License

MIT License
