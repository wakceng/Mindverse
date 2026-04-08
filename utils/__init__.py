# -*- coding: utf-8 -*-
"""
工具模块
提供LLM客户端、配置管理、内容生成器和日志记录功能
"""

# 导入主要类
from .clients import TextGenerator, OpenAIClient, DeepSeekClient, GeminiClient, MultiLLMClient
from .config import get_model_config, estimate_cost, get_api_key, set_api_key
from .generators import PromptGenerator
from .logging import PatientLogger

# 向后兼容的导入
from .config.model_config import ALL_MODELS, get_available_models
from .config.api_config import DEFAULT_CONFIG

__all__ = [
    # 客户端
    'TextGenerator',  # 推荐使用的主入口
    'MultiLLMClient',  # 向后兼容别名
    'OpenAIClient',
    'DeepSeekClient',
    'GeminiClient',
    
    # 配置
    'get_model_config',
    'estimate_cost',
    'get_api_key',
    'set_api_key',
    'ALL_MODELS',
    'get_available_models',
    'DEFAULT_CONFIG',
    
    # 生成器
    'PromptGenerator',
    
    # 日志
    'PatientLogger'
]

# 版本信息
__version__ = '2.0.0'
