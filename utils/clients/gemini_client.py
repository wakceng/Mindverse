# -*- coding: utf-8 -*-
"""
Gemini客户端实现
"""

import os
from typing import Dict, Any, Optional
from .base_client import BaseLLMClient

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

class GeminiClient(BaseLLMClient):
    """Google Gemini API客户端"""
    
    def __init__(self, model: str = "gemini-pro", api_key: Optional[str] = None):
        """
        初始化Gemini客户端
        
        Args:
            model: 模型名称
            api_key: API密钥
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("需要安装google-generativeai包: pip install google-generativeai")
            
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("未找到Gemini API密钥！请设置GEMINI_API_KEY环境变量")
            
        super().__init__(model, api_key)
        
        # 配置Gemini
        genai.configure(api_key=self.api_key)
        self.model_instance = genai.GenerativeModel(self.model)
            
    def _get_provider(self) -> str:
        return "gemini"
    
    def _generate_text(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """使用Gemini API生成文本"""
        try:
            # 转换配置参数
            generation_config = {
                "temperature": config.get("temperature", 0.8),
                "top_p": config.get("top_p", 0.9),
                "top_k": config.get("top_k", 40),
                "max_output_tokens": config.get("max_tokens", 800),
            }
            
            response = self.model_instance.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(**generation_config)
            )
            
            if not response.text:
                raise ValueError("Gemini模型没有返回文本内容")
            
            # Gemini不直接提供token使用量，使用估算
            prompt_tokens = len(prompt.split()) * 1.3  # 粗略估算
            completion_tokens = len(response.text.split()) * 1.3
            total_tokens = prompt_tokens + completion_tokens
            
            cost_estimate = self._estimate_cost(int(prompt_tokens), int(completion_tokens))
            
            return {
                "success": True,
                "content": response.text.strip(),
                "metadata": {
                    "prompt_tokens": int(prompt_tokens),
                    "completion_tokens": int(completion_tokens),
                    "total_tokens": int(total_tokens),
                    "finish_reason": "stop",
                    "cost_estimate_usd": cost_estimate,
                    "config": generation_config
                }
            }
            
        except Exception as e:
            raise e
    
    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """估算Gemini API成本"""
        # Gemini的成本结构（示例数值）
        cost_map = {
            "gemini-pro": {"input": 0.0005, "output": 0.0015},
            "gemini-pro-vision": {"input": 0.0025, "output": 0.01}
        }
        
        rates = cost_map.get(self.model, {"input": 0.0005, "output": 0.0015})
        
        input_cost = (prompt_tokens / 1000) * rates["input"]
        output_cost = (completion_tokens / 1000) * rates["output"]
        
        return input_cost + output_cost
