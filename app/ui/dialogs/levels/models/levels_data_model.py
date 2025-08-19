"""
色阶数据模型模块
负责色阶调整参数的存储和管理
"""

from typing import Dict, Any, Optional, Tuple


class LevelsDataModel:
    """
    色阶数据模型
    管理色阶调整的参数，包括输入/输出色阶和伽马值
    """

    def __init__(self):
        """初始化色阶数据模型，设置默认值"""
        # 默认值
        self._input_black = 0
        self._input_white = 255
        self._gamma = 1.0  # 1.0表示线性
        self._output_black = 0
        self._output_white = 255

    @property
    def input_black(self) -> int:
        """获取输入黑场值"""
        return self._input_black

    @input_black.setter
    def input_black(self, value: int):
        """设置输入黑场值，确保不超过输入白场"""
        self._input_black = max(0, min(value, self._input_white - 1))

    @property
    def input_white(self) -> int:
        """获取输入白场值"""
        return self._input_white

    @input_white.setter
    def input_white(self, value: int):
        """设置输入白场值，确保不小于输入黑场"""
        self._input_white = max(self._input_black + 1, min(value, 255))

    @property
    def gamma(self) -> float:
        """获取伽马值"""
        return self._gamma

    @gamma.setter
    def gamma(self, value: float):
        """设置伽马值，限制在合理范围内"""
        self._gamma = max(0.1, min(value, 9.99))

    @property
    def output_black(self) -> int:
        """获取输出黑场值"""
        return self._output_black

    @output_black.setter
    def output_black(self, value: int):
        """设置输出黑场值，确保不超过输出白场"""
        self._output_black = max(0, min(value, self._output_white))

    @property
    def output_white(self) -> int:
        """获取输出白场值"""
        return self._output_white

    @output_white.setter
    def output_white(self, value: int):
        """设置输出白场值，确保不小于输出黑场"""
        self._output_white = max(self._output_black, min(value, 255))

    def get_input_range(self) -> Tuple[int, int]:
        """获取输入范围（黑场，白场）"""
        return (self._input_black, self._input_white)

    def get_output_range(self) -> Tuple[int, int]:
        """获取输出范围（黑场，白场）"""
        return (self._output_black, self._output_white)

    def get_serializable_data(self) -> Dict[str, Any]:
        """获取可序列化的数据，用于保存或传递给操作类"""
        return {
            "input_black": self._input_black,
            "input_white": self._input_white,
            "input_gamma": self._gamma,
            "output_black": self._output_black,
            "output_white": self._output_white,
        }

    def load_from_params(self, params: Dict[str, Any]):
        """从参数字典加载数据"""
        # 先设置白场值，避免黑场值超过白场值的验证问题
        if "input_white" in params:
            self.input_white = params["input_white"]
        if "output_white" in params:
            self.output_white = params["output_white"]

        # 再设置其他参数
        if "input_black" in params:
            self.input_black = params["input_black"]
        if "input_gamma" in params:
            self.gamma = params["input_gamma"]
        if "output_black" in params:
            self.output_black = params["output_black"] 