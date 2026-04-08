# -*- coding: utf-8 -*-
"""
API配置管理
包含API密钥管理和环境配置
"""

import os
from typing import Optional

# API密钥配置
API_KEY_CONFIG = {
    "openai": {
        "env_var": "OPENAI_API_KEY",
        "default_base_url": "https://api.openai.com/v1"
    },
    "deepseek": {
        "env_var": "DEEPSEEK_API_KEY", 
        "default_base_url": "https://api.deepseek.com/v1"
    },
    "gemini": {
        "env_var": "GEMINI_API_KEY",
        "default_base_url": None
    }
}

# 默认配置
DEFAULT_CONFIG = {
    "model": "gpt-3.5-turbo",
    "provider": "openai"
}

def get_api_key(provider: str = "openai") -> Optional[str]:
    """
    获取API密钥
    
    Args:
        provider: 提供商名称
        
    Returns:
        str: API密钥，如果未找到则返回None
    """
    config = API_KEY_CONFIG.get(provider, {})
    env_var = config.get("env_var")
    
    if env_var:
        return os.getenv(env_var)
    
    return None

def set_api_key(provider: str, api_key: str):
    """
    设置API密钥到环境变量
    
    Args:
        provider: 提供商名称
        api_key: API密钥
    """
    config = API_KEY_CONFIG.get(provider, {})
    env_var = config.get("env_var")
    
    if env_var:
        os.environ[env_var] = api_key
    else:
        raise ValueError(f"不支持的提供商: {provider}")

def get_base_url(provider: str) -> Optional[str]:
    """
    获取默认基础URL
    
    Args:
        provider: 提供商名称
        
    Returns:
        str: 基础URL
    """
    config = API_KEY_CONFIG.get(provider, {})
    return config.get("default_base_url")

def is_api_key_configured(provider: str = "openai") -> bool:
    """
    检查API密钥是否已配置
    
    Args:
        provider: 提供商名称
        
    Returns:
        bool: 是否已配置
    """
    return get_api_key(provider) is not None

def get_all_configured_providers() -> list:
    """
    获取所有已配置API密钥的提供商
    
    Returns:
        list: 已配置的提供商列表
    """
    configured = []
    for provider in API_KEY_CONFIG.keys():
        if is_api_key_configured(provider):
            configured.append(provider)
    return configured
