# Implementation Plan

- [x] 1. 移除图像池的自动加载逻辑


  - 修改 `ImagePoolManager` 类，移除添加图像时自动加载到主视图的信号发送
  - 修改 `BatchProcessingHandler` 类，移除 `_on_image_added_to_pool` 方法中的自动加载逻辑
  - _Requirements: 2.3_



- [ ] 2. 移除主视图的文件打开功能
  - 修改 `InteractiveImageLabel` 类，移除 `mouseDoubleClickEvent` 中的文件对话框打开逻辑

  - 保留图像显示和交互功能，只移除文件IO相关代码
  - _Requirements: 1.1, 1.2_

- [x] 3. 重定向工具栏添加图像功能

  - 修改 `ToolbarManager` 类，将添加图像按钮的行为重定向到图像池面板
  - 确保点击工具栏按钮时激活图像池的添加功能，而不是直接打开文件对话框
  - _Requirements: 1.3_



- [ ] 4. 重定向菜单打开文件功能
  - 修改 `MenuManager` 类，将"打开文件"菜单项重定向到图像池面板
  - 保持用户体验的一致性，确保所有文件添加操作都通过图像池
  - _Requirements: 1.1, 1.3_

- [x] 5. 更新主视图状态管理


  - 修改主视图相关代码，确保只有当主视图有图像时才启用图像处理功能
  - 当主视图为空时，禁用所有依赖于当前图像的操作
  - _Requirements: 3.3_

- [x] 6. 清理旧的自动加载代码


  - 删除 `BatchProcessingHandler` 中未使用的 `_on_image_added_to_pool` 方法
  - 删除 `ImagePoolManager` 中未使用的自动加载相关信号和方法
  - 清理 `main.py` 中不再需要的信号连接代码
  - _Requirements: 5.1, 5.2_



- [ ] 7. 清理未使用的导入和死代码
  - 检查并删除所有文件中未使用的导入语句
  - 删除任何不再被调用的方法和变量
  - 确保代码整洁，没有死代码残留
  - _Requirements: 5.3_

- [x] 8. 测试数据流的单向性





  - 编写测试验证图像只能从图像池流向主视图
  - 测试主视图不能直接打开文件
  - 测试工具栏和菜单的重定向功能正常工作
  - 验证所有旧代码已被正确清理
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 5.1, 5.2, 5.3_