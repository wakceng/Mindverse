# -*- coding: utf-8 -*-
"""
心理量表稳定性测试模块
用于验证Agent在多次测试中的心理状态稳定性
支持PHQ-9和SDS量表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PHQ9_QUESTIONNAIRE, PHQ9_SCORE_RANGES, SDS_QUESTIONNAIRE, SDS_SCORE_RANGES
from core.agent_base import PatientAgent
from utils.clients import TextGenerator
import json
import time
from typing import Dict, List, Any, Tuple
from datetime import datetime
import random
import statistics


        
class QuestionnaireStabilityTester:
    """心理量表稳定性测试器，支持PHQ-9和SDS量表"""
    
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: str = None, base_url: str = None, save_base_dir: str = "stability_results"):
        """
        初始化测试器
        
        Args:
            model: 要使用的LLM模型名称，如 "gpt-3.5-turbo", "deepseek-chat", "gemini-pro" 等
            api_key: API密钥，如果为None则从环境变量获取
            base_url: API基础URL，如果为None则从环境变量获取
            save_base_dir: 数据保存基础目录
        """
        self.model = model
        self.text_generator = TextGenerator(model=model, api_key=api_key, base_url=base_url)
        self.save_base_dir = save_base_dir
        
        # 确保保存目录存在
        os.makedirs(self.save_base_dir, exist_ok=True)
        
    def create_questionnaire_prompt(self, agent: PatientAgent, question_id: int) -> str:
        """
        为特定量表问题创建提示词
        使用agent的固定测试提示词，确保稳定性测试的一致性
        
        Args:
            agent: 患者代理
            question_id: 问题ID
            
        Returns:
            str: 完整的提示词
        """
        # 使用agent的固定测试提示词，确保每次调用都返回相同的基础描述
        original_prompt = agent.get_fixed_test_prompt()
        
        
        # 根据量表类型获取问题信息
        if agent.questionnaire_type == "PHQ-9":
            questionnaire = PHQ9_QUESTIONNAIRE
            question_data = questionnaire["questions"][question_id - 1]
            question_text = question_data["question"]
            options = question_data["options"]
            
            questionnaire_prompt = f"""现在请你作为上述描述的这个人，回答以下PHQ-9量表问题：

问题：在过去的2个星期里，您有多少时候受到"{question_text}"的困扰？

选项：
0. {options[0]}
1. {options[1]}
2. {options[2]}
3. {options[3]}

请根据你的实际心理状态诚实回答，请只回答选项的完整描述（如"{options[0]}"），不要数字和解释。

你的答案是："""
            
        elif agent.questionnaire_type == "SDS":
            questionnaire = SDS_QUESTIONNAIRE
            question_data = questionnaire["questions"][question_id - 1]
            question_text = question_data["question"]
            options = questionnaire["options"]  # SDS的选项在根级别
            
            questionnaire_prompt = f"""现在请你作为上述描述的这个人，回答以下SDS量表问题：

问题：在过去的一个星期里，关于"{question_text}"这个描述，您的情况是：

选项：
1. {options[0]}
2. {options[1]}
3. {options[2]}
4. {options[3]}

请根据你的实际心理状态诚实回答，请只回答选项的完整描述（如"{options[0]}"），不要数字和解释。

你的答案是："""
        else:
            raise ValueError(f"不支持的量表类型: {agent.questionnaire_type}")
        
        # 组合完整的提示词
        full_prompt = f"""{original_prompt}
{questionnaire_prompt}
        """

        return full_prompt
    
    def test_connection(self) -> bool:
        """
        测试LLM连接是否正常
        
        Returns:
            bool: 连接是否正常
        """
        try:
            print(f"正在测试模型: {self.model}")
            test_prompt = "请回答数字：1+1等于几？只需要回答数字。"
            response = self.text_generator.generate(prompt=test_prompt)
            print(f"原始响应: '{response}'")
            print(f"响应类型: {type(response)}")
            print(f"响应长度: {len(response) if response else 0}")
            
            if response and response.strip():
                print(f"✅ LLM连接正常，测试响应: '{response.strip()}'")
                return True
            else:
                print("❌ LLM返回空响应")
                return False
        except Exception as e:
            print(f"❌ LLM连接失败: {e}")
            print(f"错误类型: {type(e).__name__}")
            return False
    
    def _create_simplified_prompt(self, agent: PatientAgent, question_id: int) -> str:
        """
        创建简化的量表问题提示词，用于处理原始提示词过长的情况
        
        Args:
            agent: 患者代理
            question_id: 问题ID
            
        Returns:
            str: 简化的提示词
        """
        # 根据量表类型获取问题信息
        if agent.questionnaire_type == "PHQ-9":
            questionnaire = PHQ9_QUESTIONNAIRE
            question_data = questionnaire["questions"][question_id - 1]
            question_text = question_data["question"]
            options = question_data["options"]
            
            # 简化的角色描述
            role_description = f"你是{agent.age}岁{agent.gender}性，{agent.depression_level}抑郁状态。"
            
            simplified_prompt = f"""{role_description}

