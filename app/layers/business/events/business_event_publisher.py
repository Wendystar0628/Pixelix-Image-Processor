"""业务事件发布器"""
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

from app.shared.events.event_bus import get_event_bus
from app.shared.events.event_models import Event, ImageProcessedEvent


class BusinessEventPublisher:
    """业务层事件发布器"""
    
    def __init__(self):
        self._event_bus = get_event_bus()
    
    def publish_image_processed(
        self,
        image_path: str,
        operation_type: str,
        processing_time: float,
        success: bool,
        error_message: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """发布图像处理完成事件"""
        event = ImageProcessedEvent(
            event_type="ImageProcessed",
            source_layer="business",
            target_layer="controller",
            payload={
                "image_path": image_path,
                "operation_type": operation_type,
                "processing_time": processing_time,
                "success": success,
                "error_message": error_message
            },
            timestamp=datetime.now(),
            correlation_id=correlation_id or str(uuid.uuid4()),
            image_path=image_path,
            operation_type=operation_type,
            processing_time=processing_time,
            success=success,
            error_message=error_message
        )
        
        self._event_bus.publish(event)
    
    def publish_pipeline_rendered(
        self,
        pipeline_length: int,
        processing_time: float,
        success: bool,
        error_message: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """发布流水线渲染完成事件"""
        event = Event(
            event_type="PipelineRendered",
            source_layer="business",
            target_layer="controller",
            payload={
                "pipeline_length": pipeline_length,
                "processing_time": processing_time,
                "success": success,
                "error_message": error_message
            },
            timestamp=datetime.now(),
            correlation_id=correlation_id or str(uuid.uuid4())
        )
        
        self._event_bus.publish(event)