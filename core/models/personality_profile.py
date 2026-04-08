# -*- coding: utf-8 -*-
"""
人格特质模块
管理Big Five人格特质相关功能
"""

import random
from typing import Dict, Optional
from config import PERSONALITY_TRAITS, DEPRESSION_PERSONALITY_TENDENCIES


class PersonalityProfile:
    """
    人格特质档案类
    
    管理Big Five人格特质：外向性、宜人性、责任心、神经质、开放性
    """
    
    def __init__(self, depression_level: str, personality: Optional[Dict[str, int]] = None):
        """
        初始化人格特质档案
        
        Args:
            depression_level: 抑郁等级
            personality: 指定的人格特质字典，如果为None则根据抑郁等级生成
        """
        self.depression_level = depression_level
        
        if personality:
            self.personality = personality.copy()
            self._validate_personality()
        else:
            self.personality = self._generate_personality()
    
    def _validate_personality(self):
        """验证人格特质数据的有效性"""
        for trait in PERSONALITY_TRAITS:
            if trait not in self.personality:
                self.personality[trait] = random.randint(1, 5)
            else:
                # 确保分数在1-5范围内
                self.personality[trait] = max(1, min(5, self.personality[trait]))
    
    def _generate_personality(self) -> Dict[str, int]:
        """根据抑郁等级生成人格特质"""
        personality = {}
        
        # 获取抑郁等级对应的人格倾向
        if self.depression_level in DEPRESSION_PERSONALITY_TENDENCIES:
            tendencies = DEPRESSION_PERSONALITY_TENDENCIES[self.depression_level]
            
            for trait in PERSONALITY_TRAITS:
                if trait in tendencies:
                    # 在倾向范围内随机生成
                    min_val, max_val = tendencies[trait]
                    personality[trait] = random.randint(min_val, max_val)
                else:
                    # 没有特定倾向，随机生成
                    personality[trait] = random.randint(1, 5)
        else:
            # 默认随机生成
            for trait in PERSONALITY_TRAITS:
                personality[trait] = random.randint(1, 5)
        
        return personality
    
    def get_personality_description(self) -> str:
        """生成人格特质的文字描述"""
        descriptions = []
        
        # 外向性
        if self.personality.get("外向性", 3) >= 4:
            descriptions.append("性格外向、活泼")
        elif self.personality.get("外向性", 3) <= 2:
            descriptions.append("性格内向、安静")
        else:
            descriptions.append("性格适中")
        
        # 宜人性
        if self.personality.get("宜人性", 3) >= 4:
            descriptions.append("友善、合作")
        elif self.personality.get("宜人性", 3) <= 2:
            descriptions.append("比较独立、竞争性强")
        
        # 责任心
        if self.personality.get("责任心", 3) >= 4:
            descriptions.append("有条理、负责任")
        elif self.personality.get("责任心", 3) <= 2:
            descriptions.append("随性、灵活")
        
        # 神经质
        if self.personality.get("神经质", 3) >= 4:
            descriptions.append("情绪敏感、容易焦虑")
        elif self.personality.get("神经质", 3) <= 2:
            descriptions.append("情绪稳定、抗压能力强")
        
        # 开放性
        if self.personality.get("开放性", 3) >= 4:
            descriptions.append("思维开放、富有创造力")
        elif self.personality.get("开放性", 3) <= 2:
            descriptions.append("务实、传统")
        
        return "、".join(descriptions)
    
    def get_summary(self) -> Dict[str, any]:
        """获取人格特质摘要"""
        return {
            "personality_scores": self.personality,
            "description": self.get_personality_description(),
            "depression_level": self.depression_level
        }


def get_personality_description(personality: Dict[str, int]) -> str:
    """
    获取人格特质描述（向后兼容函数）
    
    Args:
        personality: 人格特质字典
        
    Returns:
        str: 人格特质描述
    """
    profile = PersonalityProfile("正常", personality)
    return profile.get_personality_description()
