# 代码文件结构规范指导

## 修改前后文件结构对比

### 新增文件

```
app/utils/chinese_encoding_handler.py          # 中文编码处理工具
app/utils/filename_sanitizer.py                # 文件名安全处理器
```

### 修改文件

```
app/layers/infrastructure/filesystem/file_service.py    # 增强中文文件名支持
app/core/services/analysis_export_service.py            # 完善导出功能
```

## 新增文件职责说明

### app/utils/chinese_encoding_handler.py
- **职责**: 提供中文编码检测和转换功能
- **核心功能**: 自动检测文件路径编码，安全转换编码，处理编码异常
- **架构位置**: 工具层，为其他组件提供编码处理服务

### app/utils/filename_sanitizer.py
- **职责**: 处理文件名安全性和标准化
- **核心功能**: 清理特殊字符，生成安全文件名，处理文件名冲突
- **架构位置**: 工具层，为文件操作提供安全保障

## 修改文件内容说明

### app/layers/infrastructure/filesystem/file_service.py
- **修改内容**: 集成中文编码处理，增强错误处理
- **新增方法**: 无，仅增强现有方法
- **修改方法**: load_image(), save_image(), get_image_files_in_directory()
- **清理内容**: 移除简单的文件名处理逻辑，使用新的处理器

### app/core/services/analysis_export_service.py
- **修改内容**: 集成文件名安全处理，完善导出功能
- **新增方法**: 无，仅增强现有方法
- **修改方法**: _create_export_directory_structure(), _sanitize_filename(), export_analysis_data()
- **清理内容**: 移除旧的简单文件名清理逻辑，使用统一的处理器

## 代码清理指导

### 需要清理的旧代码模式

1. **简单字符替换的文件名处理**
   - 位置: analysis_export_service.py中的_sanitize_filename方法
   - 清理方式: 替换为调用filename_sanitizer的方法

2. **硬编码的编码处理**
   - 位置: file_service.py中可能存在的编码假设
   - 清理方式: 使用chinese_encoding_handler进行动态检测

3. **重复的错误处理逻辑**
   - 位置: 各个文件操作方法中
   - 清理方式: 统一使用新的错误处理机制

### 清理步骤

1. **识别旧逻辑**: 搜索现有的文件名处理和编码相关代码
2. **保留接口**: 保持公共方法签名不变，仅修改内部实现
3. **移除冗余**: 删除被新工具替代的旧实现
4. **更新调用**: 确保所有调用点使用新的处理逻辑

## 架构合规性检查

### 分层职责验证

- **工具层文件**: 仅提供纯函数和工具类，无业务逻辑
- **基础设施层**: 仅处理技术基础设施，不包含业务规则
- **核心层**: 专注业务逻辑，通过依赖注入使用基础设施服务

### 依赖关系检查

- **工具层**: 不依赖其他应用层
- **基础设施层**: 可依赖工具层
- **核心层**: 通过接口依赖基础设施层

## 文件命名规范

### 命名原则

- **功能明确**: 文件名清晰表达功能用途
- **避免重复**: 确保在整个项目中文件名唯一
- **分层标识**: 通过路径体现架构分层

### 具体规范

- **工具类**: 使用`_handler`、`_processor`、`_sanitizer`等后缀
- **服务类**: 使用`_service`后缀
- **接口类**: 使用`_interface`后缀
- **模型类**: 使用`_models`或具体业务名称

## 测试文件组织

### 测试文件结构

```
tests/utils/test_chinese_encoding_handler.py    # 编码处理工具测试
tests/utils/test_filename_sanitizer.py          # 文件名处理器测试
tests/integration/test_chinese_filename_flow.py # 集成测试
```

### 测试职责

- **单元测试**: 测试单个工具类的功能
- **集成测试**: 测试完整的中文文件处理流程
- **回归测试**: 确保现有英文文件处理不受影响