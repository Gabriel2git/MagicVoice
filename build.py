import os
import sys
import shutil

# 构建目录
BUILD_DIR = 'E:\\TraeFile\\magic-voice\\dist'

# 清理之前的构建目录
if os.path.exists(BUILD_DIR):
    shutil.rmtree(BUILD_DIR)
if os.path.exists('build'):
    shutil.rmtree('build')

# 安装依赖
print("安装依赖...")
os.system('pip install --upgrade pip')
os.system('pip install dashscope sounddevice keyboard pyperclip pystray pillow numpy tomli')

# 打包命令
print("开始打包...")
cmd = [
    'pyinstaller',
    '--name=MagicVoice',
    '--onefile',
    '--windowed',
    '--collect-all=idna',
    '--collect-all=requests',
    '--collect-all=dashscope',
    f'--distpath={BUILD_DIR}',
    'magic_voice.py'
]

# 执行打包命令
result = os.system(' '.join(cmd))

if result == 0:
    print("打包成功！")
    print(f"可执行文件位置: {BUILD_DIR}/MagicVoice.exe")
    
    # 复制配置文件到dist目录
    if not os.path.exists(os.path.join(BUILD_DIR, 'secret.toml')):
        if os.path.exists('secret.toml'):
            shutil.copy('secret.toml', BUILD_DIR)
            print(f"已复制 secret.toml 到 {BUILD_DIR} 目录")
        else:
            print("警告: secret.toml 文件不存在，请手动创建")
else:
    print("打包失败！")
    sys.exit(1)
