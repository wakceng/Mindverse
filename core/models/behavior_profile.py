# -*- coding: utf-8 -*-
"""
行为档案模块
管理语言特征和情绪行为相关功能
"""

import random
from typing import Optional
from config import (
    LANGUAGE_STYLES, EXPRESSION_TONES, HIDING_TENDENCIES,
    MAIN_EMOTIONS, AUTOMATIC_THOUGHTS, TYPICAL_BEHAVIORS,
    DEPRESSION_LEVEL_EMOTIONS, DEPRESSION_LEVEL_THOUGHTS, DEPRESSION_LEVEL_BEHAVIORS,
    HEALTHY_MAIN_EMOTIONS, HEALTHY_AUTOMATIC_THOUGHTS, HEALTHY_TYPICAL_BEHAVIORS,
    DEPRESSION_PSYCHOLOGICAL_PROFILES
)


class BehaviorProfile:
    """
    行为档案类
    
    管理语言特征和情绪行为：语言风格、表达语调、隐藏倾向、主要情绪、自动思维、典型行为
    """
    
    def __init__(self,
                 depression_level: str,
                 depression_tag: str,
                 language_style: Optional[str] = None,
                 expression_tone: Optional[str] = None,
                 hiding_tendency: Optional[str] = None,
                 main_emotion: Optional[str] = None,
                 automatic_thought: Optional[str] = None,
                 typical_behavior: Optional[str] = None):
        """
        初始化行为档案
        
        Args:
            depression_level: 抑郁等级
            depression_tag: 抑郁标签
            language_style: 语言风格
            expression_tone: 表达语调
            hiding_tendency: 隐藏倾向
            main_emotion: 主要情绪
            automatic_thought: 自动思维
            typical_behavior: 典型行为
        """
        self.depression_level = depression_level
        self.depression_tag = depression_tag
        
        # 初始化语言特征
        self._init_language_features(language_style, expression_tone, hiding_tendency)
        
        # 初始化情绪行为
        self._init_emotional_behavior(main_emotion, automatic_thought, typical_behavior)
    
    def _init_language_features(self, language_style: Optional[str], 
                               expression_tone: Optional[str], 
                               hiding_tendency: Optional[str]):
        """初始化语言特征"""
        
        # 语言风格
        self.language_style = language_style or random.choice(LANGUAGE_STYLES)
        
        # 表达语调
        self.expression_tone = expression_tone or random.choice(EXPRESSION_TONES)
        
        # 隐藏倾向
        if hiding_tendency == "隐藏自己的情况":
            self.hiding_tendency = "隐藏自己的情况"
        elif hiding_tendency == "可能隐藏自己的情况":
            self.hiding_tendency = random.choice(HIDING_TENDENCIES)
        elif hiding_tendency:
            self.hiding_tendency = hiding_tendency
        else:
            self.hiding_tendency = "开放表达"  # 默认值
    
    def _init_emotional_behavior(self, main_emotion: Optional[str], 
                                automatic_thought: Optional[str], 
                                typical_behavior: Optional[str]):
        """初始化情绪行为"""
        
        if self.depression_tag == "非抑郁":
            self._init_healthy_behavior(main_emotion, automatic_thought, typical_behavior)
        else:
            self._init_depressed_behavior(main_emotion, automatic_thought, typical_behavior)
    
    def _init_healthy_behavior(self, main_emotion: Optional[str], 
                              automatic_thought: Optional[str], 
                              typical_behavior: Optional[str]):
        """初始化健康人群的情绪行为"""
        self.main_emotion = main_emotion or random.choice(HEALTHY_MAIN_EMOTIONS)
        self.automatic_thought = automatic_thought or random.choice(HEALTHY_AUTOMATIC_THOUGHTS)
        self.typical_behavior = typical_behavior or random.choice(HEALTHY_TYPICAL_BEHAVIORS)
    
    def _init_depressed_behavior(self, main_emotion: Optional[str], 
                               automatic_thought: Optional[str], 
                               typical_behavior: Optional[str]):
        """初始化抑郁人群的情绪行为"""
        
        # 尝试使用分层配置
        if self.depression_level in DEPRESSION_LEVEL_EMOTIONS:
            emotion_pool = DEPRESSION_LEVEL_EMOTIONS[self.depression_level]
        elif self.depression_level in DEPRESSION_PSYCHOLOGICAL_PROFILES:
            emotion_pool = DEPRESSION_PSYCHOLOGICAL_PROFILES[self.depression_level].get(
                "emotions", MAIN_EMOTIONS
            )
        else:
            emotion_pool = MAIN_EMOTIONS
        
        if self.depression_level in DEPRESSION_LEVEL_THOUGHTS:
            thought_pool = DEPRESSION_LEVEL_THOUGHTS[self.depression_level]
        else:
            thought_pool = AUTOMATIC_THOUGHTS
        
        if self.depression_level in DEPRESSION_LEVEL_BEHAVIORS:
            behavior_pool = DEPRESSION_LEVEL_BEHAVIORS[self.depression_level]
        else:
            behavior_pool = TYPICAL_BEHAVIORS
        
        self.main_emotion = main_emotion or random.choice(emotion_pool)
        self.automatic_thought = automatic_thought or random.choice(thought_pool)
        self.typical_behavior = typical_behavior or random.choice(behavior_pool)
    
    def get_language_description(self) -> str:
        """获取语言特征描述"""
        return f"语言风格: {self.language_style}，表达语调: {self.expression_tone}，隐藏倾向: {self.hiding_tendency}"
    
    def get_behavior_description(self) -> str:
        """获取行为特征描述"""
        return f"典型行为: {self.typical_behavior}"
    
    def get_summary(self) -> dict:
        """获取行为档案摘要"""
        return {
            "language_features": {
                "语言风格": self.language_style,
                "表达语调": self.expression_tone,
                "隐藏倾向": self.hiding_tendency
            },
            "emotional_behavior": {
                "主要情绪": self.main_emotion,
                "自动思维": self.automatic_thought,
                "典型行为": self.typical_behavior
            },
            "descriptions": {
                "language": self.get_language_description(),
                "behavior": self.get_behavior_description()
            }
        }


def get_behavior_description(typical_behavior: str) -> str:
    """
    获取行为描述（向后兼容函数）
    
    Args:
        typical_behavior: 典型行为
        
    Returns:
        str: 行为描述
    """
    return f"典型行为: {typical_behavior}"
