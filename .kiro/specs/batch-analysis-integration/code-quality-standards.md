# 代码质量和架构标准

## 概述

本文档定义了批处理分析集成项目的代码质量标准和架构规范，确保AI编程产生高质量、可维护的代码。

## 代码质量标准

### 1. 代码复杂度控制

#### 函数复杂度
- **单个函数不超过50行**（特殊情况除外）
- **圈复杂度不超过10**
- **嵌套层级不超过4层**

```python
# ❌ 错误：复杂度过高的函数
def complex_function(data, config, options):
    if data:
        if config:
            if options:
                for item in data:
                    if item.valid:
                        if item.type == 'A':
                            if item.status == 'active':
                                # 嵌套过深
                                pass

# ✅ 正确：拆分后的函数
def process_data(data: List[DataItem], config: Config) -> List[ProcessedItem]:
    """处理数据的主函数"""
    if not data or not config:
        return []
    
    valid_items = self._filter_valid_items(data)
    return self._process_valid_items(valid_items, config)

def _filter_valid_items(self, data: List[DataItem]) -> List[DataItem]:
    """过滤有效项目"""
    return [item for item in data if item.valid]

def _process_valid_items(self, items: List[DataItem], config: Config) -> List[ProcessedItem]:
    """处理有效项目"""
    results = []
    for item in items:
        processed = self._process_single_item(item, config)
        if processed:
            results.append(processed)
    return results
```

#### 类复杂度
- **单个类不超过500行**
- **公共方法不超过20个**
- **类的职责要单一明确**

### 2. 命名规范

#### 变量命名
```python
# ✅ 好的命名
user_count = 10
is_processing_complete = False
export_config_manager = ExportConfigManager()
processed_image_data = []

# ❌ 差的命名
n = 10  # 不明确
flag = False  # 不明确
mgr = ExportConfigManager()  # 缩写
data = []  # 过于通用
```

#### 函数命名
```python
# ✅ 动词开头，描述行为
def calculate_histogram(image: np.ndarray) -> np.ndarray:
def validate_export_config(config: ExportConfig) -> bool:
def create_export_directory(base_path: str) -> str:

# ❌ 名词或不清晰的命名
def histogram(image):  # 应该是动词
def config(config):    # 重复且不清晰
def directory():       # 不明确行为
```

#### 类命名
```python
# ✅ 名词，描述实体或概念
class ThreadSafeImageProcessor:
class ResourceManager:
class ExportProgressTracker:

# ❌ 动词或不清晰的命名
class Processing:      # 应该是名词
class Manager:         # 过于通用
class Helper:          # 不明确职责
```

### 3. 文档规范

#### 模块文档
```python
"""
线程安全图像处理器模块

本模块提供线程安全的图像处理功能，支持：
- 多线程并发图像处理
- 结果缓存和内存管理
- 处理进度监控和统计

主要类：
    ThreadSafeImageProcessor: 线程安全的图像处理器

使用示例：
    processor = ThreadSafeImageProcessor(max_workers=4)
    result = processor.process_image_async(image, operations)
    
作者: AI Assistant
创建时间: 2024-11-28
版本: 1.0.0
"""
```

#### 类文档
```python
class ThreadSafeImageProcessor:
    """线程安全的图像处理器
    
    提供多线程安全的图像处理功能，包括异步处理、结果缓存和资源管理。
    
    Attributes:
        max_workers (int): 最大工作线程数
        cache_size (int): 结果缓存大小
        is_shutdown (bool): 是否已关闭
        
    Example:
        >>> processor = ThreadSafeImageProcessor(max_workers=4)
        >>> future = processor.process_image_async(image, operations)
        >>> result = future.result()
        >>> processor.shutdown()
        
    Note:
        使用完毕后必须调用shutdown()方法释放资源
    """
```

