# -*- coding: utf-8 -*-
"""
多模型稳定性测试模块
用于测试同一个Agent在不同LLM模型下的稳定性表现
支持PHQ-9和SDS量表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PHQ9_QUESTIONNAIRE, PHQ9_SCORE_RANGES, SDS_QUESTIONNAIRE, SDS_SCORE_RANGES
from core.agent_base import PatientAgent
from utils.clients.text_generator import TextGenerator
from stability_analysis.phq_9_test import QuestionnaireStabilityTester
import json
import time
from typing import Dict, List, Any, Tuple
from datetime import datetime
import random
import statistics


class MultiModelStabilityTester:
    """多模型稳定性测试器"""
    
    def __init__(self, save_base_dir: str = "stability_analysis/model_comparison_results"):
        """
        初始化多模型测试器
        
        Args:
            save_base_dir: 数据保存基础目录
        """
        self.save_base_dir = save_base_dir
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_PROXY_BASE_URL", "https://api.openai.com/v1")
        
        # 确保保存目录存在
        os.makedirs(self.save_base_dir, exist_ok=True)
        
        # 常用模型列表
        self.common_models = [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4o",
            "gpt-4-turbo",
            "deepseek-chat",
            "deepseek-coder",
            "claude-3-haiku",
            "claude-3-sonnet",
            "gemini-pro",
            "llama-3-8b",
            "llama-3-70b",
            "qwen-turbo",
            "qwen-plus",
            "qwen-max"
        ]
        
        print(f"使用API密钥: {'已设置' if self.api_key else '未设置'}")
        print(f"使用代理URL: {self.base_url}")
    
    def test_models_connectivity(self, models: List[str]) -> List[str]:
        """
        测试所有模型的连接性
        
        Args:
            models: 要测试的模型列表
            
        Returns:
            List[str]: 连接成功的模型列表
        """
        print(f"\n{'='*60}")
        print(f"开始测试模型连接性")
        print(f"{'='*60}")
        
        available_models = []
        
        for model in models:
            print(f"测试模型: {model}...")
            try:
                # 创建一个临时的测试器来测试连接
                from utils.clients.text_generator import TextGenerator
                text_generator = TextGenerator(model)
                
                # 发送一个简单的测试请求
                test_response = text_generator.generate("请回答：你好")
                
                if test_response and len(test_response.strip()) > 0:
                    print(f"✅ {model} - 连接成功")
                    available_models.append(model)
                else:
                    print(f"❌ {model} - 响应为空")
                    
            except Exception as e:
                print(f"❌ {model} - 连接失败: {str(e)[:100]}")
                continue
            
            # 添加延迟避免API限制
            time.sleep(2)
        
        print(f"\n连接测试完成:")
        print(f"  测试模型数: {len(models)}")
        print(f"  可用模型数: {len(available_models)}")
        print(f"  可用模型: {available_models}")
        
        if not available_models:
            raise Exception("没有可用的模型！请检查API配置和网络连接。")
        
        return available_models
    
    def get_agent_folder_name(self, agent: PatientAgent) -> str:
        """
        生成Agent文件夹名称
        
        Args:
            agent: 患者代理
            
        Returns:
            str: 文件夹名称
        """
        questionnaire_type = agent.questionnaire_type.lower().replace("-", "")
        return f"{agent.patient_id}_{questionnaire_type}_{agent.depression_level}"
    
    def create_agent_directory(self, agent: PatientAgent) -> str:
        """
        为Agent创建专用目录
        
        Args:
            agent: 患者代理
            
        Returns:
            str: Agent目录路径
        """
        agent_folder_name = self.get_agent_folder_name(agent)
        agent_dir = os.path.join(self.save_base_dir, agent_folder_name)
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
                'marital_status': getattr(agent, 'marital_status', 'unknown'),
                'questionnaire_type': agent.questionnaire_type,
                'depression_level': agent.depression_level,
                'depression_tag': getattr(agent, 'depression_tag', ''),
                'score': getattr(agent, 'score', 0),
                'personality': getattr(agent, 'personality', ''),
                'language_style': getattr(agent, 'language_style', ''),
                'expression_tone': getattr(agent, 'expression_tone', ''),
                'hiding_tendency': getattr(agent, 'hiding_tendency', ''),
                'core_belief': getattr(agent, 'core_belief', ''),
                'intermediate_belief': getattr(agent, 'intermediate_belief', ''),
                'depressed_belief': getattr(agent, 'depressed_belief', ''),
                'coping_strategy': getattr(agent, 'coping_strategy', ''),
                'main_emotion': getattr(agent, 'main_emotion', ''),
                'automatic_thought': getattr(agent, 'automatic_thought', ''),
                'typical_behavior': getattr(agent, 'typical_behavior', ''),
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
    
    def test_single_model_multiple_times(self, agent: PatientAgent, model: str, 
                                       num_tests: int = 5) -> Dict[str, Any]:
        """
        测试单个模型多次运行的稳定性
        
        Args:
            agent: 患者代理
            model: 模型名称
            num_tests: 测试次数
            
        Returns:
            Dict[str, Any]: 测试结果
        """
        print(f"\n{'='*60}")
        print(f"开始测试模型: {model}")
        print(f"Agent: {agent.patient_id}")
        print(f"量表类型: {agent.questionnaire_type}")
        print(f"测试次数: {num_tests}")
        print(f"{'='*60}")
        
        # 创建测试器
        tester = QuestionnaireStabilityTester(
            model=model,
            api_key=self.api_key,
            base_url=self.base_url,
            save_base_dir=self.save_base_dir
        )
        
        # 测试连接
        if not tester.test_connection():
            raise Exception(f"模型 {model} 连接失败")
        
        # 进行稳定性测试
        results = tester.conduct_stability_test(agent, num_tests)
        
        # 添加模型信息
        results['model_info'] = {
            'model_name': model,
            'api_base_url': self.base_url,
            'test_timestamp': datetime.now().isoformat()
        }
        
        return results
    
    def test_agent_across_models(self, agent: PatientAgent, models: List[str], 
                                num_tests_per_model: int = 5) -> Dict[str, Any]:
        """
        测试单个Agent在多个模型下的表现
        
        Args:
            agent: 患者代理
            models: 要测试的模型列表
            num_tests_per_model: 每个模型的测试次数
            
        Returns:
            Dict[str, Any]: 所有模型的测试结果
        """
        # 创建Agent目录
        agent_dir = self.create_agent_directory(agent)
        
        print(f"\n{'='*80}")
        print(f"开始多模型测试")
        print(f"Agent: {agent.patient_id} ({agent.questionnaire_type})")
        print(f"要测试的模型: {models}")
        print(f"每个模型测试次数: {num_tests_per_model}")
        print(f"结果保存到: {agent_dir}")
        print(f"{'='*80}")
        
        all_model_results = {}
        
        for i, model in enumerate(models, 1):
            print(f"\n进度: {i}/{len(models)} - 正在测试模型: {model}")
            
            try:
                # 测试单个模型
                model_results = self.test_single_model_multiple_times(
                    agent, model, num_tests_per_model
                )
                
                all_model_results[model] = model_results
                
                # 保存单个模型的结果
                model_filename = f"{model.replace('/', '_').replace('-', '_')}_results.json"
                model_filepath = os.path.join(agent_dir, model_filename)
                
                with open(model_filepath, 'w', encoding='utf-8') as f:
                    json.dump(model_results, f, ensure_ascii=False, indent=2)
                
                print(f"✅ 模型 {model} 测试完成，结果已保存到: {model_filename}")
                
                # 在模型间添加延迟，避免API调用过于频繁
                if i < len(models):
                    print(f"休息3秒后继续下一个模型...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"❌ 模型 {model} 测试失败: {e}")
                all_model_results[model] = {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                continue
        
        # 生成跨模型比较报告
        comparison_report = self.generate_model_comparison_report(all_model_results, agent)
        
        # 保存比较报告
        comparison_filename = os.path.join(agent_dir, "model_comparison_report.json")
        with open(comparison_filename, 'w', encoding='utf-8') as f:
            json.dump(comparison_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎯 跨模型比较报告已保存到: model_comparison_report.json")
        
        # 打印比较摘要
        self.print_model_comparison_summary(comparison_report)
        
        return {
            'agent_info': {
                'patient_id': agent.patient_id,
                'questionnaire_type': agent.questionnaire_type,
                'depression_level': agent.depression_level
            },
            'test_settings': {
                'models_tested': models,
                'num_tests_per_model': num_tests_per_model,
                'test_date': datetime.now().isoformat()
            },
            'model_results': all_model_results,
            'comparison_report': comparison_report,
            'save_directory': agent_dir
        }
    
    def generate_model_comparison_report(self, all_model_results: Dict[str, Any], 
                                       agent: PatientAgent) -> Dict[str, Any]:
        """
        生成模型比较报告
        
        Args:
            all_model_results: 所有模型的测试结果
            agent: 患者代理
            
        Returns:
            Dict[str, Any]: 比较报告
        """
        successful_results = {k: v for k, v in all_model_results.items() 
                            if 'error' not in v}
        
        if not successful_results:
            return {
                'error': '没有成功的测试结果',
                'failed_models': list(all_model_results.keys())
            }
        
        # 收集各模型的关键指标
        model_metrics = {}
        for model, results in successful_results.items():
            stability = results.get('stability_assessment', {})
            stats = results.get('statistics', {})
            
            model_metrics[model] = {
                'stability_score': stability.get('stability_score', 0),
                'stability_level': stability.get('stability_level', '未知'),
                'coefficient_of_variation': stability.get('coefficient_of_variation', 0),
                'percentage_in_expected_range': stability.get('percentage_in_expected_range', 0),
                'score_range': stability.get('score_range', 0),
                'mean_score': stats.get('mean', 0),
                'std_dev': stats.get('std_dev', 0),
                'scores': stats.get('scores', [])
            }
        
        # 排序模型（按稳定性分数）
        sorted_models = sorted(model_metrics.items(), 
                             key=lambda x: x[1]['stability_score'], 
                             reverse=True)
        
        # 计算平均指标
        all_stability_scores = [m['stability_score'] for m in model_metrics.values()]
        all_cvs = [m['coefficient_of_variation'] for m in model_metrics.values()]
        all_percentages = [m['percentage_in_expected_range'] for m in model_metrics.values()]
        
        comparison_report = {
            'agent_info': {
                'patient_id': agent.patient_id,
                'questionnaire_type': agent.questionnaire_type,
                'depression_level': agent.depression_level,
                'expected_score_range': self.get_expected_score_range(agent)
            },
            'test_summary': {
                'total_models_tested': len(all_model_results),
                'successful_models': len(successful_results),
                'failed_models': len(all_model_results) - len(successful_results),
                'test_timestamp': datetime.now().isoformat()
            },
            'model_metrics': model_metrics,
            'ranking': {
                'best_model': {
                    'name': sorted_models[0][0],
                    'stability_score': sorted_models[0][1]['stability_score'],
                    'stability_level': sorted_models[0][1]['stability_level']
                } if sorted_models else None,
                'worst_model': {
                    'name': sorted_models[-1][0],
                    'stability_score': sorted_models[-1][1]['stability_score'],
                    'stability_level': sorted_models[-1][1]['stability_level']
                } if sorted_models else None,
                'full_ranking': [(model, metrics['stability_score']) 
                               for model, metrics in sorted_models]
            },
            'aggregate_statistics': {
                'average_stability_score': statistics.mean(all_stability_scores) if all_stability_scores else 0,
                'average_cv': statistics.mean(all_cvs) if all_cvs else 0,
                'average_percentage_in_range': statistics.mean(all_percentages) if all_percentages else 0,
                'stability_score_range': max(all_stability_scores) - min(all_stability_scores) if all_stability_scores else 0
            },
            'failed_models': [k for k, v in all_model_results.items() if 'error' in v]
        }
        
        return comparison_report
    
    def get_expected_score_range(self, agent: PatientAgent) -> List[int]:
        """获取Agent的预期分数范围"""
        if agent.questionnaire_type == "PHQ-9":
            return list(PHQ9_SCORE_RANGES[agent.depression_level])
        elif agent.questionnaire_type == "SDS":
            return list(SDS_SCORE_RANGES[agent.depression_level])
        return [0, 0]
    
    def print_model_comparison_summary(self, comparison_report: Dict[str, Any]):
        """打印模型比较摘要"""
        if 'error' in comparison_report:
            print(f"❌ 比较报告生成失败: {comparison_report['error']}")
            return
        
        agent_info = comparison_report['agent_info']
        test_summary = comparison_report['test_summary']
        ranking = comparison_report['ranking']
        aggregate_stats = comparison_report['aggregate_statistics']
        
        print(f"\n{'='*60}")
        print(f"模型比较报告摘要")
        print(f"{'='*60}")
        
        print(f"\n📊 测试概况:")
        print(f"  Agent ID: {agent_info['patient_id']}")
        print(f"  量表类型: {agent_info['questionnaire_type']}")
        print(f"  抑郁程度: {agent_info['depression_level']}")
        print(f"  预期分数范围: {agent_info['expected_score_range'][0]}-{agent_info['expected_score_range'][1]}分")
        print(f"  测试模型数: {test_summary['total_models_tested']}")
        print(f"  成功模型数: {test_summary['successful_models']}")
        print(f"  失败模型数: {test_summary['failed_models']}")
        
        if ranking['best_model']:
            print(f"\n🏆 模型排名:")
            print(f"  最佳模型: {ranking['best_model']['name']}")
            print(f"    稳定性分数: {ranking['best_model']['stability_score']}/5")
            print(f"    稳定性等级: {ranking['best_model']['stability_level']}")
            
            print(f"  最差模型: {ranking['worst_model']['name']}")
            print(f"    稳定性分数: {ranking['worst_model']['stability_score']}/5")
            print(f"    稳定性等级: {ranking['worst_model']['stability_level']}")
            
            print(f"\n📈 完整排名:")
            for i, (model, score) in enumerate(ranking['full_ranking'], 1):
                print(f"    {i}. {model}: {score}/5")
        
        print(f"\n📊 聚合统计:")
        print(f"  平均稳定性分数: {aggregate_stats['average_stability_score']:.2f}/5")
        print(f"  平均变异系数: {aggregate_stats['average_cv']:.2f}%")
        print(f"  平均预期范围内比例: {aggregate_stats['average_percentage_in_range']:.1f}%")
        print(f"  稳定性分数差异: {aggregate_stats['stability_score_range']:.2f}")
        
        if comparison_report['failed_models']:
            print(f"\n❌ 失败的模型: {', '.join(comparison_report['failed_models'])}")
        
        print(f"{'='*60}")
    
    def batch_test_multiple_agents(self, agents: List[PatientAgent], 
                                  models: List[str], 
                                  num_tests_per_model: int = 5) -> List[Dict[str, Any]]:
        """
        批量测试多个Agent在多个模型下的表现
        
        Args:
            agents: 患者代理列表
            models: 要测试的模型列表
            num_tests_per_model: 每个模型的测试次数
            
        Returns:
            List[Dict[str, Any]]: 所有Agent的测试结果
        """
        all_results = []
        
        print(f"\n{'='*80}")
        print(f"开始批量多模型测试")
        print(f"Agent数量: {len(agents)}")
        print(f"模型数量: {len(models)}")
        print(f"每个模型测试次数: {num_tests_per_model}")
        print(f"预计总测试数: {len(agents) * len(models) * num_tests_per_model}")
        print(f"{'='*80}")
        
        for i, agent in enumerate(agents, 1):
            print(f"\n{'='*60}")
            print(f"Agent进度: {i}/{len(agents)}")
            print(f"当前Agent: {agent.patient_id}")
            print(f"{'='*60}")
            
            try:
                agent_results = self.test_agent_across_models(
                    agent, models, num_tests_per_model
                )
                all_results.append(agent_results)
                
                print(f"✅ Agent {agent.patient_id} 测试完成")
                
                # 在Agent间添加延迟
                if i < len(agents):
                    print(f"休息5秒后继续下一个Agent...")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"❌ Agent {agent.patient_id} 测试失败: {e}")
                continue
        
        # 生成总体报告
        overall_report = self.generate_overall_report(all_results)
        overall_report_file = os.path.join(self.save_base_dir, 
                                         f"overall_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(overall_report_file, 'w', encoding='utf-8') as f:
            json.dump(overall_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎯 总体报告已保存到: {overall_report_file}")
        
        return all_results
    
    def generate_overall_report(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成总体报告"""
        successful_results = [r for r in all_results if 'comparison_report' in r]
        
        if not successful_results:
            return {'error': '没有成功的测试结果'}
        
        # 收集所有模型的表现数据
        model_performance = {}
        
        for result in successful_results:
            comparison_report = result['comparison_report']
            if 'model_metrics' in comparison_report:
                for model, metrics in comparison_report['model_metrics'].items():
                    if model not in model_performance:
                        model_performance[model] = []
                    model_performance[model].append(metrics['stability_score'])
        
        # 计算每个模型的平均表现
        model_avg_performance = {}
        for model, scores in model_performance.items():
            model_avg_performance[model] = {
                'average_stability_score': statistics.mean(scores),
                'stability_score_std': statistics.stdev(scores) if len(scores) > 1 else 0,
                'num_tests': len(scores),
                'scores': scores
            }
        
        # 排序模型
        sorted_models = sorted(model_avg_performance.items(),
                             key=lambda x: x[1]['average_stability_score'],
                             reverse=True)
        
        overall_report = {
            'test_summary': {
                'total_agents': len(all_results),
                'successful_agents': len(successful_results),
                'test_timestamp': datetime.now().isoformat()
            },
            'model_performance': model_avg_performance,
            'model_ranking': [(model, perf['average_stability_score']) 
                            for model, perf in sorted_models],
            'best_overall_model': {
                'name': sorted_models[0][0],
                'average_stability_score': sorted_models[0][1]['average_stability_score']
            } if sorted_models else None,
            'detailed_results': all_results
        }
        
        return overall_report


