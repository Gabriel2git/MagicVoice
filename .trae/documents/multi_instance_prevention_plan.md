# MagicVoice - 防止多实例运行的窗口提示功能实现计划

## [x] 任务 1: 修改防止多实例运行的代码，添加窗口提示功能
- **Priority**: P1
- **Depends On**: None
- **Description**:
  - 修改 `magic_voice.py` 文件中的防止多实例运行代码
  - 当检测到已有实例运行时，弹出一个窗口提示用户
  - 窗口应该包含清晰的提示信息，告知用户程序已经在运行
  - 确保窗口能够在打包后的应用程序中正常显示
- **Success Criteria**:
  - 当尝试启动多个MagicVoice实例时，会弹出窗口提示用户
  - 提示窗口能够正常显示，包含清晰的提示信息
  - 程序在显示提示后能够正常退出
- **Test Requirements**:
  - `programmatic` TR-1.1: 当已有实例运行时，新实例会弹出提示窗口并退出
  - `human-judgement` TR-1.2: 提示窗口显示清晰，信息明确，用户能够理解程序已经在运行
- **Notes**:
  - 需要使用tkinter库创建提示窗口
  - 确保在导入tkinter之前检查是否已有实例运行，以避免不必要的资源消耗
  - 考虑在打包后的应用程序中窗口的显示效果

## [x] 任务 2: 重新打包应用程序
- **Priority**: P2
- **Depends On**: 任务 1
- **Description**:
  - 运行build.py脚本重新打包应用程序
  - 确保打包过程顺利完成
  - 验证打包后的可执行文件能够正确显示多实例提示窗口
- **Success Criteria**:
  - 应用程序成功打包到指定目录
  - 打包后的可执行文件能够正常运行
  - 当尝试启动多个实例时，会弹出提示窗口
- **Test Requirements**:
  - `programmatic` TR-2.1: 打包过程完成，没有错误
  - `programmatic` TR-2.2: 打包后的可执行文件能够正常启动
  - `human-judgement` TR-2.3: 尝试启动多个实例时，提示窗口能够正常显示
- **Notes**:
  - 确保在打包前终止所有正在运行的MagicVoice实例
  - 验证打包后的可执行文件在不同环境下的表现
