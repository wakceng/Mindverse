# -*- coding: utf-8 -*-
"""
模型配置管理
包含不同模型的配置参数和成本信息
"""

from typing import Dict, Any

# OpenAI 模型配置
OPENAI_MODELS = {
    "gpt-3.5-turbo": {
        "max_tokens": 4096,
        "temperature_range": (0.0, 2.0),
        "cost_per_1k_tokens": {"input": 0.0015, "output": 0.002},
        "recommended_config": {
            "temperature": 0.8,
            "max_tokens": 800,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }
    },
    "gpt-4": {
        "max_tokens": 8192,
        "temperature_range": (0.0, 2.0),
        "cost_per_1k_tokens": {"input": 0.03, "output": 0.06},
        "recommended_config": {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
    },
    "gpt-4-turbo": {
        "max_tokens": 4096,
        "temperature_range": (0.0, 2.0),
        "cost_per_1k_tokens": {"input": 0.01, "output": 0.03},
        "recommended_config": {
            "temperature": 0.8,
            "max_tokens": 1200,
            "top_p": 0.95,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }
    }
}

# DeepSeek 模型配置
DEEPSEEK_MODELS = {
    "deepseek-chat": {
        "max_tokens": 4096,
        "temperature_range": (0.0, 2.0),
        "cost_per_1k_tokens": {"input": 0.0001, "output": 0.0002},
        "recommended_config": {
            "temperature": 0.8,
            "max_tokens": 800,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }
    },
    "deepseek-coder": {
        "max_tokens": 4096,
        "temperature_range": (0.0, 2.0),
        "cost_per_1k_tokens": {"input": 0.0001, "output": 0.0002},
        "recommended_config": {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
    }
}

# Gemini 模型配置
GEMINI_MODELS = {
    "gemini-pro": {
        "max_tokens": 8192,
        "temperature_range": (0.0, 1.0),
        "cost_per_1k_tokens": {"input": 0.0005, "output": 0.0015},
        "recommended_config": {
            "temperature": 0.8,
            "max_output_tokens": 800,
            "top_p": 0.9,
            "top_k": 40
        }
    },
    "gemini-pro-vision": {
        "max_tokens": 4096,
        "temperature_range": (0.0, 1.0),
        "cost_per_1k_tokens": {"input": 0.0025, "output": 0.01},
        "recommended_config": {
            "temperature": 0.7,
            "max_output_tokens": 1000,
            "top_p": 0.9,
            "top_k": 32
        }
    }
}

# 合并所有模型配置
ALL_MODELS = {
    **OPENAI_MODELS,
    **DEEPSEEK_MODELS,
    **GEMINI_MODELS
}

# 提供商映射
PROVIDER_MAP = {
    "gpt-3.5-turbo": "openai",
    "gpt-4": "openai", 
    "gpt-4-turbo": "openai",
    "deepseek-chat": "deepseek",
    "deepseek-coder": "deepseek",
    "gemini-pro": "gemini",
    "gemini-pro-vision": "gemini"
}

# 内容类型和抑郁等级的配置调整
CONFIG_ADJUSTMENTS = {
    "self_description": {
        "正常": {"temperature": 0.8, "max_tokens": 600},
        "轻度": {"temperature": 0.9, "max_tokens": 700},
        "中度": {"temperature": 1.0, "max_tokens": 800},
        "重度": {"temperature": 1.1, "max_tokens": 900}
    },
    "social_post": {
        "正常": {"temperature": 0.7, "max_tokens": 300},
        "轻度": {"temperature": 0.8, "max_tokens": 350},
        "中度": {"temperature": 0.9, "max_tokens": 400},
        "重度": {"temperature": 1.0, "max_tokens": 450}
    },
    "questionnaire": {
        "正常": {"temperature": 0.3, "max_tokens": 10},
        "轻度": {"temperature": 0.3, "max_tokens": 10},
        "中度": {"temperature": 0.3, "max_tokens": 10},
        "重度": {"temperature": 0.3, "max_tokens": 10}
    }
}

def get_model_config(model: str, content_type: str = "self_description", depression_level: str = "正常") -> Dict[str, Any]:
    """
    获取模型配置
    
    Args:
        model: 模型名称
        content_type: 内容类型
        depression_level: 抑郁等级
        
    Returns:
        dict: 配置参数
    """
    # 获取基础配置
    base_config = ALL_MODELS.get(model, {}).get("recommended_config", {
        "temperature": 0.8,
        "max_tokens": 600
    }).copy()
    
    # 根据内容类型和抑郁等级调整配置
    adjustments = CONFIG_ADJUSTMENTS.get(content_type, {}).get(depression_level, {})
    base_config.update(adjustments)
    
    return base_config

def get_provider_for_model(model: str) -> str:
    """获取模型对应的提供商"""
    return PROVIDER_MAP.get(model, "openai")

def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """
    估算API调用成本
    
    Args:
        model: 模型名称
        prompt_tokens: 输入token数
        completion_tokens: 输出token数
        
    Returns:
        float: 成本（美元）
    """
    model_config = ALL_MODELS.get(model, {})
    cost_info = model_config.get("cost_per_1k_tokens", {"input": 0.001, "output": 0.002})
    
    input_cost = (prompt_tokens / 1000) * cost_info["input"]
    output_cost = (completion_tokens / 1000) * cost_info["output"]
    
    return input_cost + output_cost

def get_available_models() -> Dict[str, list]:
    """获取所有可用模型按提供商分组"""
    providers = {}
    for model, provider in PROVIDER_MAP.items():
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(model)
    return providers