#### 方法文档
```python
def process_image_async(self, 
                       image: np.ndarray, 
                       operations: List[ImageOperation],
                       callback: Optional[Callable] = None) -> Future[np.ndarray]:
    """异步处理图像
    
    在后台线程中应用指定的图像操作序列。
    
    Args:
        image: 输入图像数据，形状为(H, W, C)
        operations: 要应用的图像操作列表
        callback: 可选的完成回调函数
        
    Returns:
        Future[np.ndarray]: 异步结果对象，包含处理后的图像
        
    Raises:
        ValueError: 当图像数据无效时
        RuntimeError: 当处理器已关闭时
        ProcessingError: 当图像处理失败时
        
    Example:
        >>> future = processor.process_image_async(image, [blur_op, sharpen_op])
        >>> processed_image = future.result(timeout=30)
    """
```

### 4. 错误处理规范

#### 异常层次结构
```python
# 基础异常类
class IntegrationError(Exception):
    """集成功能基础异常"""
    pass

# 具体异常类
class ThreadSafetyError(IntegrationError):
    """线程安全相关异常"""
    pass

class ResourceAllocationError(IntegrationError):
    """资源分配异常"""
    pass

class TaskCoordinationError(IntegrationError):
    """任务协调异常"""
    pass
```

#### 异常处理模式
```python
def process_with_retry(self, operation: Callable, max_retries: int = 3) -> Any:
    """带重试的操作处理
    
    Args:
        operation: 要执行的操作
        max_retries: 最大重试次数
        
    Returns:
        操作结果
        
    Raises:
        ProcessingError: 重试次数耗尽后仍然失败
    """
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except (ValueError, RuntimeError) as e:
            last_error = e
            if attempt < max_retries:
                self._log_retry_attempt(attempt + 1, e)
                time.sleep(2 ** attempt)  # 指数退避
            else:
                break
    
    # 重试耗尽，抛出最后的错误
    raise ProcessingError(f"操作失败，已重试{max_retries}次") from last_error
```

## 架构设计标准

### 1. 依赖注入模式

```python
# ✅ 正确：使用依赖注入
class AnalysisExportService:
    def __init__(self, 
                 batch_handler: BatchProcessingHandler,
                 analysis_calculator: AnalysisCalculator,
                 resource_manager: ResourceManager):
        self.batch_handler = batch_handler
        self.analysis_calculator = analysis_calculator
        self.resource_manager = resource_manager

# ❌ 错误：硬编码依赖
class AnalysisExportService:
    def __init__(self):
        self.batch_handler = BatchProcessingHandler()  # 硬编码
        self.analysis_calculator = AnalysisCalculator()  # 硬编码
```

### 2. 接口隔离原则

```python
# ✅ 正确：细粒度接口
from abc import ABC, abstractmethod

class ImageProcessor(ABC):
    @abstractmethod
    def process_image(self, image: np.ndarray) -> np.ndarray:
        pass

class AsyncImageProcessor(ABC):
    @abstractmethod
    def process_image_async(self, image: np.ndarray) -> Future[np.ndarray]:
        pass

class CacheableProcessor(ABC):
    @abstractmethod
    def clear_cache(self) -> None:
        pass

# 实现类只实现需要的接口
class ThreadSafeImageProcessor(ImageProcessor, AsyncImageProcessor, CacheableProcessor):
    pass

# ❌ 错误：臃肿的接口
class ImageProcessorInterface(ABC):
    @abstractmethod
    def process_image(self, image): pass
    
    @abstractmethod
    def process_image_async(self, image): pass
    
    @abstractmethod
    def clear_cache(self): pass
    
    @abstractmethod
    def get_statistics(self): pass  # 不是所有实现都需要
    
    @abstractmethod
    def export_config(self): pass   # 不相关的职责
```

### 3. 观察者模式

```python
class ProgressObserver(ABC):
    @abstractmethod
    def on_progress_updated(self, progress: int, message: str) -> None:
        pass

class TaskCoordinator:
    def __init__(self):
        self._observers: List[ProgressObserver] = []
    
    def add_observer(self, observer: ProgressObserver) -> None:
        self._observers.append(observer)
    
    def remove_observer(self, observer: ProgressObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_progress(self, progress: int, message: str) -> None:
        for observer in self._observers:
            try:
                observer.on_progress_updated(progress, message)
            except Exception as e:
                # 记录错误但不影响其他观察者
                self._log_observer_error(observer, e)
```

