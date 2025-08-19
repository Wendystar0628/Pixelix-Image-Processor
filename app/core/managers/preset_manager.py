"""
预设管理器模块

提供预设的保存、加载、删除等功能。
"""
import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.core.models import PresetModel
from ..operations.base_operation import ImageOperation


class PresetManager:
    """
    预设管理器，负责预设的保存、加载、删除等操作。
    """
    
    def __init__(self, presets_dir: Optional[str] = None):
        """
        初始化预设管理器。
        
        Args:
            presets_dir: 预设文件存储目录，如果为None，则使用默认目录
        """
        # 如果没有指定预设目录，则使用默认目录
        if presets_dir is None:
            # 在应用程序目录下创建 presets 目录
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.presets_dir = os.path.join(base_dir, "presets")
        else:
            self.presets_dir = presets_dir
            
        # 确保预设目录存在
        os.makedirs(self.presets_dir, exist_ok=True)
        
    def save_preset(self, preset: PresetModel) -> bool:
        """
        保存预设到文件。
        
        Args:
            preset: 要保存的预设对象
            
        Returns:
            bool: 是否成功保存
        """
        try:
            # 构建文件路径
            file_name = f"{preset.name}.json"
            file_path = os.path.join(self.presets_dir, file_name)
            
            # 将预设转换为字典
            preset_dict = preset.to_dict()
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(preset_dict, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"保存预设失败: {e}")
            return False
            
    def load_preset(self, name: str) -> Optional[PresetModel]:
        """
        从文件加载预设。
        
        Args:
            name: 预设名称
            
        Returns:
            Optional[PresetModel]: 加载的预设对象，如果失败则返回None
        """
        try:
            # 构建文件路径
            file_name = f"{name}.json"
            file_path = os.path.join(self.presets_dir, file_name)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"预设文件不存在: {file_path}")
                return None
                
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                preset_dict = json.load(f)
                
            # 从字典创建预设对象
            preset = PresetModel.from_dict(preset_dict)
            
            return preset
        except Exception as e:
            print(f"加载预设失败: {e}")
            return None
            
    def delete_preset(self, name: str) -> bool:
        """
        删除预设文件。
        
        Args:
            name: 预设名称
            
        Returns:
            bool: 是否成功删除
        """
        try:
            # 构建文件路径
            file_name = f"{name}.json"
            file_path = os.path.join(self.presets_dir, file_name)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"预设文件不存在: {file_path}")
                return False
                
            # 删除文件
            os.remove(file_path)
            
            return True
        except Exception as e:
            print(f"删除预设失败: {e}")
            return False
            
    def get_all_presets(self) -> List[str]:
        """
        获取所有可用的预设名称。
        
        Returns:
            List[str]: 预设名称列表
        """
        try:
            # 获取预设目录中的所有JSON文件
            preset_files = [f for f in os.listdir(self.presets_dir) if f.endswith('.json')]
            
            # 提取预设名称（去掉.json后缀）
            preset_names = [os.path.splitext(f)[0] for f in preset_files]
            
            return preset_names
        except Exception as e:
            print(f"获取预设列表失败: {e}")
            return []
            
    def load_all_presets(self) -> List[PresetModel]:
        """
        加载所有预设。
        
        Returns:
            List[PresetModel]: 预设对象列表
        """
        presets = []
        
        for name in self.get_all_presets():
            preset = self.load_preset(name)
            if preset:
                presets.append(preset)
                
        return presets 