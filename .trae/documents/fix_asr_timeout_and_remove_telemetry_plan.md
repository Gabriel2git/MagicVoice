# MagicVoice ASR超时修复与遥测功能移除计划

## 问题分析

### 当前问题
1. **F2语音图标不消失**：按下F2开始录音后，再次按下F2时语音图标不会消失
2. **ASR识别内容不返回**：语音识别完成后没有返回识别内容
3. **API延迟问题**：API调用可能超时，导致程序卡住无法退出
4. **需要移除遥测功能**：用户不再需要PostHog遥测功能

### 根本原因推测
- ASR API调用可能阻塞主线程，导致UI无法更新
- 没有设置API调用超时机制
- 语音识别回调处理可能存在问题
- 遥测代码增加了不必要的复杂性和依赖

## 解决方案

### 任务1：移除遥测功能相关代码
**优先级**: P0
**依赖**: 无
**描述**:
- 移除posthog模块导入
- 移除所有posthog.capture调用
- 移除UUID生成和存储逻辑（保留config.json中的API Key功能）
- 移除遥测初始化代码
- 清理相关调试输出

**成功标准**:
- 代码中不再包含任何posthog相关代码
- 程序启动不再显示遥测相关信息
- config.json仍然保留API Key存储功能

**测试要求**:
- `programmatic` TR-1.1: 程序能正常启动，不显示遥测信息
- `programmatic` TR-1.2: config.json仍然能正常读取和保存API Key
- `human-judgment` TR-1.3: 代码简洁，无冗余遥测代码

---

### 任务2：修复ASR API超时问题
**优先级**: P0
**依赖**: 任务1
**描述**:
- 为ASR API调用添加5秒超时机制
- 使用线程或异步方式调用API，避免阻塞主线程
- 超时后强制停止识别，显示错误提示
- 确保语音图标在超时后能正确消失
- 确保程序在超时后能正常响应退出操作

**成功标准**:
- ASR API调用超过5秒自动超时
- 超时后显示用户友好的错误提示
- 语音图标在超时后能正确消失
- 程序在超时后仍能正常响应F2/F4热键

**测试要求**:
- `programmatic` TR-2.1: API调用超过5秒自动超时
- `programmatic` TR-2.2: 超时后语音图标正确消失
- `programmatic` TR-2.3: 超时后程序能正常响应热键
- `human-judgment` TR-2.4: 错误提示清晰友好

---

### 任务3：修复F2语音图标状态问题
**优先级**: P0
**依赖**: 任务2
**描述**:
- 检查toggle_f2函数的状态管理逻辑
- 确保语音识别完成后正确更新UI状态
- 修复语音图标显示/隐藏逻辑
- 确保识别结果能正确返回并粘贴

**成功标准**:
- 按下F2开始录音，语音图标显示
- 再次按下F2停止录音，语音图标消失
- 识别结果正确返回并自动粘贴
- 状态转换清晰可靠

**测试要求**:
- `programmatic` TR-3.1: F2开始录音时语音图标显示
- `programmatic` TR-3.2: F2停止录音时语音图标消失
- `programmatic` TR-3.3: 识别结果正确粘贴到光标位置
- `human-judgment` TR-3.4: 状态转换流畅自然

---

### 任务4：全方位功能测试
**优先级**: P1
**依赖**: 任务3
**描述**:
- 测试F2听写模式全流程
- 测试F4上帝模式全流程
- 测试API超时场景
- 测试正常识别场景
- 测试快速连续按键场景
- 测试程序退出功能

**成功标准**:
- F2模式在各种场景下都能正常工作
- F4模式在各种场景下都能正常工作
- API超时后能正确恢复
- 程序能正常退出

**测试要求**:
- `programmatic` TR-4.1: F2模式正常识别并粘贴
- `programmatic` TR-4.2: F4模式正常识别并粘贴AI回复
- `programmatic` TR-4.3: API超时后程序能继续正常使用
- `programmatic` TR-4.4: 程序能正常退出
- `human-judgment` TR-4.5: 用户体验流畅无卡顿

---

### 任务5：打包发布
**优先级**: P1
**依赖**: 任务4
**描述**:
- 运行build.py打包程序
- 验证打包后的exe能正常运行
- 测试打包版本的功能完整性

**成功标准**:
- 打包成功，无错误
- 打包后的exe能正常启动
- 打包版本功能完整

**测试要求**:
- `programmatic` TR-5.1: 打包过程无错误
- `programmatic` TR-5.2: 打包后的exe能正常启动
- `programmatic` TR-5.3: 打包版本功能完整

## 技术细节

### ASR超时实现方案
```python
# 使用线程实现超时控制
def recognition_with_timeout():
    result = [None]
    def do_recognition():
        result[0] = recognition.start()
    
    thread = threading.Thread(target=do_recognition)
    thread.daemon = True
    thread.start()
    thread.join(timeout=5)  # 5秒超时
    
    if thread.is_alive():
        # 超时处理
        recognition.stop()
        show_error("识别超时，请重试")
        return None
    return result[0]
```

### 状态管理优化
- 使用明确的标志位管理录音状态
- 确保状态转换的原子性
- 添加状态日志便于调试

### 遥测移除清单
- [ ] 移除 `import posthog`
- [ ] 移除 `import uuid`（如果仅用于遥测）
- [ ] 移除 `USER_ID` 全局变量
- [ ] 移除 `posthog.api_key` 和 `posthog.host` 设置
- [ ] 移除所有 `posthog.capture()` 调用
- [ ] 移除UUID生成逻辑
- [ ] 保留 `save_api_key()` 但移除user_id参数
- [ ] 保留 `load_api_keys()` 但移除user_id返回值
- [ ] 清理遥测相关调试输出

## 预期结果
- 程序启动更快（无遥测初始化）
- 代码更简洁（移除遥测代码）
- ASR识别更稳定（有超时保护）
- 用户体验更流畅（状态管理优化）
- 程序可靠性提高（异常处理完善）