### 4. 工厂模式

```python
class ExporterFactory:
    """导出器工厂类"""
    
    _exporters = {
        'pyqtgraph': 'app.core.exporters.pyqtgraph_exporter.PyQtGraphExporter',
        'matplotlib': 'app.core.exporters.matplotlib_exporter.MatplotlibExporter'
    }
    
    @classmethod
    def create_exporter(cls, engine_type: str, config: ExportConfig):
        """创建导出器实例
        
        Args:
            engine_type: 渲染引擎类型
            config: 导出配置
            
        Returns:
            导出器实例
            
        Raises:
            ValueError: 不支持的引擎类型
        """
        if engine_type not in cls._exporters:
            raise ValueError(f"不支持的渲染引擎: {engine_type}")
        
        exporter_class_path = cls._exporters[engine_type]
        module_path, class_name = exporter_class_path.rsplit('.', 1)
        
        module = importlib.import_module(module_path)
        exporter_class = getattr(module, class_name)
        
        return exporter_class(config)
```

## 性能标准

### 1. 内存管理

```python
class MemoryEfficientProcessor:
    """内存高效的处理器"""
    
    def __init__(self, max_cache_size: int = 100):
        self._cache = {}
        self._max_cache_size = max_cache_size
        self._access_order = []
    
    def process_large_dataset(self, dataset: List[Any]) -> List[Any]:
        """处理大数据集，控制内存使用"""
        results = []
        
        # 分批处理，避免内存溢出
        batch_size = self._calculate_optimal_batch_size(dataset)
        
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i:i + batch_size]
            batch_results = self._process_batch(batch)
            results.extend(batch_results)
            
            # 定期清理缓存
            if i % (batch_size * 10) == 0:
                self._cleanup_cache()
                
        return results
    
    def _calculate_optimal_batch_size(self, dataset: List[Any]) -> int:
        """根据可用内存计算最优批次大小"""
        available_memory = psutil.virtual_memory().available
        estimated_item_size = self._estimate_item_memory_usage(dataset[0] if dataset else None)
        
        if estimated_item_size > 0:
            # 使用可用内存的50%作为批处理内存
            max_batch_memory = available_memory * 0.5
            batch_size = int(max_batch_memory / estimated_item_size)
            return max(1, min(batch_size, 100))  # 限制在1-100之间
        
        return 10  # 默认批次大小
```

### 2. 并发控制

```python
class ConcurrencyController:
    """并发控制器"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self._semaphore = threading.Semaphore(self.max_workers)
        self._active_tasks = 0
        self._lock = threading.RLock()
    
    @contextmanager
    def acquire_worker(self):
        """获取工作线程资源"""
        self._semaphore.acquire()
        try:
            with self._lock:
                self._active_tasks += 1
            yield
        finally:
            with self._lock:
                self._active_tasks -= 1
            self._semaphore.release()
    
    def get_active_task_count(self) -> int:
        """获取活跃任务数量"""
        with self._lock:
            return self._active_tasks
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """等待所有任务完成"""
        start_time = time.time()
        
        while self.get_active_task_count() > 0:
            if timeout and (time.time() - start_time) > timeout:
                return False
            time.sleep(0.1)
        
        return True
```

## 测试标准

### 1. 单元测试覆盖率

- **代码覆盖率 ≥ 80%**
- **关键路径覆盖率 = 100%**
- **异常处理覆盖率 ≥ 90%**

### 2. 测试用例设计