def create_comprehensive_test_agents() -> Dict[str, List[PatientAgent]]:
    """创建全面的测试Agent列表"""
    test_agents = {}
    
    # PHQ-9量表测试Agent - 每个抑郁程度5个Agent
    phq9_agents = []
    
    # 正常人群
    for i in range(5):
        agent = PatientAgent(
            depression_level="正常", 
            questionnaire_type="PHQ-9",
            patient_id=f"phq9_normal_{i+1:03d}"
        )
        phq9_agents.append(agent)
    
    # 轻度抑郁
    for i in range(5):
        agent = PatientAgent(
            depression_level="轻度", 
            questionnaire_type="PHQ-9",
            patient_id=f"phq9_mild_{i+1:03d}"
        )
        phq9_agents.append(agent)
    
    # 中度抑郁
    for i in range(5):
        agent = PatientAgent(
            depression_level="中度", 
            questionnaire_type="PHQ-9",
            patient_id=f"phq9_moderate_{i+1:03d}"
        )
        phq9_agents.append(agent)
    
    # 重度抑郁
    for i in range(5):
        agent = PatientAgent(
            depression_level="重度", 
            questionnaire_type="PHQ-9",
            patient_id=f"phq9_severe_{i+1:03d}"
        )
        phq9_agents.append(agent)
    
    test_agents["PHQ-9"] = phq9_agents
    
    # SDS量表测试Agent - 每个抑郁程度5个Agent
    sds_agents = []
    
    # 正常人群
    for i in range(5):
        agent = PatientAgent(
            depression_level="正常", 
            questionnaire_type="SDS",
            patient_id=f"sds_normal_{i+1:03d}"
        )
        sds_agents.append(agent)
    
    # 轻度抑郁
    for i in range(5):
        agent = PatientAgent(
            depression_level="轻度", 
            questionnaire_type="SDS",
            patient_id=f"sds_mild_{i+1:03d}"
        )
        sds_agents.append(agent)
    
    # 中度抑郁
    for i in range(5):
        agent = PatientAgent(
            depression_level="中度", 
            questionnaire_type="SDS",
            patient_id=f"sds_moderate_{i+1:03d}"
        )
        sds_agents.append(agent)
    
    # 重度抑郁
    for i in range(5):
        agent = PatientAgent(
            depression_level="重度", 
            questionnaire_type="SDS",
            patient_id=f"sds_severe_{i+1:03d}"
        )
        sds_agents.append(agent)
    
    test_agents["SDS"] = sds_agents
    
    return test_agents


