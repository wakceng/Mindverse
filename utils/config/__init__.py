# -*- coding: utf-8 -*-
"""
配置模块
统一管理所有配置相关功能
"""

from .model_config import (
    ALL_MODELS,
    OPENAI_MODELS,
    DEEPSEEK_MODELS,
    GEMINI_MODELS,
    PROVIDER_MAP,
    CONFIG_ADJUSTMENTS,
    get_model_config,
    get_provider_for_model,
    estimate_cost,
    get_available_models
)

from .api_config import (
    API_KEY_CONFIG,
    DEFAULT_CONFIG,
    get_api_key,
    set_api_key,
    get_base_url,
    is_api_key_configured,
    get_all_configured_providers
)

__all__ = [
    # 模型配置
    'ALL_MODELS',
    'OPENAI_MODELS',
    'DEEPSEEK_MODELS', 
    'GEMINI_MODELS',
    'PROVIDER_MAP',
    'CONFIG_ADJUSTMENTS',
    'get_model_config',
    'get_provider_for_model',
    'estimate_cost',
    'get_available_models',
    
    # API配置
    'API_KEY_CONFIG',
    'DEFAULT_CONFIG',
    'get_api_key',
    'set_api_key',
    'get_base_url',
    'is_api_key_configured',
    'get_all_configured_providers'
]
