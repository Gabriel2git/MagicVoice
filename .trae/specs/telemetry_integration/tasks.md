# MagicVoice 遥测功能 - 实现计划

## [x] Task 1: 安装 PostHog Python SDK
- **Priority**: P0
- **Depends On**: None
- **Description**: 在项目环境中安装 PostHog Python SDK
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 执行 `pip install posthog` 命令成功
  - `programmatic` TR-1.2: 导入 posthog 模块无错误
- **Notes**: 确保安装最新版本的 PostHog SDK

## [x] Task 2: 修改配置加载逻辑，添加 UUID 生成和存储
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 修改 load_api_keys() 函数，添加 UUID 生成逻辑
  - 如果 config.json 中没有 user_id，则自动生成 UUID4
  - 将 UUID 与 API Key 一起存入 config.json
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-2.1: 首次运行时自动生成 UUID 并保存到 config.json
  - `programmatic` TR-2.2: 后续运行时加载已存在的 UUID
- **Notes**: 确保 UUID 生成逻辑不影响现有功能

## [x] Task 3: 集成 PostHog 初始化
- **Priority**: P0
- **Depends On**: Task 2
- **Description**:
  - 在代码全局引入 posthog
  - 设置 posthog.project_api_key 和 posthog.host
  - 在程序启动时初始化 PostHog
  - 打印 'Telemetry initialized successfully.'
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-3.1: PostHog 初始化成功
  - `programmatic` TR-3.2: 控制台打印 'Telemetry initialized successfully.'
- **Notes**: 使用用户提供的 PostHog 配置

## [x] Task 4: 添加 app_launched 事件收集
- **Priority**: P1
- **Depends On**: Task 3
- **Description**: 在程序启动成功，开始监听热键时，触发 posthog.capture(distinct_id, 'app_launched')
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-4.1: 程序启动时触发 app_launched 事件
  - `human-judgment` TR-4.2: 事件包含正确的 distinct_id
- **Notes**: 确保事件触发不阻塞主程序

## [x] Task 5: 添加 feature_used 事件收集（F2 模式）
- **Priority**: P1
- **Depends On**: Task 3
- **Description**: 在 F2 听写完成后，触发 posthog.capture(distinct_id, 'feature_used', {'mode': 'F2_dictation', 'text_length': len(text)})
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: F2 模式完成后触发 feature_used 事件
  - `programmatic` TR-5.2: 事件包含正确的 mode 和 text_length
  - `human-judgment` TR-5.3: 事件不包含具体文本内容
- **Notes**: 只发送字符长度，不发送具体文本

## [x] Task 6: 添加 feature_used 和 api_latency 事件收集（F4 模式）
- **Priority**: P1
- **Depends On**: Task 3
- **Description**:
  - 在 F4 上帝模式完成后，触发 feature_used 事件
  - 计算从松开按键到文字上屏的耗时，触发 api_latency 事件
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: F4 模式完成后触发 feature_used 事件
  - `programmatic` TR-6.2: F4 模式完成后触发 api_latency 事件
  - `programmatic` TR-6.3: 事件包含正确的属性
  - `human-judgment` TR-6.4: 事件不包含具体文本内容
- **Notes**: 计算准确的延迟时间

## [x] Task 7: 添加异常处理，确保遥测失败不影响主程序
- **Priority**: P1
- **Depends On**: Task 4, Task 5, Task 6
- **Description**: 为所有 posthog.capture 调用添加 try-except 包裹，确保网络异常时程序正常运行
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: 网络连接失败时程序继续运行
  - `programmatic` TR-7.2: PostHog 服务不可用时程序继续运行
- **Notes**: 异常处理应静默失败，不打印错误信息

## [x] Task 8: 测试遥测功能
- **Priority**: P2
- **Depends On**: Task 4, Task 5, Task 6, Task 7
- **Description**: 运行程序，测试所有遥测事件是否正常触发
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-8.1: 程序启动时触发 app_launched 事件
  - `programmatic` TR-8.2: F2 模式触发 feature_used 事件
  - `programmatic` TR-8.3: F4 模式触发 feature_used 和 api_latency 事件
  - `human-judgment` TR-8.4: 所有事件数据符合预期，无隐私数据
- **Notes**: 检查 PostHog 控制台是否接收到事件