问题：过去2周，"{question_text}"困扰你的频率？
0.{options[0]} 1.{options[1]} 2.{options[2]} 3.{options[3]}
请只回答选项的完整描述（如'完全不会'），不要数字和解释："""
            
        elif agent.questionnaire_type == "SDS":
            questionnaire = SDS_QUESTIONNAIRE
            question_data = questionnaire["questions"][question_id - 1]
            question_text = question_data["question"]
            options = questionnaire["options"]  # SDS的选项在根级别
            
            # 简化的角色描述
            role_description = f"你是{agent.age}岁{agent.gender}性，{agent.depression_level}抑郁状态。"
            
            simplified_prompt = f"""{role_description}

问题：过去1周，"{question_text}"的情况？
1.{options[0]} 2.{options[1]} 3.{options[2]} 4.{options[3]}
请只回答选项的完整描述（如'完全不会'），不要数字和解释："""
        else:
            raise ValueError(f"不支持的量表类型: {agent.questionnaire_type}")
        
        return simplified_prompt

    def ask_questionnaire_question(self, agent: PatientAgent, question_id: int, 
                                 test_round: int = 1, attempt: int = 1) -> Tuple[int, str, str, str]:
        """
        向Agent询问单个量表问题
        
        Args:
            agent: 患者代理
            question_id: 问题ID
            test_round: 测试轮次
            attempt: 尝试次数（用于重试机制）
            
        Returns:
            Tuple[int, str, str, str]: (答案分数, Agent的完整回答, 问题文本, 完整提示词)
        """
        prompt = self.create_questionnaire_prompt(agent, question_id)
        
        # 根据量表类型获取问题信息
        if agent.questionnaire_type == "PHQ-9":
            questionnaire = PHQ9_QUESTIONNAIRE
            question_text = questionnaire["questions"][question_id - 1]["question"]
            valid_scores = [0, 1, 2, 3]
            score_ranges = PHQ9_SCORE_RANGES
        elif agent.questionnaire_type == "SDS":
            questionnaire = SDS_QUESTIONNAIRE
            question_data = questionnaire["questions"][question_id - 1]
            question_text = question_data["question"]
            valid_scores = [1, 2, 3, 4]
            score_ranges = SDS_SCORE_RANGES
        else:
            raise ValueError(f"不支持的量表类型: {agent.questionnaire_type}")
        
        try:
            # TextGenerator.generate() 直接返回文本内容
            response = self.text_generator.generate(prompt=prompt)
            answer_text = response.strip() if response else ""
            
            # 如果返回空响应，记录详细信息
            if not answer_text:
                print(f"问题{question_id}收到空响应，提示词长度: {len(prompt)} 字符")
                if len(prompt) > 2000:
                    print("提示词可能过长，尝试使用简化版本...")
                    simplified_prompt = self._create_simplified_prompt(agent, question_id)
                    response = self.text_generator.generate(prompt=simplified_prompt)
                    answer_text = response.strip() if response else ""
                    prompt = simplified_prompt  # 更新提示词为简化版本
            
            # 尝试从回答中提取数字
            score = None
            for char in answer_text:
                if char.isdigit() and int(char) in valid_scores:
                    score = int(char)
                    break
            
            # 如果没有找到有效数字，尝试解析文本
            if score is None:
                score = self._parse_text_answer(answer_text, agent.questionnaire_type, valid_scores, question_id)
            
            # 如果仍然无法解析，且尝试次数少于3次，则重试
            if score is None and attempt < 3:
                print(f"问题{question_id}回答格式不正确: '{answer_text[:100]}'，正在重试...")
                time.sleep(1)
                return self.ask_questionnaire_question(agent, question_id, test_round, attempt + 1)
            
            # 最后尝试失败，根据抑郁程度给出默认值
            if score is None:
                print(f"问题{question_id}解析失败: '{answer_text[:100]}'，使用默认值")
                score = self._get_default_score(agent, valid_scores)
                answer_text = f"[解析失败-默认值] {answer_text}"
            
            # 保存交互数据到Agent目录
            if hasattr(self, 'current_agent_dir') and self.current_agent_dir:
                self._save_question_interaction(
                    self.current_agent_dir, question_id, prompt, answer_text, score, test_round
                )
            
            return (score, answer_text, question_text, prompt)
                
        except Exception as e:
            print(f"询问问题{question_id}时出错: {e}")
            print(f"提示词长度: {len(prompt)} 字符")
            if attempt < 3:
                print(f"问题{question_id}调用失败，正在重试...")
                time.sleep(2)
                return self.ask_questionnaire_question(agent, question_id, test_round, attempt + 1)
            
            # 默认值处理
            print(f"问题{question_id}多次调用失败，使用默认值")
            default_score = self._get_default_score(agent, valid_scores)
            
            # 保存错误信息
            error_response = f"[API调用失败: {str(e)}]"
            if hasattr(self, 'current_agent_dir') and self.current_agent_dir:
                self._save_question_interaction(
                    self.current_agent_dir, question_id, prompt, error_response, default_score, test_round
                )
            
            return (default_score, error_response, question_text, prompt)
    
    def _get_default_score(self, agent: PatientAgent, valid_scores: List[int]) -> int:
        """根据抑郁程度获取默认分数"""
        if agent.depression_level == "正常":
            return valid_scores[0]  # 最低分
        elif agent.depression_level == "轻度":
            return valid_scores[1] if len(valid_scores) > 1 else valid_scores[0]
        elif agent.depression_level == "中度":
            return valid_scores[2] if len(valid_scores) > 2 else valid_scores[-1]
        else:  # 重度
            return valid_scores[-1]  # 最高分
    
    def _parse_text_answer(self, answer_text: str, questionnaire_type: str, valid_scores: List[int], question_id: int = None) -> int:
        """尝试从文本中解析答案"""
        answer_text_lower = answer_text.lower()
        
        if questionnaire_type == "PHQ-9":
            if any(word in answer_text_lower for word in ['完全不会', '没有', '不会', '从不']):
                return 0
            elif any(word in answer_text_lower for word in ['有过几天', '偶尔', '有时']):
                return 1  
            elif any(word in answer_text_lower for word in ['一半以上', '经常', '大部分']):
                return 2
            elif any(word in answer_text_lower for word in ['几乎每天', '总是', '每天']):
                return 3
        elif questionnaire_type == "SDS":
            # SDS选项解析：需要根据题目类型（正向/反向）来确定最终分数
            # 先解析出选项索引 - 注意匹配顺序，更精确的匹配在前面
            option_index = None
            if any(word in answer_text_lower for word in ['绝大部分', '全部', '总是', '每天']):
                option_index = 3  # 对应"绝大部分或全部时间"
            elif any(word in answer_text_lower for word in ['相当多', '经常', '大部分']):
                option_index = 2  # 对应"相当多时间"
            elif any(word in answer_text_lower for word in ['小部分', '偶尔', '有时']):
                option_index = 1  # 对应"小部分时间"
            elif any(word in answer_text_lower for word in ['没有', '很少', '从不']):
                option_index = 0  # 对应"没有或很少时间"
            
            # 根据题目类型确定最终分数
            if option_index is not None and question_id is not None:
                from config.questionnaire_config import SDS_QUESTIONNAIRE
                question_data = SDS_QUESTIONNAIRE["questions"][question_id - 1]
                question_type = question_data.get("type", "positive")
                
                if question_type == "negative":
                    # 反向题：选项分数为[4, 3, 2, 1]
                    return [4, 3, 2, 1][option_index]
                else:
                    # 正向题：选项分数为[1, 2, 3, 4]
                    return [1, 2, 3, 4][option_index]
            elif option_index is not None:
                # 如果没有question_id，默认按正向题处理
                return [1, 2, 3, 4][option_index]
        
        return None
    
    def _get_agent_expected_score(self, agent: PatientAgent, question_id: int) -> int:
        """
        获取Agent预设的某个问题的分数
        
        Args:
            agent: 患者代理
            question_id: 问题ID
            
        Returns:
            int: Agent预设的分数
        """
        if agent.questionnaire_type == "PHQ-9":
            # 从agent的预设分数中获取
            if hasattr(agent, 'phq9_scores') and agent.phq9_scores:
                if question_id <= len(agent.phq9_scores):
                    return agent.phq9_scores[question_id - 1]
            # 如果没有预设分数，返回默认值
            return self._get_default_score(agent, [0, 1, 2, 3])
            
        elif agent.questionnaire_type == "SDS":
            # 从agent的预设分数中获取
            if hasattr(agent, 'sds_scores') and agent.sds_scores:
                if question_id <= len(agent.sds_scores):
                    return agent.sds_scores[question_id - 1]
            # 如果没有预设分数，返回默认值
            return self._get_default_score(agent, [1, 2, 3, 4])
        
        return 0
    
    def conduct_single_questionnaire_test(self, agent: PatientAgent) -> Tuple[List[Dict], int]:
        """
        对Agent进行一次完整的量表测试
        
        Args:
            agent: 患者代理
            
        Returns:
            Tuple[List[Dict], int]: (详细回答列表, 总分)
        """
        detailed_answers = []
        scores = []
        
        questionnaire_type = agent.questionnaire_type
        print(f"\n开始对患者 {agent.patient_id} 进行{questionnaire_type}测试...")
        
        if questionnaire_type == "PHQ-9":
            # PHQ-9只问前9个问题，计入总分
            total_questions = 9
        elif questionnaire_type == "SDS":
            # SDS有20个问题，全部计入总分
            total_questions = 20
        else:
            raise ValueError(f"不支持的量表类型: {questionnaire_type}")
        
        # 询问所有问题
        for question_id in range(1, total_questions + 1):
            print(f"  询问问题 {question_id}/{total_questions}...")
            score, answer_text, question_text, full_prompt = self.ask_questionnaire_question(agent, question_id)
            
            # 获取Agent预设的分数（用于对比）
            expected_score = self._get_agent_expected_score(agent, question_id)
            
            # 记录详细答案，包括完整的提示词
            answer_detail = {
                'question_id': question_id,
                'question_text': question_text,
                'agent_answer': answer_text,
                'llm_response_score': score,  # LLM实际回答的分数
                'agent_expected_score': expected_score,  # Agent预设的分数
                'score_match': score == expected_score,  # 分数是否匹配
                'timestamp': datetime.now().isoformat(),
                'full_prompt': full_prompt  # 保存完整的提示词
            }
            
            # 对于SDS，所有题目的分数都直接累加，不需要再次转换
            if questionnaire_type == "SDS":
                # LLM回答解析出的分数就是该题的最终分数
                # 在_parse_text_answer中已经根据题目类型(正向/反向)处理了分数转换
                scores.append(score)
                answer_detail['sds_final_score'] = score
            else:
                # PHQ-9直接使用原始分数，所有问题都计入总分
                scores.append(score)
            
            detailed_answers.append(answer_detail)
            time.sleep(0.5)  # 避免API调用过于频繁(0.5)  # 避免API调用过于频繁
        
        # 计算总分
        if questionnaire_type == "SDS":
            # SDS需要将原始分乘以1.25得到标准分
            raw_total = sum(scores)
            total_score = int(raw_total * 1.25)
        else:
            # PHQ-9直接求和
            total_score = sum(scores)
        
        print(f"  测试完成！总分: {total_score}")
        return detailed_answers, total_score
    
    def conduct_stability_test(self, agent: PatientAgent, num_tests: int = 5) -> Dict[str, Any]:
        """
        对Agent进行多次量表测试以验证稳定性
        
        Args:
            agent: 患者代理
            num_tests: 测试次数，默认5次
            
        Returns:
            Dict[str, Any]: 包含所有测试结果和统计信息的字典
        """
        questionnaire_type = agent.questionnaire_type
        
        # 根据量表类型获取分数范围
        if questionnaire_type == "PHQ-9":
            score_ranges = PHQ9_SCORE_RANGES
        elif questionnaire_type == "SDS":
            score_ranges = SDS_SCORE_RANGES
        else:
            raise ValueError(f"不支持的量表类型: {questionnaire_type}")
        
        print(f"\n{'='*60}")
        print(f"开始稳定性测试：患者 {agent.patient_id}")
        print(f"量表类型：{questionnaire_type}")
        print(f"预期抑郁程度：{agent.depression_level}")
        print(f"预期{questionnaire_type}分数范围：{score_ranges[agent.depression_level]}")
        print(f"测试次数：{num_tests}")
        print(f"{'='*60}")
        
        all_tests = []
        all_scores = []
        
        for test_num in range(1, num_tests + 1):
            print(f"\n第 {test_num}/{num_tests} 次测试")
            detailed_answers, total_score = self.conduct_single_questionnaire_test(agent)
            
            test_result = {
                'test_number': test_num,
                'timestamp': datetime.now().isoformat(),
                'detailed_answers': detailed_answers,
                'llm_total_score': total_score,  # LLM实际回答得到的总分
                'depression_classification': self._classify_depression_by_score(total_score, questionnaire_type),
                'score_statistics': self._calculate_test_score_statistics(detailed_answers, questionnaire_type)
            }
            
            all_tests.append(test_result)
            all_scores.append(total_score)
            
            # 在测试间隔添加短暂延迟
            if test_num < num_tests:
                time.sleep(2)
        
        # 计算统计信息
        stats = self._calculate_statistics(all_scores, agent.depression_level, questionnaire_type)
        
        # 生成详细报告
        stability_report = {
            'llm_info': {
                'model_name': self.model,
                'text_generator_type': type(self.text_generator).__name__
            },
            'agent_info': {
                'patient_id': agent.patient_id,
                'age': agent.age,
                'gender': agent.gender,
                'education': agent.education,
                'occupation': agent.occupation,
                'questionnaire_type': questionnaire_type,
                'expected_depression_level': agent.depression_level,
                'expected_score_range': score_ranges[agent.depression_level]
            },
            'test_settings': {
                'num_tests': num_tests,
                'test_date': datetime.now().isoformat()
            },
            'individual_tests': all_tests,
            'statistics': stats,
            'stability_assessment': self._assess_stability(stats)
        }
        
        # 打印结果摘要
        self._print_test_summary(stability_report)
        
        return stability_report
    
    def _classify_depression_by_score(self, score: int, questionnaire_type: str) -> str:
        """根据量表分数分类抑郁程度"""
        if questionnaire_type == "PHQ-9":
            score_ranges = PHQ9_SCORE_RANGES
        elif questionnaire_type == "SDS":
            score_ranges = SDS_SCORE_RANGES
        else:
            return "未知"
            
        for level, (min_score, max_score) in score_ranges.items():
            if min_score <= score <= max_score:
                return level
        return "未知"
    
    def _calculate_statistics(self, scores: List[int], expected_level: str, questionnaire_type: str) -> Dict[str, Any]:
        """计算统计信息"""
        if questionnaire_type == "PHQ-9":
            score_ranges = PHQ9_SCORE_RANGES
        elif questionnaire_type == "SDS":
            score_ranges = SDS_SCORE_RANGES
        else:
            raise ValueError(f"不支持的量表类型: {questionnaire_type}")
            
        expected_range = score_ranges[expected_level]
        
        stats = {
            'questionnaire_type': questionnaire_type,
            'scores': scores,
            'mean': statistics.mean(scores),
            'median': statistics.median(scores),
            'std_dev': statistics.stdev(scores) if len(scores) > 1 else 0,
            'min_score': min(scores),
            'max_score': max(scores),
            'range': max(scores) - min(scores),
            'expected_range': expected_range,
            'expected_mean': (expected_range[0] + expected_range[1]) / 2,
            'scores_in_expected_range': sum(1 for s in scores if expected_range[0] <= s <= expected_range[1]),
            'percentage_in_range': sum(1 for s in scores if expected_range[0] <= s <= expected_range[1]) / len(scores) * 100,
            'coefficient_of_variation': (statistics.stdev(scores) / statistics.mean(scores)) * 100 if len(scores) > 1 and statistics.mean(scores) > 0 else 0
        }
        
        return stats
    
    def _assess_stability(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """评估稳定性"""
        cv = stats['coefficient_of_variation']
        percentage_in_range = stats['percentage_in_range']
        score_range = stats['range']
        
        # 稳定性评级标准
        if cv <= 10 and percentage_in_range >= 80 and score_range <= 3:
            stability_level = "优秀"
            stability_score = 5
        elif cv <= 20 and percentage_in_range >= 60 and score_range <= 5:
            stability_level = "良好"  
            stability_score = 4
        elif cv <= 30 and percentage_in_range >= 40 and score_range <= 7:
            stability_level = "一般"
            stability_score = 3
        elif cv <= 40 and percentage_in_range >= 20 and score_range <= 10:
            stability_level = "较差"
            stability_score = 2
        else:
            stability_level = "很差"
            stability_score = 1
        
        return {
            'stability_level': stability_level,
            'stability_score': stability_score,
            'coefficient_of_variation': cv,
            'percentage_in_expected_range': percentage_in_range,
            'score_range': score_range,
            'assessment_criteria': {
                'cv_threshold': "变异系数应 ≤ 20%",
                'range_threshold': "分数在预期范围内的比例应 ≥ 60%", 
                'score_range_threshold': "分数波动范围应 ≤ 5分"
            }
        }
    
    def _print_test_summary(self, report: Dict[str, Any]):
        """打印测试结果摘要"""
        llm_info = report['llm_info']
        agent_info = report['agent_info']
        stats = report['statistics']
        stability = report['stability_assessment']
        questionnaire_type = agent_info['questionnaire_type']
        
        print(f"\n{'='*60}")
        print(f"{questionnaire_type}稳定性测试报告")
        print(f"{'='*60}")
        
        print(f"\n🤖 LLM信息:")
        print(f"  模型名称: {llm_info['model_name']}")
        print(f"  生成器类型: {llm_info['text_generator_type']}")
        
        print(f"\n📊 患者信息:")
        print(f"  ID: {agent_info['patient_id']}")
        print(f"  基本信息: {agent_info['age']}岁 {agent_info['gender']}性")
        print(f"  量表类型: {questionnaire_type}")
        print(f"  预期抑郁程度: {agent_info['expected_depression_level']}")
        print(f"  预期分数范围: {agent_info['expected_score_range'][0]}-{agent_info['expected_score_range'][1]}分")
        
        print(f"\n📈 测试结果统计:")
        print(f"  测试次数: {len(stats['scores'])}次")
        print(f"  LLM实际分数: {stats['scores']}")
        print(f"  平均分: {stats['mean']:.2f}分")
        print(f"  标准差: {stats['std_dev']:.2f}")
        print(f"  分数范围: {stats['min_score']}-{stats['max_score']}分 (波动{stats['range']}分)")
        print(f"  变异系数: {stats['coefficient_of_variation']:.2f}%")
        print(f"  预期范围内: {stats['scores_in_expected_range']}/{len(stats['scores'])}次 ({stats['percentage_in_range']:.1f}%)")
        
        # 显示分数对比信息
        if len(report['individual_tests']) > 0:
            first_test = report['individual_tests'][0]
            score_stats = first_test.get('score_statistics', {})
            if score_stats:
                print(f"\n📊 分数对比分析:")
                print(f"  Agent预设总分: {score_stats.get('agent_expected_total_score', 'N/A')}分")
                print(f"  LLM实际总分: {score_stats.get('llm_response_total_score', 'N/A')}分")
                score_diff = score_stats.get('score_difference', 0)
                print(f"  分数差异: {score_diff:+d}分 ({'✅' if abs(score_diff) <= 3 else '⚠️' if abs(score_diff) <= 6 else '❌'})")
                match_rate = score_stats.get('score_match_rate', 0) * 100
                print(f"  单题匹配率: {match_rate:.1f}% ({'✅' if match_rate >= 70 else '⚠️' if match_rate >= 50 else '❌'})")
        
        print(f"\n🎯 稳定性评估:")
        print(f"  稳定性等级: {stability['stability_level']} ({stability['stability_score']}/5)")
        print(f"  变异系数: {stability['coefficient_of_variation']:.2f}% ({'✅' if stability['coefficient_of_variation'] <= 20 else '❌'} ≤20%)")
        print(f"  预期范围内比例: {stability['percentage_in_expected_range']:.1f}% ({'✅' if stability['percentage_in_expected_range'] >= 60 else '❌'} ≥60%)")
        print(f"  分数波动范围: {stability['score_range']}分 ({'✅' if stability['score_range'] <= 5 else '❌'} ≤5分)")
        
        # 给出建议
        print(f"\n💡 建议:")
        if stability['stability_score'] >= 4:
            print("  Agent的心理状态表现稳定，可以用于数据生成。")
        elif stability['stability_score'] >= 3:
            print("  Agent的稳定性基本可接受，建议进行微调优化。")
        else:
            print("  Agent的稳定性较差，建议检查以下方面：")
            print("    - 提示词是否足够明确和具体")
            print("    - LLM的temperature参数是否过高")
            print("    - Agent的心理状态描述是否存在矛盾")
            print("    - Agent预设分数与LLM实际回答的匹配度")
        
        print(f"{'='*60}")
    
    def _calculate_test_score_statistics(self, detailed_answers: List[Dict], questionnaire_type: str) -> Dict[str, Any]:
        """
        计算单次测试的分数统计信息
        
        Args:
            detailed_answers: 详细答案列表
            questionnaire_type: 量表类型
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        total_questions = len(detailed_answers)
        
        # 统计分数匹配情况
        score_matches = [answer['score_match'] for answer in detailed_answers if 'score_match' in answer]
        match_count = sum(score_matches)
        match_rate = match_count / len(score_matches) if score_matches else 0
        
        # 计算预设总分和实际总分
        expected_total = sum([answer['agent_expected_score'] for answer in detailed_answers 
                             if 'agent_expected_score' in answer])
        
        llm_total = sum([answer['llm_response_score'] for answer in detailed_answers 
                        if 'llm_response_score' in answer])
        
        # 对于SDS，需要考虑反向题转换
        if questionnaire_type == "SDS":
            sds_total = sum([answer.get('sds_actual_score', answer['llm_response_score']) 
                           for answer in detailed_answers if 'llm_response_score' in answer])
            sds_expected_total = int(expected_total * 1.25) if expected_total > 0 else 0
            sds_llm_total = int(sds_total * 1.25)
            
            return {
                'total_questions': total_questions,
                'score_match_count': match_count,
                'score_match_rate': match_rate,
                'agent_expected_total_score': sds_expected_total,
                'llm_response_total_score': sds_llm_total,
                'score_difference': sds_llm_total - sds_expected_total,
                'raw_expected_total': expected_total,
                'raw_llm_total': sds_total
            }
        else:
            return {
                'total_questions': total_questions,
                'score_match_count': match_count,
                'score_match_rate': match_rate,
                'agent_expected_total_score': expected_total,
                'llm_response_total_score': llm_total,
                'score_difference': llm_total - expected_total
            }
    
    def _create_agent_directory(self, agent: PatientAgent) -> str:
        """
        为Agent创建专用目录
        
        Args:
            agent: 患者代理
            
        Returns:
            str: Agent目录路径
        """
        agent_dir = os.path.join(self.save_base_dir, agent.patient_id)
        os.makedirs(agent_dir, exist_ok=True)
        
        # 保存Agent的基本信息
        agent_info_file = os.path.join(agent_dir, "agent_info.json")
        if not os.path.exists(agent_info_file):
            agent_info = {
                'patient_id': agent.patient_id,
                'age': agent.age,
                'gender': agent.gender,
                'education': agent.education,
                'occupation': agent.occupation,
                'marital_status': agent.marital_status,
                'questionnaire_type': agent.questionnaire_type,
                'depression_level': agent.depression_level,
                'depression_tag': agent.depression_tag,
                'score': agent.score,
                'personality': agent.personality,
                'language_style': agent.language_style,
                'expression_tone': agent.expression_tone,
                'hiding_tendency': agent.hiding_tendency,
                'core_belief': agent.core_belief,
                'intermediate_belief': agent.intermediate_belief,
                'depressed_belief': agent.depressed_belief,
                'coping_strategy': agent.coping_strategy,
                'main_emotion': agent.main_emotion,
                'automatic_thought': agent.automatic_thought,
                'typical_behavior': agent.typical_behavior,
                'created_time': datetime.now().isoformat()
            }
            
            # 保存预设分数
            if hasattr(agent, 'phq9_scores') and agent.phq9_scores:
                agent_info['phq9_scores'] = agent.phq9_scores
            if hasattr(agent, 'sds_scores') and agent.sds_scores:
                agent_info['sds_scores'] = agent.sds_scores
            
            with open(agent_info_file, 'w', encoding='utf-8') as f:
                json.dump(agent_info, f, ensure_ascii=False, indent=2)
        
        return agent_dir
    
    def _save_question_interaction(self, agent_dir: str, question_id: int, 
                                 prompt: str, response: str, score: int, 
                                 test_round: int = 1) -> str:
        """
        保存单个问题的交互数据
        
        Args:
            agent_dir: Agent目录路径
            question_id: 问题ID
            prompt: 完整提示词
            response: LLM回答
            score: 解析出的分数
            test_round: 测试轮次
            
        Returns:
            str: 保存的文件路径
        """
        # 创建测试轮次目录
        round_dir = os.path.join(agent_dir, f"round_{test_round:03d}")
        os.makedirs(round_dir, exist_ok=True)
        
        # 保存交互数据
        interaction_file = os.path.join(round_dir, f"question_{question_id:02d}.json")
        interaction_data = {
            'question_id': question_id,
            'test_round': test_round,
            'model': self.model,
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt,
            'llm_response': response,
            'parsed_score': score,
            'prompt_length': len(prompt),
            'response_length': len(response) if response else 0
        }
        
        with open(interaction_file, 'w', encoding='utf-8') as f:
            json.dump(interaction_data, f, ensure_ascii=False, indent=2)
        
        return interaction_file
    
    def _save_test_round_summary(self, agent_dir: str, test_round: int, 
                               detailed_answers: List[Dict], total_score: int) -> str:
        """
        保存单轮测试的汇总数据
        
        Args:
            agent_dir: Agent目录路径
            test_round: 测试轮次
            detailed_answers: 详细答案列表
            total_score: 总分
            
        Returns:
            str: 保存的文件路径
        """
        round_dir = os.path.join(agent_dir, f"round_{test_round:03d}")
        summary_file = os.path.join(round_dir, "round_summary.json")
        
        summary_data = {
            'test_round': test_round,
            'model': self.model,
            'timestamp': datetime.now().isoformat(),
            'total_score': total_score,
            'total_questions': len(detailed_answers),
            'detailed_answers': detailed_answers,
            'score_statistics': self._calculate_test_score_statistics(detailed_answers, 
                                                                    detailed_answers[0]['question_id'] if detailed_answers else "PHQ-9")
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        return summary_file
def save_test_results(results: Dict[str, Any], filepath: str):
    """保存测试结果到文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n测试结果已保存到: {filepath}")

def load_test_results(filepath: str) -> Dict[str, Any]:
    """从文件加载测试结果"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def batch_stability_test(
    agents: List[PatientAgent], 
    num_tests: int = 5, 
    save_dir: str = "stability_results",
    model: str = "gpt-3.5-turbo",
    api_key: str = None
) -> List[Dict[str, Any]]:
    """
    批量测试多个Agent的稳定性
    
    Args:
        agents: 患者代理列表
        num_tests: 每个Agent的测试次数
        save_dir: 结果保存目录
        model: 要使用的LLM模型名称
        api_key: API密钥，如果为None则从环境变量获取
        
    Returns:
        List[Dict[str, Any]]: 所有测试结果列表
    """
    os.makedirs(save_dir, exist_ok=True)
    tester = QuestionnaireStabilityTester(model=model, api_key=api_key)
    all_results = []
    
    print(f"\n开始批量稳定性测试，共{len(agents)}个Agent")
    print(f"使用模型: {model}")
    
    for i, agent in enumerate(agents, 1):
        print(f"\n{'='*80}")
        print(f"测试进度: {i}/{len(agents)}")
        
        # 进行稳定性测试
        results = tester.conduct_stability_test(agent, num_tests)
        all_results.append(results)
        
        # 保存单个结果
        filename = f"{save_dir}/stability_test_{agent.patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_test_results(results, filename)
        
        # 休息一下，避免API调用过于密集
        if i < len(agents):
            print(f"休息5秒后继续下一个测试...")
            time.sleep(5)
    
    # 生成汇总报告
    summary_report = generate_batch_summary(all_results)
    summary_filename = f"{save_dir}/batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_test_results(summary_report, summary_filename)
    
    return all_results

