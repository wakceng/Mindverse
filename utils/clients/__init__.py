# -*- coding: utf-8 -*-
"""
LLM客户端模块
提供统一的LLM调用接口
"""

from .text_generator import TextGenerator
from .openai_client import OpenAIClient
from .deepseek_client import DeepSeekClient
from .gemini_client import GeminiClient

# 主要的公共接口
__all__ = [
    'TextGenerator',  # 主入口，推荐使用
    'OpenAIClient', 
    'DeepSeekClient',
    'GeminiClient'
]

# 向后兼容别名
MultiLLMClient = TextGenerator  # 向后兼容