from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """
    所有命令的抽象基类。

    每个命令都代表一个对应用状态的原子性修改。
    它必须是可执行和可撤销的。
    命令在初始化时获取所需的管理器引用。
    """

    @abstractmethod
    def execute(self):
        """
        执行命令，修改相关管理器中的状态。
        """
        pass

    @abstractmethod
    def undo(self):
        """
        撤销命令，将相关管理器中的状态恢复到执行前的样子。
        """
        pass 