def generate_batch_summary(all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成批量测试的汇总报告"""
    summary = {
        'total_agents': len(all_results),
        'test_date': datetime.now().isoformat(),
        'stability_distribution': {},
        'average_metrics': {},
        'best_performers': [],
        'worst_performers': []
    }
    
    # 统计稳定性等级分布
    stability_levels = [r['stability_assessment']['stability_level'] for r in all_results]
    for level in stability_levels:
        summary['stability_distribution'][level] = summary['stability_distribution'].get(level, 0) + 1
    
    # 计算平均指标
    all_cvs = [r['stability_assessment']['coefficient_of_variation'] for r in all_results]
    all_percentages = [r['stability_assessment']['percentage_in_expected_range'] for r in all_results]
    all_ranges = [r['stability_assessment']['score_range'] for r in all_results]
    all_scores = [r['stability_assessment']['stability_score'] for r in all_results]
    
    summary['average_metrics'] = {
        'average_cv': statistics.mean(all_cvs),
        'average_percentage_in_range': statistics.mean(all_percentages),
        'average_score_range': statistics.mean(all_ranges),
        'average_stability_score': statistics.mean(all_scores)
    }
    
    # 找出最佳和最差表现者
    sorted_results = sorted(all_results, key=lambda x: x['stability_assessment']['stability_score'], reverse=True)
    summary['best_performers'] = [
        {
            'patient_id': r['agent_info']['patient_id'],
            'stability_score': r['stability_assessment']['stability_score'],
            'stability_level': r['stability_assessment']['stability_level']
        }
        for r in sorted_results[:3]  # 前3名
    ]
    
    summary['worst_performers'] = [
        {
            'patient_id': r['agent_info']['patient_id'],
            'stability_score': r['stability_assessment']['stability_score'],
            'stability_level': r['stability_assessment']['stability_level']
        }
        for r in sorted_results[-3:]  # 后3名
    ]
    
    return summary

if __name__ == "__main__":
    # 示例代码：创建测试Agent并进行稳定性测试
    print("心理量表稳定性测试系统启动")
    
    # 检查可用的API密钥
    available_models = []
    if os.getenv("OPENAI_API_KEY"):
        available_models.extend(["gpt-3.5-turbo", "gpt-4", "gpt-4o"])
    if os.getenv("DEEPSEEK_API_KEY"):
        available_models.append("deepseek-chat")
    if os.getenv("GEMINI_API_KEY"):
        available_models.append("gemini-pro")
    
    print(f"\n📋 检测到可用的API密钥对应的模型: {available_models}")
    
    if not available_models:
        print("❌ 未检测到任何API密钥!")
        print("请设置以下环境变量之一:")
        print("  export OPENAI_API_KEY='your-openai-key'")
        print("  export DEEPSEEK_API_KEY='your-deepseek-key'")
        print("  export GEMINI_API_KEY='your-gemini-key'")
        exit(1)
    
    
    # 创建几个不同抑郁程度和量表类型的测试Agent
    test_agents = []
    
    # # 正常状态 - PHQ-9
    # normal_agent_phq9 = PatientAgent(
    #     age=25,
    #     gender="女",
    #     education="本科",
    #     occupation="办公室职员",
    #     depression_level="正常",
    #     questionnaire_type="PHQ-9",
    #     patient_id="test_normal_phq9_001"
    # )
    # test_agents.append(normal_agent_phq9)
    #
    # # 轻度抑郁 - PHQ-9
    # mild_agent_phq9 = PatientAgent(
    #     age=22,
    #     gender="男",
    #     education="本科",
    #     occupation="学生",
    #     depression_level="轻度",
    #     questionnaire_type="PHQ-9",
    #     patient_id="test_mild_phq9_001"
    # )
    # test_agents.append(mild_agent_phq9)
    
    # 中度抑郁 - SDS
    moderate_agent_sds = PatientAgent(
        age=28,
        gender="女",
        education="硕士", 
        occupation="办公室职员",
        depression_level="中度",
        questionnaire_type="SDS",
        patient_id="test_moderate_sds_001"
    )
    test_agents.append(moderate_agent_sds)
    
    # 执行批量稳定性测试
    # 现在可以方便地切换模型了！
    try:
        # 使用已经测试成功的模型
        results = batch_stability_test(
            test_agents, 
            num_tests=1,  # 为了演示，每个Agent测试1次
            model="gpt-4.1"
        )
        print(f"\n批量测试完成！共测试了{len(results)}个Agent")
        
        # 如果想测试其他模型，可以这样：
        # results_deepseek = batch_stability_test(
        #     test_agents, 
        #     num_tests=3,
        #     model="deepseek-chat",
        #     save_dir="stability_results_deepseek"
        # )
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        print("请检查LLM客户端配置和API密钥设置")