def run_comprehensive_stability_test():
    """运行全面的稳定性测试"""
    print("=" * 80)
    print("全面模型稳定性测试系统启动")
    print("=" * 80)
    
    # 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_PROXY_BASE_URL", "https://api.openai.com/v1")
    
    print(f"API密钥: {'已设置' if api_key else '❌ 未设置'}")
    print(f"代理URL: {base_url}")
    
    if not api_key:
        print("\n❌ 请设置环境变量:")
        print("export OPENAI_API_KEY='your-api-key'")
        print("export OPENAI_PROXY_BASE_URL='https://api.zhizengzeng.com/v1'")
        return
    
    # 创建测试器
    tester = MultiModelStabilityTester()
    
    # 定义要测试的模型
    test_models = [
        "gpt-4.1",
        "gpt-4o",
        "deepseek-chat",
        "qwen3-235b-a22b",
        "kimi-latest",
        "llama-4-maverick-17b-128e-instruct",
    ]
    
    print(f"\n预定测试模型: {test_models}")
    
    # 首先测试所有模型的连接性
    try:
        available_models = tester.test_models_connectivity(test_models)
        print(f"\n✅ 模型连接测试完成，可用模型: {available_models}")
    except Exception as e:
        print(f"\n❌ 模型连接测试失败: {e}")
        return
    
    # 创建测试Agent
    all_test_agents = create_comprehensive_test_agents()
    
    # 测试配置
    num_tests_per_model = 5  # 每个模型测试5次
    
    print(f"\n测试配置:")
    print(f"  可用模型数: {len(available_models)}")
    print(f"  PHQ-9 Agent数: {len(all_test_agents['PHQ-9'])}")
    print(f"  SDS Agent数: {len(all_test_agents['SDS'])}")
    print(f"  每个模型测试次数: {num_tests_per_model}")
    
    total_tests = len(available_models) * (len(all_test_agents['PHQ-9']) + len(all_test_agents['SDS'])) * num_tests_per_model
    print(f"  预计总测试数: {total_tests}")
    
    # 询问是否继续
    confirm = input(f"\n是否开始测试? (y/n): ").strip().lower()
    if confirm != 'y':
        print("测试已取消")
        return
    
    # 开始测试
    all_results = []
    
    # 测试PHQ-9
    print(f"\n{'='*80}")
    print("开始PHQ-9量表测试")
    print(f"{'='*80}")
    
    for agent in all_test_agents['PHQ-9']:
        try:
            print(f"\n测试Agent: {agent.patient_id} ({agent.depression_level})")
            agent_results = tester.test_agent_across_models(
                agent, available_models, num_tests_per_model
            )
            all_results.append(agent_results)
            print(f"✅ Agent {agent.patient_id} 测试完成")
            
            # Agent间休息
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Agent {agent.patient_id} 测试失败: {e}")
            continue
    
    # 测试SDS
    print(f"\n{'='*80}")
    print("开始SDS量表测试")
    print(f"{'='*80}")
    
    for agent in all_test_agents['SDS']:
        try:
            print(f"\n测试Agent: {agent.patient_id} ({agent.depression_level})")
            agent_results = tester.test_agent_across_models(
                agent, available_models, num_tests_per_model
            )
            all_results.append(agent_results)
            print(f"✅ Agent {agent.patient_id} 测试完成")
            
            # Agent间休息
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Agent {agent.patient_id} 测试失败: {e}")
            continue
    
    # 生成总体报告
    print(f"\n{'='*80}")
    print("生成总体测试报告")
    print(f"{'='*80}")
    
    overall_report = tester.generate_overall_report(all_results)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    overall_report_file = os.path.join(tester.save_base_dir, f"comprehensive_test_report_{timestamp}.json")
    
    with open(overall_report_file, 'w', encoding='utf-8') as f:
        json.dump(overall_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎯 全面测试报告已保存到: {overall_report_file}")
    print(f"✅ 全面测试完成！共测试了 {len(all_results)} 个Agent")
    
    # 打印简要统计
    successful_tests = len([r for r in all_results if 'comparison_report' in r])
    print(f"📊 测试统计:")
    print(f"  成功测试: {successful_tests}/{len(all_results)}")
    print(f"  测试模型: {len(available_models)}")
    print(f"  总测试轮数: {successful_tests * len(available_models) * num_tests_per_model}")
    
    return all_results


if __name__ == "__main__":
    # 运行全面的稳定性测试
    run_comprehensive_stability_test()
