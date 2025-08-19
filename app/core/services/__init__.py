# -*- coding: utf-8 -*-
"""
服务层模块

包含各种业务服务，如持久化服务等。
服务层负责协调业务逻辑和外部资源的交互。
"""

from .persistence_service import PersistenceService

__all__ = ['PersistenceService']