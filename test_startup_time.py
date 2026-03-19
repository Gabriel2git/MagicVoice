import time
import subprocess
import sys

# 测试程序启动时间
def test_startup_time():
    start_time = time.time()
    print(f"开始测试启动时间: {start_time}")
    
    # 启动程序
    process = subprocess.Popen([sys.executable, 'magic_voice.py'])
    
    # 等待 3 秒，然后终止程序
    time.sleep(3)
    process.terminate()
    
    end_time = time.time()
    startup_time = end_time - start_time
    print(f"启动时间: {startup_time:.2f} 秒")
    
    return startup_time

if __name__ == "__main__":
    test_startup_time()