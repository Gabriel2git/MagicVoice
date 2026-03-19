# MagicVoice - 启动时间优化计划

## [x] 任务 1: 移除或延迟 LLM 模型测试
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - 移除 `main()` 函数中的 `test_llm_models()` 调用，或改为延迟执行
  - 分析 `test_llm_models()` 函数的作用，确定是否可以在启动后异步执行
  - 确保移除测试后不影响应用程序的正常功能
- **Success Criteria**:
  - 应用程序启动时不再执行 LLM 模型测试
  - 启动时间显著缩短
  - 应用程序功能不受影响
- **Test Requirements**:
  - `programmatic` TR-1.1: 启动时间减少至少 3 秒
  - `human-judgement` TR-1.2: 应用程序启动后功能正常，托盘图标能够快速显示
- **Notes**:
  - `test_llm_models()` 函数会发送网络请求测试 LLM 模型，这是导致启动时间长的主要原因
  - 可以考虑将测试功能移到设置窗口中，让用户手动触发

## [x] 任务 2: 优化模块导入顺序
- **Priority**: P1
- **Depends On**: None
- **Description**:
  - 分析当前的模块导入顺序，将必要的模块优先导入
  - 考虑延迟导入非必要的模块，只在需要时才导入
  - 优化导入语句，减少导入时间
- **Success Criteria**:
  - 模块导入顺序更加合理
  - 启动时间有所缩短
  - 应用程序功能不受影响
- **Test Requirements**:
  - `programmatic` TR-2.1: 导入时间减少
  - `human-judgement` TR-2.2: 应用程序启动后功能正常
- **Notes**:
  - 一些模块如 dashscope、sounddevice 可能需要较长时间导入
  - 可以考虑使用懒加载技术，只在需要时才导入这些模块

## [x] 任务 3: 优化托盘图标创建过程
- **Priority**: P2
- **Depends On**: None
- **Description**:
  - 分析托盘图标创建的过程，找出可能的优化点
  - 确保托盘图标能够尽快显示，即使其他初始化任务尚未完成
  - 考虑将托盘图标创建和显示放在启动过程的早期
- **Success Criteria**:
  - 托盘图标显示时间提前
  - 用户能够更快地看到应用程序已经启动
  - 应用程序功能不受影响
- **Test Requirements**:
  - `human-judgement` TR-3.1: 托盘图标显示时间明显提前
  - `human-judgement` TR-3.2: 应用程序启动后功能正常
- **Notes**:
  - 托盘图标是用户感知应用程序启动的重要指标
  - 可以考虑先显示基本图标，然后再进行其他初始化任务

## [x] 任务 4: 重新打包应用程序并测试启动时间
- **Priority**: P2
- **Depends On**: 任务 1, 任务 2, 任务 3
- **Description**:
  - 运行 build.py 脚本重新打包应用程序
  - 测试优化后的应用程序启动时间
  - 验证应用程序功能是否正常
- **Success Criteria**:
  - 应用程序成功打包
  - 启动时间显著缩短（目标：从 5 秒减少到 2 秒以内）
  - 应用程序功能正常
- **Test Requirements**:
  - `programmatic` TR-4.1: 打包过程完成，没有错误
  - `programmatic` TR-4.2: 启动时间减少至少 3 秒
  - `human-judgement` TR-4.3: 应用程序启动后功能正常，托盘图标能够快速显示
- **Notes**:
  - 确保在打包前终止所有正在运行的 MagicVoice 实例
  - 测试启动时间时，应该多次运行取平均值
