# -*- coding: utf-8 -*-
"""
患者Agent基础模型
重构后的核心Agent类，更清晰的代码结构
"""

import random
import json
import uuid
from typing import Dict, Any, Optional, Union
from datetime import datetime

from config import *
from .models.personality_profile import PersonalityProfile
from .models.psychological_state import PsychologicalState
from .models.behavior_profile import BehaviorProfile
from utils.logging import PatientLogger
from utils.generators import PromptGenerator


class PatientAgent:
    """
    患者Agent主类
    
    这个类代表一个虚拟的患者，具有完整的心理档案和行为特征。
    可以用于生成自述内容、社交媒体发言等文本数据。
    """
    
    def __init__(self, 
                 # 基本信息
                 age: Optional[int] = None,
                 gender: Optional[str] = None,
                 education: Optional[str] = None,
                 occupation: Optional[str] = None,
                 marital_status: Optional[str] = None,
                 
                 # 心理状态
                 depression_level: Optional[str] = None,
                 questionnaire_type: str = "PHQ-9",
                 questionnaire_score: Optional[int] = None,
                 
                 # 人格特质
                 personality: Optional[Dict[str, int]] = None,
                 
                 # 语言特征
                 language_style: Optional[str] = None,
                 expression_tone: Optional[str] = None,
                 hiding_tendency: Optional[str] = None,
                 
                 # 认知概念化
                 core_belief: Optional[str] = None,
                 intermediate_belief: Optional[str] = None,
                 depressed_belief: Optional[str] = None,
                 coping_strategy: Optional[str] = None,
                 
                 # 情绪行为
                 main_emotion: Optional[str] = None,
                 automatic_thought: Optional[str] = None,
                 typical_behavior: Optional[str] = None,
                 
                 # 系统参数
                 patient_id: Optional[str] = None,
                 enable_logging: bool = True):
        """
        初始化患者Agent
        
        Args:
            age: 年龄 (13-39)
            gender: 性别 ("男"/"女"/"非二元")
            education: 教育程度 ("初中"/"高中"/"本科"/"硕士"/"博士")
            occupation: 职业状态 ("学生"/"办公室职员"/"无业"/"自由职业者")
            marital_status: 婚姻状况 ("单身"/"恋爱"/"已婚"/"离异")
            depression_level: 抑郁等级 ("正常"/"轻度"/"中度"/"重度")
            questionnaire_type: 量表类型 ("PHQ-9"/"SDS")
            questionnaire_score: 量表评分
            personality: Big Five人格特质字典
            language_style: 语言风格
            expression_tone: 表达语调
            hiding_tendency: 隐藏倾向
            core_belief: 核心信念
            intermediate_belief: 中间信念
            depressed_belief: 抑郁相关信念
            coping_strategy: 应对策略
            main_emotion: 主要情绪
            automatic_thought: 自动思维
            typical_behavior: 典型行为
            patient_id: 患者ID
            enable_logging: 是否启用日志记录
        """
        
        # 系统参数
        self.patient_id = patient_id or f"patient_{uuid.uuid4().hex[:8]}"
        self.questionnaire_type = questionnaire_type
        self.enable_logging = enable_logging
        
        # 初始化基本信息
        self._init_basic_info(age, gender, education, occupation, marital_status)
        
        # 初始化心理状态
        self._init_psychological_state(depression_level, questionnaire_score)
        
        # 初始化各个组件
        self.personality_profile = PersonalityProfile(
            depression_level=self.depression_level,
            personality=personality
        )
        
        self.psychological_state = PsychologicalState(
            depression_level=self.depression_level,
            depression_tag=self.depression_tag,
            core_belief=core_belief,
            intermediate_belief=intermediate_belief,
            depressed_belief=depressed_belief,
            coping_strategy=coping_strategy
        )
        
        self.behavior_profile = BehaviorProfile(
            depression_level=self.depression_level,
            depression_tag=self.depression_tag,
            language_style=language_style,
            expression_tone=expression_tone,
            hiding_tendency=hiding_tendency,
            main_emotion=main_emotion,
            automatic_thought=automatic_thought,
            typical_behavior=typical_behavior
        )
        
        # 生成并保存分项分数，用于测试时的预设答案
        self._init_item_scores()
        
        # 初始化固定的提示词参数，确保稳定性测试时的一致性
        self._init_prompt_parameters()
        
        # 初始化工具
        self.prompt_generator = PromptGenerator(self)
        
        # 初始化日志记录器
        if self.enable_logging:
            self.logger = PatientLogger(self.patient_id)
            # 保存患者档案
            self.save_profile()
        else:
            self.logger = None
    
    def _init_basic_info(self, age: Optional[int], gender: Optional[str], 
                        education: Optional[str], occupation: Optional[str], 
                        marital_status: Optional[str]):
        """初始化基本人口统计学信息"""
        
        # 年龄
        self.age = age if age is not None else random.randint(MIN_AGE, MAX_AGE)
        
        # 性别
        self.gender = gender or random.choice(GENDERS)
        
        # 教育程度（考虑年龄约束）
        if education:
            self.education = education
        else:
            valid_educations = DATA_GENERATION_CONSTRAINTS["age_education_mapping"].get(
                self.age, EDUCATION_LEVELS
            )
            self.education = random.choice(valid_educations)
        
        # 职业状态（考虑年龄和教育约束）
        if occupation:
            self.occupation = occupation
        else:
            # 根据年龄确定可能的职业
            valid_occupations = []
            for age_range, occupations in DATA_GENERATION_CONSTRAINTS["age_occupation_mapping"].items():
                if age_range[0] <= self.age <= age_range[1]:
                    valid_occupations.extend(occupations)
            
            # 根据教育程度进一步筛选
            education_occupations = DATA_GENERATION_CONSTRAINTS["education_occupation_constraints"].get(
                self.education, OCCUPATION_STATUS
            )
            
            # 取交集
            valid_occupations = list(set(valid_occupations) & set(education_occupations))
            if not valid_occupations:
                valid_occupations = OCCUPATION_STATUS
            
            self.occupation = random.choice(valid_occupations)
        
        # 婚姻状况
        self.marital_status = marital_status or random.choice(MARITAL_STATUS)
    
    def _init_psychological_state(self, depression_level: Optional[str], 
                                 questionnaire_score: Optional[int]):
        """初始化心理状态信息"""
        
        # 确定抑郁等级
        if depression_level:
            self.depression_level = depression_level
        else:
            # 随机选择，70%概率选择抑郁，30%选择正常
            if random.random() < 0.6:
                self.depression_level = random.choice(DEPRESSED_LEVELS)
            else:
                self.depression_level = random.choice(NON_DEPRESSED_LEVELS)
        
        # 确定抑郁标签
        if self.depression_level in NON_DEPRESSED_LEVELS:
            self.depression_tag = "非抑郁"
        else:
            self.depression_tag = "抑郁"
        
        # 确定量表评分
        if questionnaire_score is not None:
            self.score = questionnaire_score
        else:
            if self.questionnaire_type == "PHQ-9":
                score_range = PHQ9_SCORE_RANGES[self.depression_level]
            else:  # SDS
                score_range = SDS_SCORE_RANGES[self.depression_level]
            
            self.score = random.randint(score_range[0], score_range[1])
    
    def _init_item_scores(self):
        """初始化分项分数，用于测试时的预设答案"""
        item_scores = self._generate_fixed_item_scores()
        
        # 存储分项分数字典供后续使用
        self.item_scores = item_scores
        
        if self.questionnaire_type == "PHQ-9":
            # 将字典转换为列表（按问题ID顺序）
            self.phq9_scores = [item_scores.get(i, 0) for i in range(1, 10)]  # PHQ-9有9个问题
            # 确保分项分数总和等于总分
            actual_sum = sum(self.phq9_scores)
            if actual_sum != self.score:
                self.score = actual_sum  # 以分项分数总和为准
        elif self.questionnaire_type == "SDS":
            # 将字典转换为列表（按问题ID顺序）
            self.sds_scores = [item_scores.get(i, 1) for i in range(1, 21)]  # SDS有20个问题
            # 确保标准分总和等于总分
            raw_sum = sum(self.sds_scores)
            standard_score = int(raw_sum * 1.25)
            if standard_score != self.score:
                self.score = standard_score  # 以分项分数计算的标准分为准
    
    def _init_prompt_parameters(self):
        """
        初始化固定的提示词参数，确保稳定性测试时的一致性
        这些参数在Agent创建时就确定，之后不再改变
        """
        # 固定场景、风格和时间维度
        self.fixed_scenario = random.choice(list(PROMPT_SCENARIOS.keys()))
        self.fixed_style = random.choice(list(EXPRESSION_STYLES.keys()))
        self.fixed_time_perspective = random.choice(list(TIME_PERSPECTIVES.keys()))
        
        # 从选定场景的选项中固定选择一个具体描述
        self.fixed_scenario_prompt = random.choice(PROMPT_SCENARIOS[self.fixed_scenario])
        
        # 固定历史模板选择逻辑
        if self.depression_tag == "非抑郁":
            self.fixed_history_templates = HEALTHY_HISTORY_TEMPLATES
            self.fixed_use_level_specific = False
        else:
            # 根据抑郁等级选择更有针对性的历史模板
            if self.depression_level in DEPRESSION_LEVEL_HISTORIES:
                # 70%概率使用分层模板，30%概率使用全部模板（保持多样性）
                if random.random() < 0.7:
                    self.fixed_history_templates = DEPRESSION_LEVEL_HISTORIES[self.depression_level]
                    self.fixed_use_level_specific = True
                else:
                    self.fixed_history_templates = PATIENT_HISTORY_TEMPLATES
                    self.fixed_use_level_specific = False
            else:
                self.fixed_history_templates = PATIENT_HISTORY_TEMPLATES
                self.fixed_use_level_specific = False
        
        # 从历史模板中固定选择一个
        self.fixed_personal_history = random.choice(self.fixed_history_templates)
        
        # 固定情境触发器选择
        if self.depression_tag != "非抑郁" and self.depression_level in SITUATIONAL_TRIGGERS:
            if random.random() < 0.1:  # 10%概率添加特定触发器
                trigger_options = SITUATIONAL_TRIGGERS[self.depression_level]
                trigger_key = random.choice(list(trigger_options.keys()))
                self.fixed_situational_trigger = f"\n【特定关注点】\n{trigger_options[trigger_key]}\n"
            else:
                self.fixed_situational_trigger = ""
        else:
            self.fixed_situational_trigger = ""
        
        # 缓存生成的提示词（用于稳定性测试）
        self._cached_test_prompt = None
    
    @property
    def personality(self) -> Dict[str, int]:
        """获取人格特质"""
        return self.personality_profile.personality
    
    @property
    def language_style(self) -> str:
        """获取语言风格"""
        return self.behavior_profile.language_style
    
    @property
    def expression_tone(self) -> str:
        """获取表达语调"""
        return self.behavior_profile.expression_tone
    
    @property
    def hiding_tendency(self) -> str:
        """获取隐藏倾向"""
        return self.behavior_profile.hiding_tendency
    
    @property
    def core_belief(self) -> str:
        """获取核心信念"""
        return self.psychological_state.core_belief
    
    @property
    def intermediate_belief(self) -> str:
        """获取中间信念"""
        return self.psychological_state.intermediate_belief
    
    @property
    def depressed_belief(self) -> str:
        """获取抑郁相关信念"""
        return self.psychological_state.depressed_belief
    
    @property
    def coping_strategy(self) -> str:
        """获取应对策略"""
        return self.psychological_state.coping_strategy
    
    @property
    def main_emotion(self) -> str:
        """获取主要情绪"""
        return self.behavior_profile.main_emotion
    
    @property
    def automatic_thought(self) -> str:
        """获取自动思维"""
        return self.behavior_profile.automatic_thought
    
    @property
    def typical_behavior(self) -> str:
        """获取典型行为"""
        return self.behavior_profile.typical_behavior
    
    def generate_self_description_prompt(self, scenario: Optional[str] = None,
                                       style: Optional[str] = None,
                                       time_perspective: Optional[str] = None) -> str:
        """
        生成自我状态阐述的提示词
        
        Args:
            scenario: 指定场景类型
            style: 指定表达风格
            time_perspective: 指定时间维度
            
        Returns:
            str: 完整的提示词
        """
        return self.prompt_generator.generate_self_description_prompt(
            scenario=scenario,
            style=style,
            time_perspective=time_perspective
        )
    
    def generate_social_post_prompt(self, platform: str = "微博",
                                  context: Optional[str] = None,
                                  post_type: Optional[str] = None) -> str:
        """
        生成社交媒体发言提示词
        
        Args:
            platform: 社交媒体平台
            context: 发言的上下文背景
            post_type: 指定发言类型
            
        Returns:
            str: 完整的提示词
        """
        return self.prompt_generator.generate_social_post_prompt(
            platform=platform,
            context=context,
            post_type=post_type
        )
    
    def generate_item_scores(self) -> Dict[int, int]:
        """
        获取已固定的量表分项分数
        
        Returns:
            Dict[int, int]: 分项分数字典，键为题目编号，值为分数
        """
        # 如果已经初始化了分项分数，直接返回
        if hasattr(self, 'item_scores'):
            return self.item_scores
        else:
            # 如果还没有初始化，生成并存储
            return self._generate_fixed_item_scores()
    
    def _generate_fixed_item_scores(self) -> Dict[int, int]:
        """
        生成固定的量表分项分数（仅在初始化时调用一次）
        
        Returns:
            Dict[int, int]: 分项分数字典，键为题目编号，值为分数
        """
        if self.questionnaire_type == "PHQ-9":
            return self._generate_phq9_item_scores()
        elif self.questionnaire_type == "SDS":
            return self._generate_sds_item_scores()
        else:
            return self._generate_phq9_item_scores()
    
    def _generate_phq9_item_scores(self) -> Dict[int, int]:
        """生成PHQ-9分项分数"""
        target_score = self.score
        num_items = 9
        
        # 先将所有项目设为0分
        scores = {i: 0 for i in range(1, num_items + 1)}
        remaining_score = target_score
        
        # 随机分配分数，确保总分匹配
        while remaining_score > 0:
            # 随机选择一个项目
            item = random.randint(1, num_items)
            # 如果该项目还能增加分数（最大3分）
            if scores[item] < 3:
                scores[item] += 1
                remaining_score -= 1
        
        return scores
    
    def _generate_sds_item_scores(self) -> Dict[int, int]:
        """生成SDS分项分数"""
        # SDS量表有20项，每项1-4分
        target_raw_score = int(self.score / 1.25)  # 标准分转原始分
        num_items = 20
        
        # 先将所有项目设为1分（SDS最低分是1）
        scores = {i: 1 for i in range(1, num_items + 1)}
        remaining_score = target_raw_score - num_items  # 减去已分配的基础分数
        
        # 随机分配剩余分数
        while remaining_score > 0:
            # 随机选择一个项目
            item = random.randint(1, num_items)
            # 如果该项目还能增加分数（最大4分）
            if scores[item] < 4:
                scores[item] += 1
                remaining_score -= 1
        
        return scores
    
    def get_basic_info(self) -> Dict[str, Any]:
        """获取基本信息"""
        return {
            "patient_id": self.patient_id,
            "age": self.age,
            "gender": self.gender,
            "education": self.education,
            "occupation": self.occupation,
            "marital_status": self.marital_status,
            "depression_level": self.depression_level,
            "depression_tag": self.depression_tag,
            "questionnaire_type": self.questionnaire_type,
            "score": self.score
        }
    
    def get_detailed_info(self) -> Dict[str, Any]:
        """获取详细信息"""
        return {
            **self.get_basic_info(),
            "personality": self.personality,
            "language_style": self.language_style,
            "expression_tone": self.expression_tone,
            "hiding_tendency": self.hiding_tendency,
            "core_belief": self.core_belief,
            "intermediate_belief": self.intermediate_belief,
            "depressed_belief": self.depressed_belief,
            "coping_strategy": self.coping_strategy,
            "main_emotion": self.main_emotion,
            "automatic_thought": self.automatic_thought,
            "typical_behavior": self.typical_behavior
        }
    
    def save_profile(self, file_path: Optional[str] = None) -> str:
        """
        保存患者档案到文件
        
        Args:
            file_path: 文件路径，如果为None则自动生成
            
        Returns:
            str: 保存的文件路径
        """
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"logs/{self.patient_id}/profile_{timestamp}.json"
        
        profile_data = {
            "basic_info": self.get_basic_info(),
            "detailed_info": self.get_detailed_info(),
            "created_at": datetime.now().isoformat()
        }
        
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def log_self_description_response(self, response: str, prompt_type: str = "self_description",
                                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        记录自我状态阐述的LLM响应
        
        Args:
            response: LLM生成的响应内容
            prompt_type: prompt类型
            metadata: 额外的元数据
            
        Returns:
            str: 日志文件路径
        """
        if self.logger:
            return self.logger.log_response(response, prompt_type, metadata)
        else:
            print(f"日志记录已禁用，响应内容: {response[:50]}...")
            return ""
    
    def log_social_post_response(self, response: str, platform: str = "微博",
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        记录社交媒体发言的LLM响应
        
        Args:
            response: LLM生成的响应内容
            platform: 社交媒体平台
            metadata: 额外的元数据
            
        Returns:
            str: 日志文件路径
        """
        if self.logger:
            metadata = metadata or {}
            metadata["platform"] = platform
            return self.logger.log_response(response, "social_post", metadata)
        else:
            print(f"日志记录已禁用，响应内容: {response[:50]}...")
            return ""
    
    def get_self_descriptions_history(self) -> list:
        """
        获取自述历史记录
        
        Returns:
            list: 自述历史记录列表
        """
        if self.logger:
            return self.logger.get_responses_by_type("self_description")
        else:
            return []
    
    def get_social_posts_history(self) -> list:
        """
        获取社交媒体发言历史记录
        
        Returns:
            list: 社交媒体发言历史记录列表
        """
        if self.logger:
            return self.logger.get_responses_by_type("social_post")
        else:
            return []
    
    def get_all_responses_history(self) -> list:
        """
        获取所有响应历史记录
        
        Returns:
            list: 所有响应历史记录列表
        """
        if self.logger:
            return self.logger.get_all_responses()
        else:
            return []
    
    def export_data(self, file_path: Optional[str] = None) -> str:
        """
        导出患者所有数据
        
        Args:
            file_path: 导出文件路径，如果为None则自动生成
            
        Returns:
            str: 导出文件路径
        """
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"logs/{self.patient_id}/export_{timestamp}.json"
        
        export_data = {
            "patient_profile": self.get_detailed_info(),
            "self_descriptions": self.get_self_descriptions_history(),
            "social_posts": self.get_social_posts_history(),
            "export_time": datetime.now().isoformat()
        }
        
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def get_fixed_test_prompt(self) -> str:
        """
        获取固定的测试提示词，确保稳定性测试的一致性
        
        Returns:
            str: 完整的测试提示词（缓存版本，每次调用返回相同内容）
        """
        # 如果已经缓存，直接返回
        if self._cached_test_prompt is not None:
            return self._cached_test_prompt
        
        # 生成固定的测试提示词并缓存
        self._cached_test_prompt = self.prompt_generator.generate_self_description_prompt_with_item_scores_for_phq9_test(
            scenario=self.fixed_scenario,
            style=self.fixed_style,
            time_perspective=self.fixed_time_perspective
        )
        
        return self._cached_test_prompt

    def __str__(self) -> str:
        """字符串表示"""
        return (f"PatientAgent(id={self.patient_id}, age={self.age}, "
                f"gender={self.gender}, depression_level={self.depression_level}, "
                f"score={self.score})")
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()


# 向后兼容的导出
__all__ = ['PatientAgent']
