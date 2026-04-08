# -*- coding: utf-8 -*-
"""
基础LLM客户端抽象类
定义所有LLM客户端的通用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time

class BaseLLMClient(ABC):
    """LLM客户端基类"""
    
    def __init__(self, model: str, api_key: str):
        """
        初始化基础客户端
        
        Args:
            model: 模型名称
            api_key: API密钥
        """
        self.model = model
        self.api_key = api_key
        self.provider = self._get_provider()
        
    @abstractmethod
    def _get_provider(self) -> str:
        """获取提供商名称"""
        pass
    
    @abstractmethod
    def _generate_text(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成文本的核心方法
        
        Args:
            prompt: 输入提示词
            config: 生成配置
            
        Returns:
            dict: 生成结果
        """
        pass
    
    def generate_text(self, prompt: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        统一的文本生成接口
        
        Args:
            prompt: 输入提示词
            config: 生成配置
            
        Returns:
            dict: 标准格式的生成结果
        """
        if config is None:
            config = self._get_default_config()
            
        try:
            start_time = time.time()
            result = self._generate_text(prompt, config)
            end_time = time.time()
            
            if result.get("success", False):
                result["metadata"]["generation_time"] = end_time - start_time
                result["metadata"]["provider"] = self.provider
                result["metadata"]["model"] = self.model
                
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "temperature": 0.8,
            "max_tokens": 600,
            "top_p": 0.9
        }
    
    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        估算API调用成本
        
        Args:
            prompt_tokens: 输入token数
            completion_tokens: 输出token数
            
        Returns:
            float: 成本估算（美元）
        """
        # 子类可以重写此方法提供更准确的成本估算
        return 0.0
