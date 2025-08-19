# 设计文档

## 概述

本设计文档描述了如何增强现有图像处理软件以支持中文文件名处理和完善数据分析导出功能。设计遵循现有的分层架构，通过增强基础设施层的文件服务和核心层的导出服务来实现功能。

## 架构设计

### 核心组件

1. **中文编码处理工具** - 位于utils层，提供编码检测和转换功能
2. **增强文件服务** - 扩展现有FileService，添加中文文件名支持
3. **完善分析导出服务** - 增强现有AnalysisExportService，确保导出功能完整
4. **文件名安全处理器** - 处理文件名特殊字符和编码问题

### 分层职责

- **基础设施层**: 文件系统操作的中文编码支持
- **核心层**: 分析导出逻辑完善和中文文件名处理集成
- **工具层**: 编码检测、文件名处理等通用工具

## 组件设计

### 1. 中文编码处理工具

**文件**: `app/utils/chinese_encoding_handler.py`

**职责**:
- 自动检测文件路径编码（UTF-8、GBK、GB2312）
- 提供编码转换功能
- 处理编码异常和回退机制

**核心方法**:
- `detect_encoding(file_path)` - 检测文件路径编码
- `safe_encode_path(path, target_encoding)` - 安全编码转换
- `normalize_chinese_path(path)` - 标准化中文路径

### 2. 文件名安全处理器

**文件**: `app/utils/filename_sanitizer.py`

**职责**:
- 清理和标准化文件名
- 处理特殊字符和长度限制
- 生成安全的导出文件名

**核心方法**:
- `sanitize_filename(filename)` - 清理文件名
- `generate_safe_export_name(original_name, suffix)` - 生成安全导出名
- `handle_filename_conflicts(base_path, filename)` - 处理文件名冲突

### 3. 增强文件服务

**文件**: `app/layers/infrastructure/filesystem/file_service.py` (修改)

**增强内容**:
- 集成中文编码处理
- 增强错误处理和日志记录
- 添加编码检测和转换逻辑

**修改方法**:
- `load_image()` - 添加中文路径处理
- `save_image()` - 增强中文文件名保存
- `get_image_files_in_directory()` - 支持中文目录扫描

### 4. 完善分析导出服务

**文件**: `app/core/services/analysis_export_service.py` (修改)

**增强内容**:
- 集成文件名安全处理
- 完善导出错误处理
- 确保所有分析类型导出功能完整

**修改方法**:
- `_create_export_directory_structure()` - 支持中文目录名
- `_sanitize_filename()` - 使用新的文件名处理器
- `export_analysis_data()` - 增强错误处理

## 数据模型

### 编码检测结果

```python
@dataclass
class EncodingDetectionResult:
    detected_encoding: str
    confidence: float
    is_chinese: bool
    fallback_used: bool
```

### 文件处理结果

```python
@dataclass
class FileProcessingResult:
    success: bool
    processed_path: str
    original_encoding: str
    target_encoding: str
    error_message: Optional[str]
```

## 错误处理策略

### 编码错误处理

1. **检测失败**: 回退到UTF-8编码
2. **转换失败**: 记录错误并使用原始路径
3. **文件操作失败**: 提供详细错误信息

### 导出错误处理

1. **文件名冲突**: 自动添加数字后缀
2. **目录创建失败**: 尝试使用临时目录
3. **编码问题**: 转换为安全字符

## 测试策略

### 单元测试重点

1. **编码检测准确性** - 测试各种中文编码的检测
2. **文件名处理** - 测试特殊字符和长文件名处理
3. **导出功能完整性** - 测试所有分析类型的导出

### 集成测试重点

1. **端到端中文文件处理** - 从加载到保存的完整流程
2. **批处理中文文件** - 混合中英文文件名的批处理
3. **导出功能验证** - 各种格式和配置的导出测试

## 性能考虑

### 编码检测优化

- 缓存检测结果避免重复检测
- 使用快速检测算法
- 限制检测文件大小

### 文件操作优化

- 批量操作时复用编码检测结果
- 异步处理大批量文件
- 内存使用优化

## 向后兼容性

### 现有功能保护

- 英文文件名处理保持原有性能
- 现有配置和设置继续有效
- API接口保持兼容

### 渐进式增强

- 中文支持作为增强功能添加
- 不影响现有工作流程
- 可选的高级编码设置