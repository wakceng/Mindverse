# -*- coding: utf-8 -*-
"""
DeepSeek客户端实现
"""

import openai
import os
from typing import Dict, Any, Optional
from .base_client import BaseLLMClient

class DeepSeekClient(BaseLLMClient):
    """DeepSeek API客户端（使用OpenAI兼容接口）"""
    
    def __init__(self, model: str = "deepseek-chat", api_key: Optional[str] = None):
        """
        初始化DeepSeek客户端
        
        Args:
            model: 模型名称
            api_key: API密钥
        """
        if api_key is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")
        
        if not api_key:
            raise ValueError("未找到DeepSeek API密钥！请设置DEEPSEEK_API_KEY环境变量")
            
        super().__init__(model, api_key)
        
        # 设置DeepSeek配置
        openai.api_key = self.api_key
        openai.api_base = "https://api.deepseek.com/v1"
            
    def _get_provider(self) -> str:
        return "deepseek"
    
    def _generate_text(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """使用DeepSeek API生成文本"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **config
            )
            
            generated_text = response.choices[0].message.content.strip()
            
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
                    "config": config
                }
            }
            
        except Exception as e:
            raise e
    
    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """估算DeepSeek API成本"""
        # DeepSeek的成本相对较低
        cost_map = {
            "deepseek-chat": {"input": 0.0001, "output": 0.0002},
            "deepseek-coder": {"input": 0.0001, "output": 0.0002}
        }
        
        rates = cost_map.get(self.model, {"input": 0.0001, "output": 0.0002})
        
        input_cost = (prompt_tokens / 1000) * rates["input"]
        output_cost = (completion_tokens / 1000) * rates["output"]
        
        return input_cost + output_cost
