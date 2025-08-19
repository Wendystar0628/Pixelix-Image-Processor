# ProcessingHandler 重构实现计划

- [ ] 1. 创建 ImageLoadingService 核心服务
  - 在 `app/core/services/` 目录下创建 `image_loading_service.py`
  - 实现简化的图像加载流程，直接加载全分辨率图像
  - 集成现有的 ErrorRecoveryService 进行错误处理
  - _需求: 1.2, 2.1, 2.2, 4.2_

- [ ] 2. 重构 ProcessingHandler 移除业务流程编排
  - 从 ProcessingHandler 中移除 `load_image_complete()` 方法
  - 从 ProcessingHandler 中移除 `clear_image_complete()` 方法  
  - 从 ProcessingHandler 中删除 `load_image_proxy_complete()` 方法
  - _需求: 1.1, 2.2, 4.1_

- [ ] 3. 移除状态管理相关的辅助方法
  - 从 ProcessingHandler 中移除 `_capture_current_state()` 方法
  - 从 ProcessingHandler 中移除 `_restore_state()` 方法
  - 清理相关的导入和类型定义
  - _需求: 1.3, 4.1_

- [ ] 4. 更新 AppController 调用接口
  - 修改 AppController 中图像加载相关的方法调用
  - 将图像加载请求重定向到 ImageLoadingService
  - 确保图像清除功能正常工作
  - _需求: 2.1, 2.3, 5.2_

- [ ] 5. 验证预览功能保持完整
  - 确认 `on_slider_pressed()` 和 `on_slider_released()` 方法正常工作
  - 确认 `start_preview()` 和 `cancel_preview()` 方法正常工作
  - 验证实时预览参数设置功能
  - _需求: 3.1, 3.2, 3.3, 5.3_

- [ ] 6. 测试图像加载功能
  - 测试全分辨率图像直接加载功能
  - 验证图像加载后的显示效果
  - 确认不再创建代理图像用于主视图
  - _需求: 2.1, 2.2, 2.3, 5.1_

- [ ] 7. 验证所有图像操作功能
  - 测试所有 `apply_*` 方法的正常工作
  - 验证命令创建和执行逻辑
  - 确认操作后的状态更新正常
  - _需求: 5.1, 5.2_