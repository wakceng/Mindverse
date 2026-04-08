# -*- coding: utf-8 -*-
"""
OpenAI客户端实现
支持OpenAI v1.0+ 和旧版本API，支持代理配置
"""

import os
from typing import Dict, Any, Optional
from .base_client import BaseLLMClient

class OpenAIClient(BaseLLMClient):
    """OpenAI API客户端"""
    
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化OpenAI客户端
        
        Args:
            model: 模型名称
            api_key: API密钥
            base_url: 自定义API基础URL（支持代理）
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("未找到OpenAI API密钥！请设置OPENAI_API_KEY环境变量")
            
        super().__init__(model, api_key)
        
        # 设置基础URL，支持代理
        if base_url is None:
            base_url = (
                os.getenv("OPENAI_BASE_URL") or 
                os.getenv("OPENAI_PROXY_BASE_URL") or 
                "https://api.openai.com/v1"
            )
        
        self.base_url = base_url
        
        # 尝试导入和初始化OpenAI客户端
        try:
            import openai
            # 检查是否是新版本 (v1.0+)
            if hasattr(openai, 'OpenAI'):
                self.use_new_api = True
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                print(f"🔗 使用新版OpenAI API，代理地址: {self.base_url}")
            else:
                # 旧版本API
                self.use_new_api = False
                import openai as openai_legacy
                openai_legacy.api_key = self.api_key
                openai_legacy.api_base = self.base_url
                self.openai_legacy = openai_legacy
                print(f"🔗 使用旧版OpenAI API，代理地址: {self.base_url}")
        except ImportError:
            raise ImportError("未找到openai库！请运行：pip install openai")
            
    def _get_provider(self) -> str:
        return "openai"
    
    def _generate_text(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """使用OpenAI API生成文本"""
        try:
            if self.use_new_api:
                # 使用新版本API (v1.0+)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    **config
                )
                
                generated_text = response.choices[0].message.content
                if generated_text:
                    generated_text = generated_text.strip()
                else:
                    generated_text = ""
                
                # 计算成本估算
                cost_estimate = self._estimate_cost(
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
                
                return {
                    "success": True,
                    "content": generated_text,
                    "metadata": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                        "finish_reason": response.choices[0].finish_reason,
                        "cost_estimate_usd": cost_estimate,
                        "config": config,
                        "model": self.model,
                        "base_url": self.base_url
                    }
                }
            else:
                # 使用旧版本API
                response = self.openai_legacy.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    **config
                )
                
                generated_text = response.choices[0].message.content
                if generated_text:
                    generated_text = generated_text.strip()
                else:
                    generated_text = ""
                
                # 计算成本估算
                cost_estimate = self._estimate_cost(
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
                
                return {
                    "success": True,
                    "content": generated_text,
                    "metadata": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                        "finish_reason": response.choices[0].finish_reason,
                        "cost_estimate_usd": cost_estimate,
                        "config": config,
                        "model": self.model,
                        "base_url": self.base_url
                    }
                }
                
        except Exception as e:
            raise e
    
    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """估算OpenAI API成本"""
        # 这里可以根据具体模型计算成本
        cost_map = {
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03}
        }
        
        rates = cost_map.get(self.model, {"input": 0.001, "output": 0.002})
        
        input_cost = (prompt_tokens / 1000) * rates["input"]
        output_cost = (completion_tokens / 1000) * rates["output"]
        
        return input_cost + output_cost
