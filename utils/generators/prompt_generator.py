# -*- coding: utf-8 -*-
"""
模板生成器
用于生成病人自述、社交媒体发言的prompt模板
"""

import random
from config import *

class PromptGenerator:
    def __init__(self, patient_agent):
        """
        初始化模板生成器
        
        Args:
            patient_agent: 病人代理对象
        """
        self.patient = patient_agent
    
    def generate_self_description_prompt(self, scenario=None, style=None, time_perspective=None):
        """
        生成多样化的自我状态阐述prompt
        
        Args:
            scenario: 指定场景类型，如为None则随机选择
            style: 指定表达风格，如为None则随机选择  
            time_perspective: 指定时间维度，如为None则随机选择
            
        Returns:
            str: 完整的prompt模板
        """
        # 动态选择场景、风格和时间维度
        selected_scenario = scenario or random.choice(list(PROMPT_SCENARIOS.keys()))
        selected_style = style or random.choice(list(EXPRESSION_STYLES.keys()))
        selected_time = time_perspective or random.choice(list(TIME_PERSPECTIVES.keys()))
        
        # 获取具体的场景描述
        scenario_prompt = random.choice(PROMPT_SCENARIOS[selected_scenario])
        style_prompt = EXPRESSION_STYLES[selected_style]
        time_prompt = TIME_PERSPECTIVES[selected_time]
        
        # 根据抑郁标签和等级选择合适的历史模板和内容
        if self.patient.depression_tag == "非抑郁":
            history_templates = HEALTHY_HISTORY_TEMPLATES
            person_description = "一个心理健康状态良好的个体"
            writing_guidance_specific = "体现出积极健康的心理状态，但也要保持真实自然，可以有正常的生活压力和小烦恼"
            final_instruction = f"{style_prompt}，结合{selected_scenario}场景，从{selected_time}的角度，写一段真实可信、自然的健康个体内心独白。"
            phq9_section = ""  # 健康人群不需要量表内容
            situational_trigger = ""
        else:
            # 根据抑郁等级选择更有针对性的历史模板
            if self.patient.depression_level in DEPRESSION_LEVEL_HISTORIES:
                # 70%概率使用分层模板，30%概率使用全部模板（保持多样性）
                if random.random() < 0.7:
                    history_templates = DEPRESSION_LEVEL_HISTORIES[self.patient.depression_level]
                else:
                    history_templates = PATIENT_HISTORY_TEMPLATES
            else:
                history_templates = PATIENT_HISTORY_TEMPLATES
            
            person_description = "一名正在经历心理健康问题（如抑郁症）的个体"
            writing_guidance_specific = "允许内容中有犹豫、反复、情感波动，尽量接近真实抑郁患者的内心世界"
            final_instruction = f"{style_prompt}，结合{selected_scenario}场景，从{selected_time}的角度，写一段真实可信、细腻自然的抑郁患者内心独白。"
            
            # 添加情境触发器
            if self.patient.depression_level in SITUATIONAL_TRIGGERS:
                trigger_options = SITUATIONAL_TRIGGERS[self.patient.depression_level]
                if random.random() < 0.6:  # 60%概率添加特定触发器
                    trigger_key = random.choice(list(trigger_options.keys()))
                    situational_trigger = f"\n【特定关注点】\n{trigger_options[trigger_key]}\n"
                else:
                    situational_trigger = ""
            else:
                situational_trigger = ""
            
            # 根据量表类型选择不同的内容
            if self.patient.questionnaire_type == "PHQ-9":
                phq9_section = self._generate_phq9_section()
            elif self.patient.questionnaire_type == "SDS":
                phq9_section = self._generate_sds_section()
            else:
                phq9_section = self._generate_phq9_section()  # 默认使用PHQ-9
        
        # 随机选择对应的历史模板
        personal_history = random.choice(history_templates)
        
        # 根据抑郁标签动态生成心理状态描述
        if self.patient.depression_tag == "非抑郁":
            mental_state_description = f"- 当前心理状态等级：{self.patient.depression_level}"
        else:
            mental_state_description = f"- 当前心理状态等级：{self.patient.depression_level}抑郁"
        
        # 根据抑郁标签动态生成认知特征描述
        if self.patient.depression_tag == "非抑郁":
            cognitive_features = f"""【认知特征】
- 核心信念：{self.patient.core_belief}
- 中间信念：{self.patient.intermediate_belief}
- 应对策略：{self.patient.coping_strategy}"""
        else:
            cognitive_features = f"""【认知特征】
- 核心信念：{self.patient.core_belief}
- 中间信念：{self.patient.intermediate_belief}
- 抑郁时的中间信念：{self.patient.depressed_belief}
- 应对策略：{self.patient.coping_strategy}"""
        
        prompt = f"""请你以第一人称，真实细腻地描写自己当前的心理状态和日常体验。你是{person_description}。请充分参考下方的"个人档案""个人经历"和"认知特征"内容，让自述充满生活细节和内心独白。

⸻

【场景焦点】{selected_scenario} | 【表达方式】{selected_style} | 【时间视角】{selected_time}

【核心任务】
{scenario_prompt}
{time_prompt}

{situational_trigger}

【个人档案】
- 年龄：{self.patient.age}岁
- 性别：{self.patient.gender}
- 教育背景：{self.patient.education}
- 职业/身份：{self.patient.occupation}
- 婚姻状况：{self.patient.marital_status}
- 人格特质（五项，满分5分）：外向性({self.patient.personality_profile.personality.get('外向性', 'N/A')})、宜人性({self.patient.personality_profile.personality.get('宜人性', 'N/A')})、责任心({self.patient.personality_profile.personality.get('责任心', 'N/A')})、神经质({self.patient.personality_profile.personality.get('神经质', 'N/A')})、开放性({self.patient.personality_profile.personality.get('开放性', 'N/A')})
- 语言风格偏好：{self.patient.language_style}
{mental_state_description}
- PHQ-9分数：{self.patient.score}

【个人经历】
{personal_history}

{cognitive_features}

【情绪与体验】
- 主要情绪：{self.patient.main_emotion}
- 典型想法：{self.patient.automatic_thought}
- 近期典型行为：{self.patient.typical_behavior}
{phq9_section}

⸻

【写作指导】
1. 以第一人称进行自我叙述，内容应真实、自然、具备情感色彩和细节。
2. 不要直接提及"认知特征"或列表内容，但要让你的表达和想法体现出这些信念与应对方式的影响。
3. 重点围绕【场景焦点】和【核心任务】展开，但可以自然地涉及其他生活方面。
4. 结合当前情绪和典型想法，展现你与外界和自我的关系。
5. {writing_guidance_specific}
6. 字数建议 200～400 字，根据选择的表达方式灵活调整长度。

⸻

{final_instruction}"""

        return prompt
    
    def generate_social_post_prompt(self, platform="微博", context=None, post_type=None):
        """
        生成多样化的社交媒体发言prompt
        
        Args:
            platform: 社交媒体平台
            context: 发言的上下文背景
            post_type: 指定发言类型，如为None则随机选择
            
        Returns:
            str: 完整的prompt模板
        """
        # 动态选择发言类型
        if post_type is None and platform in SOCIAL_MEDIA_CONTEXTS:
            platform_contexts = SOCIAL_MEDIA_CONTEXTS[platform]
            selected_post_type = random.choice(list(platform_contexts.keys()))
            post_guidance = platform_contexts[selected_post_type]
        elif post_type and platform in SOCIAL_MEDIA_CONTEXTS and post_type in SOCIAL_MEDIA_CONTEXTS[platform]:
            selected_post_type = post_type
            post_guidance = SOCIAL_MEDIA_CONTEXTS[platform][post_type]
        else:
            selected_post_type = "日常分享"
            post_guidance = "分享你的日常感受和想法"
        
        context_text = context if context else post_guidance
        
        # 根据抑郁等级添加不同的表达倾向
        if self.patient.depression_tag == "非抑郁":
            tone_guidance = "可以表达正面情绪，但也要保持真实，可以有正常的小烦恼和压力"
            length_suggestion = "内容长度适中，语言自然轻松"
        else:
            if self.patient.depression_level == "轻度":
                tone_guidance = "可能会透露一些焦虑、疲惫或不确定的情绪，但不会过于消极"
                length_suggestion = "内容可能比较简短，有时会有一些犹豫的表达"
            elif self.patient.depression_level == "中度":
                tone_guidance = "可能会表达孤独、失落、无助等较强的负面情绪"
                length_suggestion = "内容可能情绪化一些，有时会比较沉重"
            else:  # 重度
                tone_guidance = "可能会表达深度的绝望、无意义感，或者异常简短的表达"
                length_suggestion = "内容可能非常简短或异常沉重，表达方式可能比较极端"
        
        prompt = f"""请你作为一个在{platform}上发言的用户，基于以下个人信息和心理状态，生成1-3条符合你当前状态的社交媒体发言。

【发言场景】{selected_post_type} | 【平台特色】{platform}

【个人信息】
- 年龄：{self.patient.age}岁
- 性别：{self.patient.gender}
- 教育背景：{self.patient.education}
- 职业：{self.patient.occupation}
- 婚姻状况：{self.patient.marital_status}

【心理状态】
- 抑郁等级：{self.patient.depression_level}
- 主要情绪：{self.patient.main_emotion}
- 语言风格：{self.patient.language_style}
- 隐藏倾向：{self.patient.hiding_tendency}

【认知特征】
- 核心信念：{self.patient.core_belief}
- 典型自动想法：{self.patient.automatic_thought}
- 近期行为表现：{self.patient.typical_behavior}

【发言背景】
{context_text}

【要求】
1. 发言要符合{platform}平台的特点和字数限制
2. {tone_guidance}
3. 根据隐藏倾向决定是直接表达还是含蓄暗示
4. 语言风格要与个人特征匹配
5. {length_suggestion}
6. 可以包含日常生活片段、感受、想法、或对生活的感悟
7. 避免过于直白地描述心理状态，要自然流露
8. 每条发言应该有不同的角度或内容重点

请生成1-3条发言内容："""

        return prompt
    
    def generate_self_description_prompt_with_item_scores(self, scenario=None, style=None, time_perspective=None):
        """
        生成包含具体分项分数的自我状态阐述prompt
        
        Args:
            scenario: 指定场景类型，如为None则随机选择
            style: 指定表达风格，如为None则随机选择  
            time_perspective: 指定时间维度，如为None则随机选择
            
        Returns:
            str: 完整的prompt模板（包含详细分项分数）
        """
        # 动态选择场景、风格和时间维度
        selected_scenario = scenario or random.choice(list(PROMPT_SCENARIOS.keys()))
        selected_style = style or random.choice(list(EXPRESSION_STYLES.keys()))
        selected_time = time_perspective or random.choice(list(TIME_PERSPECTIVES.keys()))
        
        # 获取具体的场景描述
        scenario_prompt = random.choice(PROMPT_SCENARIOS[selected_scenario])
        style_prompt = EXPRESSION_STYLES[selected_style]
        time_prompt = TIME_PERSPECTIVES[selected_time]
        
        # 根据抑郁标签和等级选择合适的历史模板和内容
        if self.patient.depression_tag == "非抑郁":
            history_templates = HEALTHY_HISTORY_TEMPLATES
            person_description = "一个心理健康状态良好的个体"
            writing_guidance_specific = "体现出积极健康的心理状态，但也要保持真实自然，可以有正常的生活压力和小烦恼"
            final_instruction = f"{style_prompt}，结合{selected_scenario}场景，从{selected_time}的角度，写一段真实可信、自然的健康个体内心独白。"
            phq9_section = ""  # 健康人群不需要量表内容
            situational_trigger = ""
        else:
            # 根据抑郁等级选择更有针对性的历史模板
            if self.patient.depression_level in DEPRESSION_LEVEL_HISTORIES:
                # 70%概率使用分层模板，30%概率使用全部模板（保持多样性）
                if random.random() < 0.7:
                    history_templates = DEPRESSION_LEVEL_HISTORIES[self.patient.depression_level]
                else:
                    history_templates = PATIENT_HISTORY_TEMPLATES
            else:
                history_templates = PATIENT_HISTORY_TEMPLATES
            
            person_description = "一名正在经历心理健康问题（如抑郁症）的个体"
            writing_guidance_specific = "允许内容中有犹豫、反复、情感波动，尽量接近真实抑郁患者的内心世界"
            final_instruction = f"{style_prompt}，结合{selected_scenario}场景，从{selected_time}的角度，写一段真实可信、细腻自然的抑郁患者内心独白。"
            
            # 添加情境触发器
            if self.patient.depression_level in SITUATIONAL_TRIGGERS:
                trigger_options = SITUATIONAL_TRIGGERS[self.patient.depression_level]
                if random.random() < 0.6:  # 60%概率添加特定触发器
                    trigger_key = random.choice(list(trigger_options.keys()))
                    situational_trigger = f"\n【特定关注点】\n{trigger_options[trigger_key]}\n"
                else:
                    situational_trigger = ""
            else:
                situational_trigger = ""
            
            # 根据量表类型选择不同的内容
            if self.patient.questionnaire_type == "PHQ-9":
                phq9_section = self._generate_phq9_section_with_item_scores()
            elif self.patient.questionnaire_type == "SDS":
                phq9_section = self._generate_sds_section_with_item_scores()
            else:
                phq9_section = self._generate_phq9_section_with_item_scores()  # 默认使用PHQ-9
        
        # 随机选择对应的历史模板
        personal_history = random.choice(history_templates)
        
        # 根据抑郁标签动态生成心理状态描述
        if self.patient.depression_tag == "非抑郁":
            mental_state_description = f"- 当前心理状态等级：{self.patient.depression_level}"
        else:
            mental_state_description = f"- 当前心理状态等级：{self.patient.depression_level}抑郁"
        
        # 根据抑郁标签动态生成认知特征描述
        if self.patient.depression_tag == "非抑郁":
            cognitive_features = f"""【认知特征】
- 核心信念：{self.patient.core_belief}
- 中间信念：{self.patient.intermediate_belief}
- 应对策略：{self.patient.coping_strategy}"""
        else:
            cognitive_features = f"""【认知特征】
- 核心信念：{self.patient.core_belief}
- 中间信念：{self.patient.intermediate_belief}
- 抑郁时的中间信念：{self.patient.depressed_belief}
- 应对策略：{self.patient.coping_strategy}"""
        
        prompt = f"""请你以第一人称，真实细腻地描写自己当前的心理状态和日常体验。你是{person_description}。请充分参考下方的"个人档案""个人经历"和"认知特征"内容，让自述充满生活细节和内心独白。

⸻

【场景焦点】{selected_scenario} | 【表达方式】{selected_style} | 【时间视角】{selected_time}

【核心任务】
{scenario_prompt}
{time_prompt}

{situational_trigger}

【个人档案】
- 年龄：{self.patient.age}岁
- 性别：{self.patient.gender}
- 教育背景：{self.patient.education}
- 职业/身份：{self.patient.occupation}
- 婚姻状况：{self.patient.marital_status}
- 人格特质（五项，满分5分）：外向性({self.patient.personality_profile.personality.get('外向性', 'N/A')})、宜人性({self.patient.personality_profile.personality.get('宜人性', 'N/A')})、责任心({self.patient.personality_profile.personality.get('责任心', 'N/A')})、神经质({self.patient.personality_profile.personality.get('神经质', 'N/A')})、开放性({self.patient.personality_profile.personality.get('开放性', 'N/A')})
- 语言风格偏好：{self.patient.language_style}
{mental_state_description}
- {self.patient.questionnaire_type}总分：{self.patient.score}

【个人经历】
{personal_history}

{cognitive_features}

【情绪与体验】
- 主要情绪：{self.patient.main_emotion}
- 典型想法：{self.patient.automatic_thought}
- 近期典型行为：{self.patient.typical_behavior}
{phq9_section}

⸻

【写作指导】
1. 以第一人称进行自我叙述，内容应真实、自然、具备情感色彩和细节。
2. 不要直接提及"认知特征"或列表内容，但要让你的表达和想法体现出这些信念与应对方式的影响。
3. 重点围绕【场景焦点】和【核心任务】展开，但可以自然地涉及其他生活方面。
4. 结合当前情绪和典型想法，展现你与外界和自我的关系。
5. {writing_guidance_specific}
6. 字数建议 200～400 字，根据选择的表达方式灵活调整长度。

⸻

{final_instruction}"""

        return prompt

    def generate_self_description_prompt_with_item_scores_for_phq9_test(self, scenario=None, style=None, time_perspective=None):
        """
        生成包含具体分项分数的自我状态阐述prompt
        
        Args:
            scenario: 指定场景类型，如为None则使用Agent的固定场景
            style: 指定表达风格，如为None则使用Agent的固定风格  
            time_perspective: 指定时间维度，如为None则使用Agent的固定时间维度
            
        Returns:
            str: 完整的prompt模板（包含详细分项分数）
        """
        # 优先使用传入参数，如果为None则使用Agent的固定参数（确保稳定性）
        if hasattr(self.patient, 'fixed_scenario') and scenario is None:
            selected_scenario = self.patient.fixed_scenario
            scenario_prompt = self.patient.fixed_scenario_prompt
        else:
            selected_scenario = scenario or random.choice(list(PROMPT_SCENARIOS.keys()))
            scenario_prompt = random.choice(PROMPT_SCENARIOS[selected_scenario])
        
        if hasattr(self.patient, 'fixed_style') and style is None:
            selected_style = self.patient.fixed_style
        else:
            selected_style = style or random.choice(list(EXPRESSION_STYLES.keys()))
        
        if hasattr(self.patient, 'fixed_time_perspective') and time_perspective is None:
            selected_time = self.patient.fixed_time_perspective
        else:
            selected_time = time_perspective or random.choice(list(TIME_PERSPECTIVES.keys()))
        
        # 获取对应的提示词
        style_prompt = EXPRESSION_STYLES[selected_style]
        time_prompt = TIME_PERSPECTIVES[selected_time]
        
        # 根据抑郁标签和等级选择合适的历史模板和内容
        if self.patient.depression_tag == "非抑郁":
            person_description = "一个心理健康状态良好的个体"
            writing_guidance_specific = "体现出积极健康的心理状态，但也要保持真实自然，可以有正常的生活压力和小烦恼"
            final_instruction = f"{style_prompt}，结合{selected_scenario}场景，从{selected_time}的角度，写一段真实可信、自然的健康个体内心独白。"
            phq9_section = ""  # 健康人群不需要量表内容
            situational_trigger = ""
        else:
            person_description = "一名正在经历心理健康问题（如抑郁症）的个体"
            writing_guidance_specific = "允许内容中有犹豫、反复、情感波动，尽量接近真实抑郁患者的内心世界"
            final_instruction = f"{style_prompt}，结合{selected_scenario}场景，从{selected_time}的角度，写一段真实可信、细腻自然的抑郁患者内心独白。"


            
            # 根据量表类型选择不同的内容
            if self.patient.questionnaire_type == "PHQ-9":
                phq9_section = self._generate_phq9_section_with_item_scores_for_phq9_test()
            elif self.patient.questionnaire_type == "SDS":
                phq9_section = self._generate_sds_section_with_item_scores_for_phq9_test()
            else:
                phq9_section = self._generate_phq9_section_with_item_scores_for_phq9_test()  # 默认使用PHQ-9
        
        # 使用固定的历史模板（如果有）
        if hasattr(self.patient, 'fixed_personal_history'):
            personal_history = self.patient.fixed_personal_history
        else:
            # 旧的随机逻辑，仅在没有固定参数时使用
            if self.patient.depression_level in DEPRESSION_LEVEL_HISTORIES:
                # 70%概率使用分层模板，30%概率使用全部模板（保持多样性）
                if random.random() < 0.7:
                    history_templates = DEPRESSION_LEVEL_HISTORIES[self.patient.depression_level]
                else:
                    history_templates = PATIENT_HISTORY_TEMPLATES
            else:
                history_templates = PATIENT_HISTORY_TEMPLATES
            personal_history = random.choice(history_templates)
        
        # 根据抑郁标签动态生成心理状态描述
        if self.patient.depression_tag == "非抑郁":
            mental_state_description = f"- 当前心理状态等级：{self.patient.depression_level}"
        else:
            mental_state_description = f"- 当前心理状态等级：{self.patient.depression_level}抑郁"
        
        
        prompt = f"""你是{person_description}，以下是你的个人档案，请你结合你的信息以及抑郁量表信息回答问题。
⸻

【个人档案】
- 年龄：{self.patient.age}岁
- 性别：{self.patient.gender}
- 教育背景：{self.patient.education}
- 职业/身份：{self.patient.occupation}
- 婚姻状况：{self.patient.marital_status}
- 人格特质（五项，满分5分）：外向性({self.patient.personality_profile.personality.get('外向性', 'N/A')})、宜人性({self.patient.personality_profile.personality.get('宜人性', 'N/A')})、责任心({self.patient.personality_profile.personality.get('责任心', 'N/A')})、神经质({self.patient.personality_profile.personality.get('神经质', 'N/A')})、开放性({self.patient.personality_profile.personality.get('开放性', 'N/A')})
- 语言风格偏好：{self.patient.language_style}
{mental_state_description}
- {self.patient.questionnaire_type}总分：{self.patient.score}

{phq9_section}

"""

        return prompt
    
    def _generate_phq9_section(self):
        """
        为抑郁患者生成PHQ-9量表相关内容
        
        Returns:
            str: PHQ-9量表的格式化内容
        """
        phq9_content = f"""
【PHQ-9抑郁症状自评量表参考】
以下是抑郁症的标准评估指标，您的自述应该自然地体现出与您当前抑郁程度相符的症状表现：

PHQ-9量表（过去2周内的症状频率）：

1. 做什么事都感到没有兴趣或乐趣
2. 感到心情低落、沮丧或绝望
3. 入睡困难、很难熟睡或睡太多
4. 感到疲劳或无精打采
5. 胃口不好或吃太多
6. 觉得自己很糟，或很失败，或让自己或家人很失望
7. 注意很难集中，例如阅读报纸或看电视
8. 动作或说话速度缓慢到别人可觉察的程度，或正好相反—烦躁或坐立不安，动来动去的情况比平常更严重
9. 有不如死掉或用某种方式伤害自己的念头

评分标准：
- 完全不会 = 0分
- 有过几天 = 1分  
- 一半以上的日子 = 2分
- 几乎每天 = 3分

您当前的抑郁等级为"{self.patient.depression_level}"，PHQ-9总分为{self.patient.score}分。
在自述中，请自然地体现出符合这个等级的症状严重程度和频率，但不要直接提及量表或评分。"""

        return phq9_content
    
    def _generate_sds_section(self):
        """
        为抑郁患者生成SDS量表相关内容
        
        Returns:
            str: SDS量表的格式化内容
        """
        sds_content = f"""
【SDS抑郁自评量表参考】
以下是抑郁症的标准评估指标，您的自述应该自然地体现出与您当前抑郁程度相符的症状表现：

SDS量表（过去一周内的症状频率）：

选择标准：1.没有或很少时间  2.小部分时间  3.相当多时间  4.绝大部分或全部时间

1. 我觉得闷闷不乐，情绪低沉
2. 我觉得一天之中早晨最好
3. 我一阵阵哭出来或觉得想哭
4. 我晚上睡眠不好
5. 我吃得跟平常一样多
6. 我与异性密切接触时和以往一样感到愉快
7. 我发觉我的体重下降
8. 我有便秘的苦恼
9. 我心跳比平时快
10. 我无缘无故地感到疲乏
11. 我的头脑跟平常一样清楚
12. 我觉得经常做的事情并没有困难
13. 我觉得不安而平静不下来
14. 我对将来抱有希望
15. 我比平常容易生气激动
16. 我觉得作出决定是容易的
17. 我觉得自己是个有用的人，有人需要我
18. 我的生活过得很有意思
19. 我认为如果我死了别人会生活得好些
20. 我平常感兴趣的事我仍然照样感兴趣

评分说明：
- 正向题：依次评为1、2、3、4分
- 反向题：依次评为4、3、2、1分
- 原始分乘以1.25后取整得到标准分

您当前的抑郁等级为"{self.patient.depression_level}"，SDS标准分为{self.patient.score}分。
在自述中，请自然地体现出符合这个等级的症状严重程度和频率，但不要直接提及量表或评分。"""

        return sds_content

    def _generate_phq9_section_with_item_scores(self):
        """
        为抑郁患者生成包含具体分项分数的PHQ-9量表内容
        
        Returns:
            str: PHQ-9量表的格式化内容（包含具体分项分数）
        """
        # 生成分项分数
        item_scores = self.patient.generate_item_scores()
        
        # PHQ-9分数对应的描述
        phq9_descriptions = {
            0: "完全不会",
            1: "有过几天", 
            2: "一半以上的日子",
            3: "几乎每天"
        }
        
        phq9_content = f"""
【PHQ-9抑郁症状自评量表参考】
以下是抑郁症的标准评估指标，您的自述应该自然地体现出与您当前抑郁程度相符的症状表现：

PHQ-9量表（过去2周内的症状频率）：

1. 做什么事都感到没有兴趣或乐趣 - {phq9_descriptions.get(item_scores.get(1, 0), "完全不会")}
2. 感到心情低落、沮丧或绝望 - {phq9_descriptions.get(item_scores.get(2, 0), "完全不会")}
3. 入睡困难、很难熟睡或睡太多 - {phq9_descriptions.get(item_scores.get(3, 0), "完全不会")}
4. 感到疲劳或无精打采 - {phq9_descriptions.get(item_scores.get(4, 0), "完全不会")}
5. 胃口不好或吃太多 - {phq9_descriptions.get(item_scores.get(5, 0), "完全不会")}
6. 觉得自己很糟，或很失败，或让自己或家人很失望 - {phq9_descriptions.get(item_scores.get(6, 0), "完全不会")}
7. 注意很难集中，例如阅读报纸或看电视 - {phq9_descriptions.get(item_scores.get(7, 0), "完全不会")}
8. 动作或说话速度缓慢到别人可觉察的程度，或正好相反—烦躁或坐立不安，动来动去的情况比平常更严重 - {phq9_descriptions.get(item_scores.get(8, 0), "完全不会")}
9. 有不如死掉或用某种方式伤害自己的念头 - {phq9_descriptions.get(item_scores.get(9, 0), "完全不会")}

评分标准：
- 完全不会 = 0分
- 有过几天 = 1分  
- 一半以上的日子 = 2分
- 几乎每天 = 3分

您当前的抑郁等级为"{self.patient.depression_level}"，PHQ-9总分为{self.patient.score}分。
【重要提示】：在自述中，请根据上述每个症状的具体分数，自然地体现出对应强度的症状表现。
- 0分的症状：完全不要在自述中体现
- 1分的症状：可以轻微提及或暗示
- 2分的症状：应该明显体现在自述中
- 3分的症状：应该强烈体现，成为自述的重点内容

但不要直接提及量表、评分或分项分数。"""

        return phq9_content

    def _generate_phq9_section_with_item_scores_for_phq9_test(self):
        """
        为抑郁患者生成包含具体分项分数的PHQ-9量表内容
        
        Returns:
            str: PHQ-9量表的格式化内容（包含具体分项分数）
        """
        # 生成分项分数
        item_scores = self.patient.generate_item_scores()
        
        # PHQ-9分数对应的描述
        phq9_descriptions = {
            0: "完全不会",
            1: "有过几天", 
            2: "一半以上的日子",
            3: "几乎每天"
        }
        
        phq9_content = f"""
【PHQ-9抑郁症状自评量表参考】
以下是抑郁症的标准评估指标，

PHQ-9量表（过去2周内的症状频率）：

1. 做什么事都感到没有兴趣或乐趣 - {phq9_descriptions.get(item_scores.get(1, 0), "完全不会")}
2. 感到心情低落、沮丧或绝望 - {phq9_descriptions.get(item_scores.get(2, 0), "完全不会")}
3. 入睡困难、很难熟睡或睡太多 - {phq9_descriptions.get(item_scores.get(3, 0), "完全不会")}
4. 感到疲劳或无精打采 - {phq9_descriptions.get(item_scores.get(4, 0), "完全不会")}
5. 胃口不好或吃太多 - {phq9_descriptions.get(item_scores.get(5, 0), "完全不会")}
6. 觉得自己很糟，或很失败，或让自己或家人很失望 - {phq9_descriptions.get(item_scores.get(6, 0), "完全不会")}
7. 注意很难集中，例如阅读报纸或看电视 - {phq9_descriptions.get(item_scores.get(7, 0), "完全不会")}
8. 动作或说话速度缓慢到别人可觉察的程度，或正好相反—烦躁或坐立不安，动来动去的情况比平常更严重 - {phq9_descriptions.get(item_scores.get(8, 0), "完全不会")}
9. 有不如死掉或用某种方式伤害自己的念头 - {phq9_descriptions.get(item_scores.get(9, 0), "完全不会")}

评分标准：
- 完全不会 = 0分
- 有过几天 = 1分  
- 一半以上的日子 = 2分
- 几乎每天 = 3分

您当前的抑郁等级为"{self.patient.depression_level}"，PHQ-9总分为{self.patient.score}分。

"""

        return phq9_content
    
    def _generate_sds_section_with_item_scores(self):
        """
        为抑郁患者生成包含具体分项分数的SDS量表内容
        
        Returns:
            str: SDS量表的格式化内容（包含具体分项分数）
        """
        from config import SDS_QUESTIONNAIRE
        
        # 生成分项分数
        item_scores = self.patient.generate_item_scores()
        
        # SDS分数对应的描述
        sds_descriptions = {
            1: "没有或很少时间",
            2: "小部分时间",
            3: "相当多时间", 
            4: "绝大部分或全部时间"
        }
        
        # 获取每个题目的显示描述，考虑反向题
        def get_item_description(question_id, raw_score):
            question_data = SDS_QUESTIONNAIRE["questions"][question_id - 1]
            if question_data["type"] == "negative":
                # 反向题：原始分数越低，实际抑郁程度越高
                # 1分->4分效果，2分->3分效果，3分->2分效果，4分->1分效果
                display_score = 5 - raw_score
            else:
                # 正向题：原始分数直接对应
                display_score = raw_score
            return sds_descriptions.get(display_score, "没有或很少时间")
        
        sds_content = f"""
【SDS抑郁自评量表参考】
以下是抑郁症的标准评估指标，您的自述应该自然地体现出与您当前抑郁程度相符的症状表现：

SDS量表（过去一周内的症状频率）：

选择标准：1.没有或很少时间  2.小部分时间  3.相当多时间  4.绝大部分或全部时间

1. 我觉得闷闷不乐，情绪低沉 - {get_item_description(1, item_scores.get(1, 1))}
2. 我觉得一天之中早晨最好 - {get_item_description(2, item_scores.get(2, 1))}
3. 我一阵阵哭出来或觉得想哭 - {get_item_description(3, item_scores.get(3, 1))}
4. 我晚上睡眠不好 - {get_item_description(4, item_scores.get(4, 1))}
5. 我吃得跟平常一样多 - {get_item_description(5, item_scores.get(5, 1))}
6. 我与异性密切接触时和以往一样感到愉快 - {get_item_description(6, item_scores.get(6, 1))}
7. 我发觉我的体重下降 - {get_item_description(7, item_scores.get(7, 1))}
8. 我有便秘的苦恼 - {get_item_description(8, item_scores.get(8, 1))}
9. 我心跳比平时快 - {get_item_description(9, item_scores.get(9, 1))}
10. 我无缘无故地感到疲乏 - {get_item_description(10, item_scores.get(10, 1))}
11. 我的头脑跟平常一样清楚 - {get_item_description(11, item_scores.get(11, 1))}
12. 我觉得经常做的事情并没有困难 - {get_item_description(12, item_scores.get(12, 1))}
13. 我觉得不安而平静不下来 - {get_item_description(13, item_scores.get(13, 1))}
14. 我对将来抱有希望 - {get_item_description(14, item_scores.get(14, 1))}
15. 我比平常容易生气激动 - {get_item_description(15, item_scores.get(15, 1))}
16. 我觉得作出决定是容易的 - {get_item_description(16, item_scores.get(16, 1))}
17. 我觉得自己是个有用的人，有人需要我 - {get_item_description(17, item_scores.get(17, 1))}
18. 我的生活过得很有意思 - {get_item_description(18, item_scores.get(18, 1))}
19. 我认为如果我死了别人会生活得好些 - {get_item_description(19, item_scores.get(19, 1))}
20. 我平常感兴趣的事我仍然照样感兴趣 - {get_item_description(20, item_scores.get(20, 1))}

评分说明：
- 正向题：依次评为1、2、3、4分
- 反向题：依次评为4、3、2、1分
- 原始分乘以1.25后取整得到标准分

您当前的抑郁等级为"{self.patient.depression_level}"，SDS标准分为{self.patient.score}分。
【重要提示】：在自述中，请根据上述每个症状的具体分数强度，自然地体现出对应程度的症状表现。
- 对于正向题：分数越高，症状越明显
- 对于反向题：分数越低，抑郁症状越明显（因为是反向题）
- 请自然地体现出符合上述频率描述的症状表现

但不要直接提及量表、评分或分项分数。"""

        return sds_content

    def _generate_sds_section_with_item_scores_for_phq9_test(self):
        """
        为抑郁患者生成包含具体分项分数的SDS量表内容
        
        Returns:
            str: SDS量表的格式化内容（包含具体分项分数）
        """
        from config import SDS_QUESTIONNAIRE
        
        # 生成分项分数
        item_scores = self.patient.generate_item_scores()
        
        # SDS分数对应的描述
        sds_descriptions = {
            1: "没有或很少时间",
            2: "小部分时间",
            3: "相当多时间", 
            4: "绝大部分或全部时间"
        }
        
        # 获取每个题目的显示描述，考虑反向题
        def get_item_description(question_id, raw_score):
            question_data = SDS_QUESTIONNAIRE["questions"][question_id - 1]
            if question_data["type"] == "negative":
                # 反向题：原始分数越低，实际抑郁程度越高
                # 1分->4分效果，2分->3分效果，3分->2分效果，4分->1分效果
                display_score = 5 - raw_score
            else:
                # 正向题：原始分数直接对应
                display_score = raw_score
            return sds_descriptions.get(display_score, "没有或很少时间")
        
        sds_content = f"""
【SDS抑郁自评量表参考】
以下是抑郁症的标准评估指标，

SDS量表（过去一周内的症状频率）：

选择标准：1.没有或很少时间  2.小部分时间  3.相当多时间  4.绝大部分或全部时间

1. 我觉得闷闷不乐，情绪低沉 - {get_item_description(1, item_scores.get(1, 1))}
2. 我觉得一天之中早晨最好 - {get_item_description(2, item_scores.get(2, 1))}
3. 我一阵阵哭出来或觉得想哭 - {get_item_description(3, item_scores.get(3, 1))}
4. 我晚上睡眠不好 - {get_item_description(4, item_scores.get(4, 1))}
5. 我吃得跟平常一样多 - {get_item_description(5, item_scores.get(5, 1))}
6. 我与异性密切接触时和以往一样感到愉快 - {get_item_description(6, item_scores.get(6, 1))}
7. 我发觉我的体重下降 - {get_item_description(7, item_scores.get(7, 1))}
8. 我有便秘的苦恼 - {get_item_description(8, item_scores.get(8, 1))}
9. 我心跳比平时快 - {get_item_description(9, item_scores.get(9, 1))}
10. 我无缘无故地感到疲乏 - {get_item_description(10, item_scores.get(10, 1))}
11. 我的头脑跟平常一样清楚 - {get_item_description(11, item_scores.get(11, 1))}
12. 我觉得经常做的事情并没有困难 - {get_item_description(12, item_scores.get(12, 1))}
13. 我觉得不安而平静不下来 - {get_item_description(13, item_scores.get(13, 1))}
14. 我对将来抱有希望 - {get_item_description(14, item_scores.get(14, 1))}
15. 我比平常容易生气激动 - {get_item_description(15, item_scores.get(15, 1))}
16. 我觉得作出决定是容易的 - {get_item_description(16, item_scores.get(16, 1))}
17. 我觉得自己是个有用的人，有人需要我 - {get_item_description(17, item_scores.get(17, 1))}
18. 我的生活过得很有意思 - {get_item_description(18, item_scores.get(18, 1))}
19. 我认为如果我死了别人会生活得好些 - {get_item_description(19, item_scores.get(19, 1))}
20. 我平常感兴趣的事我仍然照样感兴趣 - {get_item_description(20, item_scores.get(20, 1))}


您当前的抑郁等级为"{self.patient.depression_level}"，SDS标准分为{self.patient.score}分。

"""

        return sds_content



if __name__ == "__main__":
    # 示例用法
    from core.agent_base import PatientAgent
    
    # 创建一个测试病人代理
    patient = PatientAgent()
    print(patient.generate_self_description_prompt())