# MagicVoice 遥测功能 - 产品需求文档

## Overview
- **Summary**: 为 MagicVoice 集成 PostHog 遥测功能，收集核心业务指标，包括用户启动、功能使用和API延迟数据，为产品决策提供数据支持。
- **Purpose**: 建立数据驱动的产品决策机制，通过真实数据展示产品使用情况，为 AI PM 简历提供数据图表支撑。
- **Target Users**: MagicVoice 产品经理和开发者，用于分析产品使用情况和优化产品体验。

## Goals
- 建立最小可行性的数据收集反馈流
- 收集核心业务指标，包括 DAU、功能使用占比和 API 延迟
- 确保遥测功能不干扰核心功能（F2/F4）
- 保护用户隐私，不收集具体语音或文本内容
- 提供零成本的企业级数据看板

## Non-Goals (Out of Scope)
- 不收集用户的具体语音或文本内容
- 不干扰核心功能的正常运行
- 不增加用户的使用负担
- 不要求用户注册或登录

## Background & Context
MagicVoice 是一款基于阿里云 API 的 Windows 语音转文字工具，支持 F2 听写模式和 F4 上帝模式（语音转文字 + AI 回答）。为了进一步优化产品，需要建立数据收集机制，了解用户使用情况和产品性能。

## Functional Requirements
- **FR-1**: 集成 PostHog 遥测 SDK
- **FR-2**: 生成并存储匿名用户标识（UUID）
- **FR-3**: 收集 app_launched 事件（启动事件）
- **FR-4**: 收集 feature_used 事件（功能使用事件）
- **FR-5**: 收集 api_latency 事件（API 延迟事件）
- **FR-6**: 确保遥测请求不阻塞主程序

## Non-Functional Requirements
- **NFR-1**: 隐私保护 - 不收集用户的具体语音或文本内容
- **NFR-2**: 可靠性 - 遥测失败不应影响主程序运行
- **NFR-3**: 性能 - 遥测功能不应增加明显的启动时间或运行负担
- **NFR-4**: 可扩展性 - 遥测架构应便于未来添加新的事件类型

## Constraints
- **Technical**: 使用 PostHog Python SDK，零成本实现
- **Business**: 无额外预算，使用 PostHog 免费额度
- **Dependencies**: PostHog 服务可用性

## Assumptions
- 用户设备已连接互联网
- PostHog 服务正常运行
- 用户同意数据收集（通过使用产品默示同意）

## Acceptance Criteria

### AC-1: 遥测初始化
- **Given**: 程序启动
- **When**: 加载配置时
- **Then**: 自动生成或加载 UUID，并初始化 PostHog SDK
- **Verification**: `programmatic`
- **Notes**: 控制台应打印 'Telemetry initialized successfully.'

### AC-2: 启动事件收集
- **Given**: 程序启动成功，开始监听热键
- **When**: 主函数执行完成
- **Then**: 触发 app_launched 事件，包含匿名设备 ID 和启动时间
- **Verification**: `programmatic`

### AC-3: 功能使用事件收集
- **Given**: 用户使用 F2 或 F4 功能
- **When**: 功能执行完成
- **Then**: 触发 feature_used 事件，包含模式和生成的字符数
- **Verification**: `programmatic`
- **Notes**: 只发送字符长度，不发送具体文本内容

### AC-4: API 延迟事件收集
- **Given**: 用户使用 F4 功能
- **When**: 从松开按键到文字上屏
- **Then**: 触发 api_latency 事件，包含耗时（毫秒）
- **Verification**: `programmatic`

### AC-5: 隐私保护
- **Given**: 遥测功能运行
- **When**: 收集事件数据
- **Then**: 不收集用户的具体语音或文本内容
- **Verification**: `human-judgment`

### AC-6: 异常处理
- **Given**: 网络连接失败或 PostHog 服务不可用
- **When**: 触发遥测事件
- **Then**: 程序继续正常运行，不报错闪退
- **Verification**: `programmatic`

## Open Questions
- [ ] PostHog 免费额度是否足够支持长期使用？
- [ ] 是否需要在用户首次使用时明确告知数据收集政策？
- [ ] 未来是否需要扩展其他事件类型？