```python
class TestThreadSafeImageProcessor(unittest.TestCase):
    """线程安全图像处理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.processor = ThreadSafeImageProcessor(max_workers=2)
        self.test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        self.test_operations = [MockBlurOperation(), MockSharpenOperation()]
    
    def tearDown(self):
        """测试后清理"""
        self.processor.shutdown()
    
    def test_single_image_processing(self):
        """测试单图像处理"""
        result = self.processor.process_image(self.test_image, self.test_operations)
        
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, self.test_image.shape)
        self.assertFalse(np.array_equal(result, self.test_image))  # 应该有变化
    
    def test_concurrent_processing(self):
        """测试并发处理"""
        futures = []
        
        # 提交多个并发任务
        for i in range(10):
            future = self.processor.process_image_async(
                self.test_image, 
                self.test_operations
            )
            futures.append(future)
        
        # 等待所有任务完成
        results = [future.result(timeout=30) for future in futures]
        
        # 验证结果
        self.assertEqual(len(results), 10)
        for result in results:
            self.assertIsInstance(result, np.ndarray)
            self.assertEqual(result.shape, self.test_image.shape)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效输入
        with self.assertRaises(ValueError):
            self.processor.process_image(None, self.test_operations)
        
        # 测试处理器关闭后的行为
        self.processor.shutdown()
        with self.assertRaises(RuntimeError):
            self.processor.process_image(self.test_image, self.test_operations)
    
    def test_resource_cleanup(self):
        """测试资源清理"""
        # 处理一些图像
        for _ in range(5):
            self.processor.process_image(self.test_image, self.test_operations)
        
        # 检查缓存状态
        cache_size_before = len(self.processor._cache)
        
        # 清理缓存
        self.processor.clear_cache()
        
        # 验证缓存已清理
        self.assertEqual(len(self.processor._cache), 0)
        self.assertGreater(cache_size_before, 0)
```

### 3. 集成测试

```python
class TestBatchAnalysisIntegration(unittest.TestCase):
    """批处理分析集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.test_data_dir = Path(__file__).parent / "test_data"
        cls.test_images = list(cls.test_data_dir.glob("*.jpg"))[:5]
    
    def setUp(self):
        """每个测试前的准备"""
        self.batch_handler = MockBatchProcessingHandler()
        self.resource_manager = ResourceManager(max_memory_mb=1024, max_cpu_cores=2)
        self.task_coordinator = TaskCoordinator(self.resource_manager)
        
        # 创建测试作业
        self.test_job = self.batch_handler.add_job("测试作业")
        for image_path in self.test_images:
            self.batch_handler.add_images_to_pool([str(image_path)])
        
    def test_full_export_workflow(self):
        """测试完整的导出工作流"""
        # 配置导出
        config = ExportConfig(
            output_directory=str(self.test_data_dir / "output"),
            analysis_types=[AnalysisType.RGB_HISTOGRAM.value],
            file_format="PNG"
        )
        
        # 创建集成导出服务
        export_service = IntegratedAnalysisExportService(
            self.batch_handler,
            MockAnalysisCalculator(),
            MockImageProcessor(),
            self.resource_manager,
            self.task_coordinator
        )
        
        # 执行导出
        result = export_service.export_job_analysis(config)
        
        # 验证结果
        self.assertTrue(result.success)
        self.assertGreater(result.exported_files, 0)
        self.assertEqual(result.failed_files, 0)
        
        # 验证输出文件
        output_dir = Path(result.output_directory)
        self.assertTrue(output_dir.exists())
        
        histogram_dir = output_dir / AnalysisType.RGB_HISTOGRAM.value
        self.assertTrue(histogram_dir.exists())
        
        exported_files = list(histogram_dir.glob("*.png"))
        self.assertEqual(len(exported_files), len(self.test_images))
```

## 代码审查清单

### 1. 功能性检查
- [ ] 代码实现了所有需求
- [ ] 边界条件处理正确
- [ ] 错误处理完整
- [ ] 性能满足要求

### 2. 代码质量检查
- [ ] 命名清晰明确
- [ ] 函数和类大小合理
- [ ] 注释和文档完整
- [ ] 无重复代码

### 3. 架构检查
- [ ] 职责分离清晰
- [ ] 依赖关系合理
- [ ] 接口设计良好
- [ ] 可扩展性好

### 4. 安全性检查
- [ ] 输入验证充分
- [ ] 资源正确释放
- [ ] 线程安全
- [ ] 异常安全

通过遵循这些标准，可以确保AI编程产生高质量、可维护、可扩展的代码。