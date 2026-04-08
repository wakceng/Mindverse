# -*- coding: utf-8 -*-
"""
心理状态模块
管理认知概念化相关功能
"""

import random
from typing import Optional
from config import (
    CORE_BELIEFS, INTERMEDIATE_BELIEFS, DEPRESSED_BELIEFS, COPING_STRATEGIES,
    HEALTHY_CORE_BELIEFS, HEALTHY_INTERMEDIATE_BELIEFS, HEALTHY_COPING_STRATEGIES,
    DEPRESSION_PSYCHOLOGICAL_PROFILES
)


class PsychologicalState:
    """
    心理状态类
    
    管理认知概念化：核心信念、中间信念、抑郁相关信念、应对策略
    """
    
    def __init__(self, 
                 depression_level: str,
                 depression_tag: str,
                 core_belief: Optional[str] = None,
                 intermediate_belief: Optional[str] = None,
                 depressed_belief: Optional[str] = None,
                 coping_strategy: Optional[str] = None):
        """
        初始化心理状态
        
        Args:
            depression_level: 抑郁等级
            depression_tag: 抑郁标签 ("抑郁"/"非抑郁")
            core_belief: 指定的核心信念
            intermediate_belief: 指定的中间信念
            depressed_belief: 指定的抑郁相关信念
            coping_strategy: 指定的应对策略
        """
        self.depression_level = depression_level
        self.depression_tag = depression_tag
        
        # 生成认知特征
        if depression_tag == "非抑郁":
            self._init_healthy_cognition(core_belief, intermediate_belief, coping_strategy)
        else:
            self._init_depressed_cognition(core_belief, intermediate_belief, 
                                         depressed_belief, coping_strategy)
    
    def _init_healthy_cognition(self, core_belief: Optional[str], 
                               intermediate_belief: Optional[str], 
                               coping_strategy: Optional[str]):
        """初始化健康人群的认知特征"""
        self.core_belief = core_belief or random.choice(HEALTHY_CORE_BELIEFS)
        self.intermediate_belief = intermediate_belief or random.choice(HEALTHY_INTERMEDIATE_BELIEFS)
        self.depressed_belief = None  # 健康人群没有抑郁相关信念
        self.coping_strategy = coping_strategy or random.choice(HEALTHY_COPING_STRATEGIES)
    
    def _init_depressed_cognition(self, core_belief: Optional[str], 
                                 intermediate_belief: Optional[str], 
                                 depressed_belief: Optional[str], 
                                 coping_strategy: Optional[str]):
        """初始化抑郁人群的认知特征"""
        
        # 尝试使用分层配置
        if self.depression_level in DEPRESSION_PSYCHOLOGICAL_PROFILES:
            profile = DEPRESSION_PSYCHOLOGICAL_PROFILES[self.depression_level]
            
            self.core_belief = core_belief or random.choice(
                profile.get("core_beliefs", CORE_BELIEFS)
            )
            self.coping_strategy = coping_strategy or random.choice(
                profile.get("coping_strategies", COPING_STRATEGIES)
            )
        else:
            # 使用通用配置
            self.core_belief = core_belief or random.choice(CORE_BELIEFS)
            self.coping_strategy = coping_strategy or random.choice(COPING_STRATEGIES)
        
        self.intermediate_belief = intermediate_belief or random.choice(INTERMEDIATE_BELIEFS)
        self.depressed_belief = depressed_belief or random.choice(DEPRESSED_BELIEFS)
    
    def get_cognitive_features(self) -> dict:
        """获取认知特征字典"""
        features = {
            "核心信念": self.core_belief,
            "中间信念": self.intermediate_belief,
            "应对策略": self.coping_strategy
        }
        
        # 只有抑郁人群才有抑郁相关信念
        if self.depression_tag != "非抑郁" and self.depressed_belief:
            features["抑郁时信念"] = self.depressed_belief
        
        return features
    
    def get_summary(self) -> dict:
        """获取心理状态摘要"""
        return {
            "depression_level": self.depression_level,
            "depression_tag": self.depression_tag,
            "cognitive_features": self.get_cognitive_features()
        }


def get_cognitive_features(depression_tag: str, depression_level: str, 
                          core_belief: str, intermediate_belief: str, 
                          depressed_belief: str, coping_strategy: str) -> dict:
    """
    获取认知特征（向后兼容函数）
    
    Args:
        depression_tag: 抑郁标签
        depression_level: 抑郁等级  
        core_belief: 核心信念
        intermediate_belief: 中间信念
        depressed_belief: 抑郁相关信念
        coping_strategy: 应对策略
        
    Returns:
        dict: 认知特征字典
    """
    state = PsychologicalState(
        depression_level=depression_level,
        depression_tag=depression_tag,
        core_belief=core_belief,
        intermediate_belief=intermediate_belief,
        depressed_belief=depressed_belief,
        coping_strategy=coping_strategy
    )
    
    return {
        "core_belief": state.core_belief,
        "intermediate_belief": state.intermediate_belief,
        "depressed_belief": state.depressed_belief,
        "coping_strategy": state.coping_strategy
    }
