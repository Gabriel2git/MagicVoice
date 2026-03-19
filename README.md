# MagicVoice

Windows 语音转文字工具，基于阿里云 API，支持实时语音识别和 AI 智能回答。

## 功能特性

- **F2 键**：实时语音转文字模式，结束时自动粘贴
- **F4 键**：语音转文字 + AI 回答模式，AI 回答自动粘贴
- **系统托盘集成**：右键托盘图标访问功能菜单
- **实时流式识别**：支持 fun-asr-realtime 模型，低延迟识别
- **API 密钥持久化**：只需输入一次 API Key，下次自动加载
- **防止多实例运行**：重复启动时会弹出提示窗口
- **启动速度优化**：快速启动，减少等待时间
- **设置窗口**：图形化界面配置 API Key
- **模型选择**：支持多种 ASR 和 LLM 模型
- **热键配置**：可自定义热键（通过配置文件）

## 安装使用

### 方式一：使用打包好的 exe（推荐）

1. 下载最新发布版本的 `MagicVoice.zip`
2. 解压到任意目录
3. 双击运行 `MagicVoice.exe`
4. 首次运行时会弹出设置窗口，输入你的阿里云 API Key
5. API Key 会自动保存到 `config.json` 文件中，下次启动无需重复输入

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
python magic_voice.py
```

## 配置说明

### 获取阿里云 API Key

1. 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
2. 登录后创建 API Key
3. 首次运行程序时，在弹出的设置窗口中输入 API Key
4. API Key 会自动保存到 `config.json` 文件中
5. 如需修改 API Key，可右键点击系统托盘图标，选择「设置」

### 模型选择

右键点击系统托盘图标，选择相应的模型：

- **语音模型**：`fun-asr-realtime`、`fun-asr-flash-8k-realtime`
- **大语言模型**：`qwen-flash`、`qwen-turbo`

### 热键配置

编辑 `config.toml` 文件中的热键配置：

```toml
[hotkey]
f2 = "ctrl+shift+f2"  # 听写模式热键（建议使用组合键，降低冲突）
f4 = "ctrl+shift+f4"  # 上帝模式热键（建议使用组合键，降低冲突）
```

## 打包 exe

使用项目根目录下的 `build.py` 脚本进行打包：

```bash
python build.py
```

打包后的文件在 `dist/MagicVoice.exe`

## 热键说明

| 按键 | 功能 |
|------|------|
| F2 | 听写模式（按一次开始，再按一次结束，自动粘贴） |
| F4 | 上帝模式（按一次开始，再按一次结束，AI 回答自动粘贴） |

## 注意事项

- 阿里云 API 是付费服务，请合理控制使用量
- 支持 Windows 10/11 64 位系统
- 首次运行可能需要安装 Visual C++ Redistributable
- 程序会在系统托盘运行，右键图标可访问功能菜单
- 程序会自动防止多实例运行，避免冲突
- 若遇到音频设备问题，请检查麦克风权限
- 若热键偶发不响应，优先改用组合键（如 `ctrl+shift+f2`），并查看 `magic_voice.log` 排查注册/回调异常

## 项目结构

```
MagicVoice/
├── magic_voice.py           # 主程序
├── ali_voice_assistant.py   # 辅助模块
├── build.py                 # 打包脚本
├── magic_voice.ico          # 应用图标
├── secret.toml.template     # API Key 模板（备用）
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
- tomli - TOML 文件解析
- Pillow - 图标处理

## License

MIT License
