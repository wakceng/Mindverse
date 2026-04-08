# -*- coding: utf-8 -*-
"""
统一的文本生成器
提供简洁的文本生成接口
"""

import os
from typing import Optional, Dict, Any

class TextGenerator:
    """统一的文本生成器，支持多种LLM提供商"""
    
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化文本生成器
        
        Args:
            model: 模型名称，如 "gpt-3.5-turbo", "gpt-4", "deepseek-chat", "gemini-pro"
            api_key: API密钥，如果为None则从环境变量获取
            base_url: API基础URL，如果为None则从环境变量获取
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        
        # 根据模型选择对应的客户端
        self._client = self._create_client()
    
    def _create_client(self):
        """根据模型名称创建对应的客户端"""
        from .openai_client import OpenAIClient
        return OpenAIClient(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url
        )
        # if self.model.startswith("gpt") or self.model.startswith("o1"):
        #     from .openai_client import OpenAIClient
        #     return OpenAIClient(
        #         model=self.model,
        #         api_key=self.api_key,
        #         base_url=self.base_url
        #     )
        # elif self.model.startswith("deepseek"):
        #     from .deepseek_client import DeepSeekClient
        #     return DeepSeekClient(
        #         model=self.model,
        #         api_key=self.api_key,
        #         base_url=self.base_url
        #     )
        # elif self.model.startswith("gemini"):
        #     from .gemini_client import GeminiClient
        #     return GeminiClient(
        #         model=self.model,
        #         api_key=self.api_key
        #     )
        # else:
        #     # 默认使用OpenAI客户端（兼容其他OpenAI兼容的模型）
        #     from .openai_client import OpenAIClient
        #     return OpenAIClient(
        #         model=self.model,
        #         api_key=self.api_key,
        #         base_url=self.base_url
        #     )
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本（简化接口）
        
        Args:
            prompt: 输入提示词
            **kwargs: 生成参数，如 temperature, max_tokens 等
            
        Returns:
            str: 生成的文本
            
        Raises:
            Exception: 当API调用失败时抛出异常
        """
        # 设置默认参数
        config = {
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "top_p": kwargs.get("top_p", 1.0)
        }
        
        # 添加其他参数
        for key, value in kwargs.items():
            if key not in config:
                config[key] = value
        
        # 调用底层客户端
        result = self._client.generate_text(prompt, config)
        
        # 检查结果
        if not result.get('success', False):
            error_msg = result.get('error', '未知错误')
            error_type = result.get('error_type', 'UnknownError')
            raise Exception(f"{error_type}: {error_msg}")
        
        content = result.get('content', '')
        if not content:
            raise Exception("API返回成功但内容为空")
            
        return content
    
    def generate_with_metadata(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        生成文本（完整接口，包含元数据）
        
        Args:
            prompt: 输入提示词
            **kwargs: 生成参数
            
        Returns:
            Dict[str, Any]: 包含内容和元数据的完整响应
        """
        config = {
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "top_p": kwargs.get("top_p", 1.0)
        }
        
        for key, value in kwargs.items():
            if key not in config:
                config[key] = value
        
        result = self._client.generate_text(prompt, config)
        
        if not result.get('success', False):
            error_msg = result.get('error', '未知错误')
            error_type = result.get('error_type', 'UnknownError')
            raise Exception(f"{error_type}: {error_msg}")
            
        return result
    
    def test_connection(self) -> bool:
        """
        测试连接是否正常
        
        Returns:
            bool: 连接是否正常
        """
        try:
            response = self.generate("Hello", max_tokens=10)
            return bool(response and response.strip())
        except Exception:
            return False
    
    @classmethod
    def create_from_env(cls, model: str = "gpt-3.5-turbo") -> "TextGenerator":
        """
        从环境变量创建文本生成器，自动检测代理配置
        
        Args:
            model: 模型名称
            
        Returns:
            TextGenerator: 文本生成器实例
        """
        # 根据模型类型获取对应的API密钥和基础URL
        if model.startswith("gpt") or model.startswith("o1"):
            api_key = os.getenv("OPENAI_API_KEY")
            # 优先使用代理，提高可用性
            base_url = (
                os.getenv("OPENAI_PROXY_BASE_URL") or  # 代理优先
                os.getenv("OPENAI_BASE_URL") or       # 自定义URL
                "https://api.openai.com/v1"           # 默认URL
            )
            # 打印代理使用情况
            if os.getenv("OPENAI_PROXY_BASE_URL"):
                print(f"🔗 使用OpenAI代理: {base_url}")
            elif os.getenv("OPENAI_BASE_URL"):
                print(f"🔗 使用自定义OpenAI URL: {base_url}")
            else:
                print(f"🔗 使用默认OpenAI URL: {base_url}")
                
        elif model.startswith("deepseek"):
            api_key = os.getenv("DEEPSEEK_API_KEY")
            base_url = os.getenv("DEEPSEEK_BASE_URL") or "https://api.deepseek.com/v1"
            if os.getenv("DEEPSEEK_BASE_URL"):
                print(f"🔗 使用自定义DeepSeek URL: {base_url}")
            else:
                print(f"🔗 使用默认DeepSeek URL: {base_url}")
                
        elif model.startswith("gemini"):
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            base_url = None  # Gemini doesn't use base_url
            print(f"🔗 使用Gemini API")
            
        else:
            # 默认使用OpenAI配置（兼容其他OpenAI兼容的模型）
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = (
                os.getenv("OPENAI_PROXY_BASE_URL") or
                os.getenv("OPENAI_BASE_URL") or
                "https://api.openai.com/v1"
            )
            print(f"🔗 使用OpenAI兼容接口: {base_url}")
        
        if not api_key:
            raise ValueError(f"未找到模型 {model} 对应的API密钥！请设置相应的环境变量")
        
        return cls(model=model, api_key=api_key, base_url=base_url)
    
    def __str__(self) -> str:
        return f"TextGenerator(model={self.model})"
    
    def __repr__(self) -> str:
        return self.__str__()
