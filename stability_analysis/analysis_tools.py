# -*- coding: utf-8 -*-
"""
多模型稳定性测试结果分析工具
用于分析不同LLM模型在PHQ-9和SDS量表上的表现
按抑郁程度分类分析，生成详细的比较报告
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import statistics
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class MultiModelAnalyzer:
    """多模型稳定性测试结果分析器"""
    
    def __init__(self, results_dir: str = "stability_analysis/model_comparison_results"):
        """
        初始化分析器
        
        Args:
            results_dir: 测试结果目录路径
        """
        self.results_dir = results_dir
        self.analysis_output_dir = os.path.join(results_dir, "analysis_reports")
        os.makedirs(self.analysis_output_dir, exist_ok=True)
        
        # 创建图表输出目录
        self.plots_dir = os.path.join(self.analysis_output_dir, "plots")
        os.makedirs(self.plots_dir, exist_ok=True)
        
        # 定义抑郁程度和量表类型
        self.depression_levels = ["正常", "轻度", "中度", "重度"]
        self.questionnaire_types = ["phq9", "sds"]
        
        print(f"分析器已初始化")
        print(f"结果目录: {self.results_dir}")
        print(f"分析输出目录: {self.analysis_output_dir}")
    
    def load_all_test_results(self) -> Dict[str, Dict[str, Any]]:
        """
        加载所有测试结果
        
        Returns:
            Dict[str, Dict[str, Any]]: 所有Agent的测试结果
        """
        print(f"\n{'='*60}")
        print(f"开始加载测试结果...")
        print(f"{'='*60}")
        
        all_results = {}
        
        # 遍历所有Agent文件夹
        for folder_name in os.listdir(self.results_dir):
            folder_path = os.path.join(self.results_dir, folder_name)
            
            # 跳过非目录文件
            if not os.path.isdir(folder_path):
                continue
            
            # 跳过分析报告目录
            if folder_name == "analysis_reports":
                continue
            
            print(f"加载: {folder_name}")
            
            # 加载Agent基本信息
            agent_info_path = os.path.join(folder_path, "agent_info.json")
            if not os.path.exists(agent_info_path):
                print(f"  ❌ 缺少agent_info.json")
                continue
            
            try:
                with open(agent_info_path, 'r', encoding='utf-8') as f:
                    agent_info = json.load(f)
            except Exception as e:
                print(f"  ❌ 读取agent_info.json失败: {e}")
                continue
            
            # 初始化Agent结果
            agent_result = {
                'agent_info': agent_info,
                'model_results': {},
                'folder_path': folder_path
            }
            
            # 加载各个模型的测试结果
            for file_name in os.listdir(folder_path):
                if file_name.endswith('_results.json') and file_name != 'agent_info.json':
                    model_name = file_name.replace('_results.json', '').replace('_', '-')
                    model_file_path = os.path.join(folder_path, file_name)
                    
                    try:
                        with open(model_file_path, 'r', encoding='utf-8') as f:
                            model_result = json.load(f)
                        agent_result['model_results'][model_name] = model_result
                        print(f"  ✅ 加载模型结果: {model_name}")
                    except Exception as e:
                        print(f"  ❌ 读取{file_name}失败: {e}")
                        continue
            
            if agent_result['model_results']:
                all_results[folder_name] = agent_result
                print(f"  📊 Agent {folder_name}: {len(agent_result['model_results'])} 个模型结果")
            else:
                print(f"  ❌ Agent {folder_name}: 没有有效的模型结果")
        
        print(f"\n总计加载了 {len(all_results)} 个Agent的测试结果")
        return all_results
    
    def organize_results_by_questionnaire_and_level(self, all_results: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, List[Any]]]:
        """
        按量表类型和抑郁程度组织结果
        
        Args:
            all_results: 所有测试结果
            
        Returns:
            Dict[str, Dict[str, List[Any]]]: 按量表和抑郁程度组织的结果
        """
        organized_results = {}
        
        for questionnaire_type in self.questionnaire_types:
            organized_results[questionnaire_type] = {}
            for level in self.depression_levels:
                organized_results[questionnaire_type][level] = []
        
        for agent_id, agent_data in all_results.items():
            agent_info = agent_data['agent_info']
            questionnaire_type = agent_info.get('questionnaire_type', '').lower().replace('-', '')
            depression_level = agent_info.get('depression_level', '')
            
            if questionnaire_type in self.questionnaire_types and depression_level in self.depression_levels:
                organized_results[questionnaire_type][depression_level].append({
                    'agent_id': agent_id,
                    'agent_info': agent_info,
                    'model_results': agent_data['model_results']
                })
        
        # 打印组织结果统计
        print(f"\n{'='*60}")
        print(f"结果组织统计")
        print(f"{'='*60}")
        
        for questionnaire_type in self.questionnaire_types:
            print(f"\n{questionnaire_type.upper()} 量表:")
            for level in self.depression_levels:
                count = len(organized_results[questionnaire_type][level])
                print(f"  {level}: {count} 个Agent")
        
        return organized_results
    
    def calculate_model_performance_metrics(self, organized_results: Dict[str, Dict[str, List[Any]]]) -> Dict[str, Any]:
        """
        计算各模型的性能指标
        
        Args:
            organized_results: 按量表和抑郁程度组织的结果
            
        Returns:
            Dict[str, Any]: 模型性能指标
        """
        print(f"\n{'='*60}")
        print(f"计算模型性能指标...")
        print(f"{'='*60}")
        
        performance_metrics = {}
        
        for questionnaire_type in self.questionnaire_types:
            performance_metrics[questionnaire_type] = {}
            
            for depression_level in self.depression_levels:
                performance_metrics[questionnaire_type][depression_level] = {}
                agents = organized_results[questionnaire_type][depression_level]
                
                if not agents:
                    print(f"  {questionnaire_type.upper()} - {depression_level}: 无数据")
                    continue
                
                print(f"  {questionnaire_type.upper()} - {depression_level}: {len(agents)} 个Agent")
                
                # 收集所有模型的数据
                all_model_data = {}
                
                for agent in agents:
                    for model_name, model_result in agent['model_results'].items():
                        if 'error' in model_result:
                            continue
                        
                        if model_name not in all_model_data:
                            all_model_data[model_name] = {
                                'stability_scores': [],
                                'mean_scores': [],
                                'std_devs': [],
                                'cvs': [],
                                'percentages_in_range': [],
                                'score_ranges': [],
                                'individual_scores': []
                            }
                        
                        stability = model_result.get('stability_assessment', {})
                        stats = model_result.get('statistics', {})
                        
                        # 收集各种指标
                        all_model_data[model_name]['stability_scores'].append(
                            stability.get('stability_score', 0)
                        )
                        all_model_data[model_name]['mean_scores'].append(
                            stats.get('mean', 0)
                        )
                        all_model_data[model_name]['std_devs'].append(
                            stats.get('std_dev', 0)
                        )
                        all_model_data[model_name]['cvs'].append(
                            stability.get('coefficient_of_variation', 0)
                        )
                        all_model_data[model_name]['percentages_in_range'].append(
                            stability.get('percentage_in_expected_range', 0)
                        )
                        all_model_data[model_name]['score_ranges'].append(
                            stability.get('score_range', 0)
                        )
                        
                        # 收集所有个体分数
                        individual_scores = stats.get('scores', [])
                        all_model_data[model_name]['individual_scores'].extend(individual_scores)
                
                # 计算每个模型的汇总指标
                for model_name, model_data in all_model_data.items():
                    if not model_data['stability_scores']:
                        continue
                    
                    performance_metrics[questionnaire_type][depression_level][model_name] = {
                        # 稳定性指标
                        'avg_stability_score': np.mean(model_data['stability_scores']),
                        'std_stability_score': np.std(model_data['stability_scores']),
                        
                        # 分数指标
                        'avg_mean_score': np.mean(model_data['mean_scores']),
                        'std_mean_score': np.std(model_data['mean_scores']),
                        'overall_mean_score': np.mean(model_data['individual_scores']) if model_data['individual_scores'] else 0,
                        'overall_std_score': np.std(model_data['individual_scores']) if model_data['individual_scores'] else 0,
                        
                        # 变异系数指标
                        'avg_cv': np.mean(model_data['cvs']),
                        'std_cv': np.std(model_data['cvs']),
                        
                        # 准确性指标
                        'avg_percentage_in_range': np.mean(model_data['percentages_in_range']),
                        'std_percentage_in_range': np.std(model_data['percentages_in_range']),
                        
                        # 分数范围指标
                        'avg_score_range': np.mean(model_data['score_ranges']),
                        'std_score_range': np.std(model_data['score_ranges']),
                        
                        # 统计信息
                        'num_agents': len(model_data['stability_scores']),
                        'total_tests': len(model_data['individual_scores']),
                        
                        # 原始数据
                        'raw_data': model_data
                    }
        
        return performance_metrics
    
    def generate_performance_comparison_tables(self, performance_metrics: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """
        生成性能比较表格
        
        Args:
            performance_metrics: 模型性能指标
            
        Returns:
            Dict[str, pd.DataFrame]: 比较表格
        """
        print(f"\n{'='*60}")
        print(f"生成性能比较表格...")
        print(f"{'='*60}")
        
        comparison_tables = {}
        
        for questionnaire_type in self.questionnaire_types:
            print(f"\n生成 {questionnaire_type.upper()} 量表比较表格...")
            
            # 为每个指标创建表格
            metrics_to_compare = [
                ('稳定性分数', 'avg_stability_score'),
                ('准确性（预期范围内%）', 'avg_percentage_in_range'),
                ('变异系数', 'avg_cv'),
                ('平均分数', 'overall_mean_score'),
                ('分数标准差', 'overall_std_score'),
                ('分数范围', 'avg_score_range')
            ]
            
            for metric_name, metric_key in metrics_to_compare:
                table_data = []
                
                for depression_level in self.depression_levels:
                    level_data = performance_metrics[questionnaire_type].get(depression_level, {})
                    
                    for model_name, model_metrics in level_data.items():
                        table_data.append({
                            '抑郁程度': depression_level,
                            '模型': model_name,
                            metric_name: round(model_metrics.get(metric_key, 0), 3),
                            'Agent数量': model_metrics.get('num_agents', 0),
                            '总测试数': model_metrics.get('total_tests', 0)
                        })
                
                if table_data:
                    df = pd.DataFrame(table_data)
                    # 创建透视表
                    pivot_df = df.pivot(index='模型', columns='抑郁程度', values=metric_name)
                    pivot_df = pivot_df.reindex(columns=self.depression_levels)
                    
                    table_key = f"{questionnaire_type}_{metric_key}"
                    comparison_tables[table_key] = pivot_df
                    
                    # 保存表格
                    table_filename = os.path.join(self.analysis_output_dir, f"{table_key}_comparison.csv")
                    pivot_df.to_csv(table_filename, encoding='utf-8-sig')
                    print(f"  ✅ {metric_name} 比较表已保存: {table_key}_comparison.csv")
        
        return comparison_tables
    
    def create_comprehensive_visualizations(self, performance_metrics: Dict[str, Any]):
        """
        创建综合可视化图表
        
        Args:
            performance_metrics: 模型性能指标
        """
        print(f"\n{'='*60}")
        print(f"创建可视化图表...")
        print(f"{'='*60}")
        
        # 为每个量表创建综合分析图
        for questionnaire_type in self.questionnaire_types:
            self._create_questionnaire_comprehensive_plots(questionnaire_type, performance_metrics)
        
        # 创建跨量表比较图
        self._create_cross_questionnaire_comparison(performance_metrics)
        
        print(f"✅ 所有图表已保存到: {self.plots_dir}")
    
    def _create_questionnaire_comprehensive_plots(self, questionnaire_type: str, performance_metrics: Dict[str, Any]):
        """为特定量表创建综合分析图"""
        questionnaire_data = performance_metrics[questionnaire_type]
        
        # 1. 稳定性分数热力图
        self._create_stability_heatmap(questionnaire_type, questionnaire_data)
        
        # 2. 准确性条形图
        self._create_accuracy_barplot(questionnaire_type, questionnaire_data)
        
        # 3. 变异系数箱线图
        self._create_cv_boxplot(questionnaire_type, questionnaire_data)
        
        # 4. 模型综合排名雷达图
        self._create_model_radar_chart(questionnaire_type, questionnaire_data)
        
        # 5. 分数分布小提琴图
        self._create_score_distribution_violin(questionnaire_type, questionnaire_data)
    
    def _create_stability_heatmap(self, questionnaire_type: str, questionnaire_data: Dict[str, Any]):
        """创建稳定性分数热力图"""
        # 准备数据
        stability_data = []
        models = set()
        
        for depression_level in self.depression_levels:
            level_data = questionnaire_data.get(depression_level, {})
            for model_name, metrics in level_data.items():
                stability_data.append({
                    '抑郁程度': depression_level,
                    '模型': model_name,
                    '稳定性分数': metrics.get('avg_stability_score', 0)
                })
                models.add(model_name)
        
        if not stability_data:
            return
        
        df = pd.DataFrame(stability_data)
        pivot_df = df.pivot(index='模型', columns='抑郁程度', values='稳定性分数')
        pivot_df = pivot_df.reindex(columns=self.depression_levels)
        
        # 创建热力图
        plt.figure(figsize=(10, 6))
        sns.heatmap(pivot_df, annot=True, cmap='RdYlGn', center=2.5, 
                   fmt='.2f', cbar_kws={'label': '稳定性分数'})
        plt.title(f'{questionnaire_type.upper()} 量表 - 各模型稳定性分数热力图', fontsize=14, fontweight='bold')
        plt.xlabel('抑郁程度', fontsize=12)
        plt.ylabel('模型', fontsize=12)
        plt.tight_layout()
        
        filename = os.path.join(self.plots_dir, f'{questionnaire_type}_stability_heatmap.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✅ 稳定性热力图: {filename}")
    
    def _create_accuracy_barplot(self, questionnaire_type: str, questionnaire_data: Dict[str, Any]):
        """创建准确性条形图"""
        # 准备数据
        accuracy_data = []
        
        for depression_level in self.depression_levels:
            level_data = questionnaire_data.get(depression_level, {})
            for model_name, metrics in level_data.items():
                accuracy_data.append({
                    '抑郁程度': depression_level,
                    '模型': model_name,
                    '准确性': metrics.get('avg_percentage_in_range', 0)
                })
        
        if not accuracy_data:
            return
        
        df = pd.DataFrame(accuracy_data)
        
        # 创建分组条形图
        plt.figure(figsize=(12, 6))
        sns.barplot(data=df, x='抑郁程度', y='准确性', hue='模型', palette='Set2')
        plt.title(f'{questionnaire_type.upper()} 量表 - 各模型预期范围内准确性', fontsize=14, fontweight='bold')
        plt.xlabel('抑郁程度', fontsize=12)
        plt.ylabel('准确性 (%)', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        filename = os.path.join(self.plots_dir, f'{questionnaire_type}_accuracy_barplot.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✅ 准确性条形图: {filename}")
    
    def _create_cv_boxplot(self, questionnaire_type: str, questionnaire_data: Dict[str, Any]):
        """创建变异系数箱线图"""
        # 准备数据
        cv_data = []
        
        for depression_level in self.depression_levels:
            level_data = questionnaire_data.get(depression_level, {})
            for model_name, metrics in level_data.items():
                # 获取原始变异系数数据
                raw_cvs = metrics.get('raw_data', {}).get('cvs', [])
                for cv in raw_cvs:
                    cv_data.append({
                        '抑郁程度': depression_level,
                        '模型': model_name,
                        '变异系数': cv
                    })
        
        if not cv_data:
            return
        
        df = pd.DataFrame(cv_data)
        
        # 创建箱线图
        plt.figure(figsize=(12, 8))
        sns.boxplot(data=df, x='抑郁程度', y='变异系数', hue='模型', palette='Set3')
        plt.title(f'{questionnaire_type.upper()} 量表 - 各模型变异系数分布', fontsize=14, fontweight='bold')
        plt.xlabel('抑郁程度', fontsize=12)
        plt.ylabel('变异系数 (%)', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        filename = os.path.join(self.plots_dir, f'{questionnaire_type}_cv_boxplot.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✅ 变异系数箱线图: {filename}")
    
    def _create_model_radar_chart(self, questionnaire_type: str, questionnaire_data: Dict[str, Any]):
        """创建模型综合性能雷达图"""
        try:
            # 收集所有模型在各个抑郁程度下的平均表现
            model_overall_performance = {}
            
            # 获取所有模型名称
            all_models = set()
            for level_data in questionnaire_data.values():
                all_models.update(level_data.keys())
            
            for model_name in all_models:
                metrics_list = {
                    'stability_scores': [],
                    'accuracy_scores': [],
                    'cv_scores': []  # 变异系数越小越好，所以要转换
                }
                
                for depression_level in self.depression_levels:
                    level_data = questionnaire_data.get(depression_level, {})
                    if model_name in level_data:
                        metrics = level_data[model_name]
                        metrics_list['stability_scores'].append(metrics.get('avg_stability_score', 0))
                        metrics_list['accuracy_scores'].append(metrics.get('avg_percentage_in_range', 0))
                        # 变异系数转换：100 - cv，使得越小的cv值对应越高的分数
                        cv = metrics.get('avg_cv', 100)
                        metrics_list['cv_scores'].append(max(0, 100 - cv))
                
                # 计算总体平均值
                if any(metrics_list.values()):
                    model_overall_performance[model_name] = {
                        '稳定性': np.mean(metrics_list['stability_scores']) if metrics_list['stability_scores'] else 0,
                        '准确性': np.mean(metrics_list['accuracy_scores']) if metrics_list['accuracy_scores'] else 0,
                        '一致性': np.mean(metrics_list['cv_scores']) if metrics_list['cv_scores'] else 0
                    }
            
            if not model_overall_performance:
                return
            
            # 创建雷达图
            metrics = ['稳定性', '准确性', '一致性']
            num_metrics = len(metrics)
            
            # 计算角度
            angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
            angles += angles[:1]  # 闭合图形
            
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(model_overall_performance)))
            
            for i, (model_name, performance) in enumerate(model_overall_performance.items()):
                values = [performance[metric] for metric in metrics]
                values += values[:1]  # 闭合图形
                
                ax.plot(angles, values, 'o-', linewidth=2, label=model_name, color=colors[i])
                ax.fill(angles, values, alpha=0.25, color=colors[i])
            
            # 设置标签
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics)
            ax.set_ylim(0, 100)
            
            # 添加网格线
            ax.grid(True)
            
            plt.title(f'{questionnaire_type.upper()} 量表 - 模型综合性能雷达图', 
                     fontsize=14, fontweight='bold', pad=20)
            plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
            
            filename = os.path.join(self.plots_dir, f'{questionnaire_type}_model_radar.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  ✅ 雷达图: {filename}")
            
        except Exception as e:
            print(f"  ❌ 创建雷达图失败: {e}")
    
    def _create_score_distribution_violin(self, questionnaire_type: str, questionnaire_data: Dict[str, Any]):
        """创建分数分布小提琴图"""
        # 准备数据
        score_data = []
        
        for depression_level in self.depression_levels:
            level_data = questionnaire_data.get(depression_level, {})
            for model_name, metrics in level_data.items():
                individual_scores = metrics.get('raw_data', {}).get('individual_scores', [])
                for score in individual_scores:
                    score_data.append({
                        '抑郁程度': depression_level,
                        '模型': model_name,
                        '分数': score
                    })
        
        if not score_data:
            return
        
        df = pd.DataFrame(score_data)
        
        # 为每个抑郁程度创建子图
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        for i, depression_level in enumerate(self.depression_levels):
            level_df = df[df['抑郁程度'] == depression_level]
            if not level_df.empty:
                sns.violinplot(data=level_df, x='模型', y='分数', ax=axes[i], palette='Set2')
                axes[i].set_title(f'{depression_level}抑郁程度', fontsize=12, fontweight='bold')
                axes[i].tick_params(axis='x', rotation=45)
        
        plt.suptitle(f'{questionnaire_type.upper()} 量表 - 各模型分数分布', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        filename = os.path.join(self.plots_dir, f'{questionnaire_type}_score_distribution.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✅ 分数分布图: {filename}")
    
    def _create_cross_questionnaire_comparison(self, performance_metrics: Dict[str, Any]):
        """创建跨量表比较图"""
        print(f"\n创建跨量表比较图...")
        
        # 1. 稳定性分数比较
        self._create_cross_questionnaire_stability_comparison(performance_metrics)
        
        # 2. 准确性比较
        self._create_cross_questionnaire_accuracy_comparison(performance_metrics)
    
    def _create_cross_questionnaire_stability_comparison(self, performance_metrics: Dict[str, Any]):
        """创建跨量表稳定性比较图"""
        # 准备数据
        comparison_data = []
        
        for questionnaire_type in self.questionnaire_types:
            questionnaire_data = performance_metrics[questionnaire_type]
            
            for depression_level in self.depression_levels:
                level_data = questionnaire_data.get(depression_level, {})
                for model_name, metrics in level_data.items():
                    comparison_data.append({
                        '量表类型': questionnaire_type.upper(),
                        '抑郁程度': depression_level,
                        '模型': model_name,
                        '稳定性分数': metrics.get('avg_stability_score', 0)
                    })
        
        if not comparison_data:
            return
        
        df = pd.DataFrame(comparison_data)
        
        # 创建分面图
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, depression_level in enumerate(self.depression_levels):
            level_df = df[df['抑郁程度'] == depression_level]
            if not level_df.empty:
                sns.barplot(data=level_df, x='模型', y='稳定性分数', hue='量表类型', ax=axes[i], palette='Set1')
                axes[i].set_title(f'{depression_level}抑郁程度', fontsize=12, fontweight='bold')
                axes[i].tick_params(axis='x', rotation=45)
                axes[i].legend(title='量表类型')
        
        plt.suptitle('PHQ-9 vs SDS 量表 - 各模型稳定性分数比较', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        filename = os.path.join(self.plots_dir, 'cross_questionnaire_stability_comparison.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✅ 跨量表稳定性比较图: {filename}")
    
    def _create_cross_questionnaire_accuracy_comparison(self, performance_metrics: Dict[str, Any]):
        """创建跨量表准确性比较图"""
        # 准备数据
        comparison_data = []
        
        for questionnaire_type in self.questionnaire_types:
            questionnaire_data = performance_metrics[questionnaire_type]
            
            for depression_level in self.depression_levels:
                level_data = questionnaire_data.get(depression_level, {})
                for model_name, metrics in level_data.items():
                    comparison_data.append({
                        '量表类型': questionnaire_type.upper(),
                        '抑郁程度': depression_level,
                        '模型': model_name,
                        '准确性': metrics.get('avg_percentage_in_range', 0)
                    })
        
        if not comparison_data:
            return
        
        df = pd.DataFrame(comparison_data)
        
        # 创建分面图
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, depression_level in enumerate(self.depression_levels):
            level_df = df[df['抑郁程度'] == depression_level]
            if not level_df.empty:
                sns.barplot(data=level_df, x='模型', y='准确性', hue='量表类型', ax=axes[i], palette='Set2')
                axes[i].set_title(f'{depression_level}抑郁程度', fontsize=12, fontweight='bold')
                axes[i].tick_params(axis='x', rotation=45)
                axes[i].legend(title='量表类型')
                axes[i].set_ylabel('准确性 (%)')
        
        plt.suptitle('PHQ-9 vs SDS 量表 - 各模型准确性比较', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        filename = os.path.join(self.plots_dir, 'cross_questionnaire_accuracy_comparison.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✅ 跨量表准确性比较图: {filename}")
    
    def generate_comprehensive_report(self, performance_metrics: Dict[str, Any], comparison_tables: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        生成综合分析报告
        
        Args:
            performance_metrics: 模型性能指标
            comparison_tables: 比较表格
            
        Returns:
            Dict[str, Any]: 综合报告
        """
        print(f"\n{'='*60}")
        print(f"生成综合分析报告...")
        print(f"{'='*60}")
        
        report = {
            'report_info': {
                'generation_time': datetime.now().isoformat(),
                'analysis_scope': {
                    'questionnaire_types': self.questionnaire_types,
                    'depression_levels': self.depression_levels
                }
            },
            'executive_summary': {},
            'detailed_analysis': {},
            'model_rankings': {},
            'recommendations': {}
        }
        
        # 1. 生成执行摘要
        report['executive_summary'] = self._generate_executive_summary(performance_metrics)
        
        # 2. 生成详细分析
        report['detailed_analysis'] = self._generate_detailed_analysis(performance_metrics)
        
        # 3. 生成模型排名
        report['model_rankings'] = self._generate_model_rankings(performance_metrics)
        
        # 4. 生成建议
        report['recommendations'] = self._generate_recommendations(performance_metrics)
        
        # 保存报告
        report_filename = os.path.join(self.analysis_output_dir, f"comprehensive_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 综合报告已保存: {report_filename}")
        
        # 生成Markdown格式报告
        self._generate_markdown_report(report)
        
        return report
    
    def _generate_executive_summary(self, performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行摘要"""
        summary = {
            'total_models_analyzed': set(),
            'questionnaire_analysis': {},
            'key_findings': []
        }
        
        for questionnaire_type in self.questionnaire_types:
            questionnaire_data = performance_metrics[questionnaire_type]
            
            # 收集模型信息
            models_in_questionnaire = set()
            total_agents = 0
            total_tests = 0
            
            level_summary = {}
            
            for depression_level in self.depression_levels:
                level_data = questionnaire_data.get(depression_level, {})
                level_models = list(level_data.keys())
                models_in_questionnaire.update(level_models)
                
                if level_data:
                    # 计算该抑郁程度下的平均指标
                    avg_stability = np.mean([m.get('avg_stability_score', 0) for m in level_data.values()])
                    avg_accuracy = np.mean([m.get('avg_percentage_in_range', 0) for m in level_data.values()])
                    avg_cv = np.mean([m.get('avg_cv', 0) for m in level_data.values()])
                    
                    level_summary[depression_level] = {
                        'models_count': len(level_models),
                        'avg_stability_score': avg_stability,
                        'avg_accuracy': avg_accuracy,
                        'avg_cv': avg_cv,
                        'agents_count': sum(m.get('num_agents', 0) for m in level_data.values()) // len(level_data) if level_data else 0,
                        'total_tests': sum(m.get('total_tests', 0) for m in level_data.values())
                    }
                    
                    total_agents += level_summary[depression_level]['agents_count']
                    total_tests += level_summary[depression_level]['total_tests']
            
            summary['total_models_analyzed'].update(models_in_questionnaire)
            summary['questionnaire_analysis'][questionnaire_type] = {
                'models_tested': list(models_in_questionnaire),
                'models_count': len(models_in_questionnaire),
                'total_agents': total_agents,
                'total_tests': total_tests,
                'level_summary': level_summary
            }
        
        summary['total_models_analyzed'] = list(summary['total_models_analyzed'])
        
        # 生成关键发现
        summary['key_findings'] = self._extract_key_findings(performance_metrics)
        
        return summary
    
    def _extract_key_findings(self, performance_metrics: Dict[str, Any]) -> List[str]:
        """提取关键发现"""
        findings = []
        
        try:
            # 找出整体表现最好的模型
            all_model_scores = {}
            
            for questionnaire_type in self.questionnaire_types:
                questionnaire_data = performance_metrics[questionnaire_type]
                for depression_level in self.depression_levels:
                    level_data = questionnaire_data.get(depression_level, {})
                    for model_name, metrics in level_data.items():
                        if model_name not in all_model_scores:
                            all_model_scores[model_name] = []
                        all_model_scores[model_name].append(metrics.get('avg_stability_score', 0))
            
            # 计算每个模型的平均表现
            model_avg_scores = {model: np.mean(scores) for model, scores in all_model_scores.items()}
            best_model = max(model_avg_scores.items(), key=lambda x: x[1])
            worst_model = min(model_avg_scores.items(), key=lambda x: x[1])
            
            findings.append(f"整体表现最佳模型: {best_model[0]} (平均稳定性分数: {best_model[1]:.2f})")
            findings.append(f"整体表现最差模型: {worst_model[0]} (平均稳定性分数: {worst_model[1]:.2f})")
            
            # 分析量表差异
            phq9_scores = []
            sds_scores = []
            
            for model in all_model_scores:
                for questionnaire_type in self.questionnaire_types:
                    questionnaire_data = performance_metrics[questionnaire_type]
                    model_scores = []
                    for level_data in questionnaire_data.values():
                        if model in level_data:
                            model_scores.append(level_data[model].get('avg_stability_score', 0))
                    
                    if model_scores:
                        if questionnaire_type == 'phq9':
                            phq9_scores.extend(model_scores)
                        else:
                            sds_scores.extend(model_scores)
            
            if phq9_scores and sds_scores:
                avg_phq9 = np.mean(phq9_scores)
                avg_sds = np.mean(sds_scores)
                
                if avg_phq9 > avg_sds:
                    findings.append(f"PHQ-9量表整体稳定性更好 (PHQ-9: {avg_phq9:.2f} vs SDS: {avg_sds:.2f})")
                elif avg_sds > avg_phq9:
                    findings.append(f"SDS量表整体稳定性更好 (SDS: {avg_sds:.2f} vs PHQ-9: {avg_phq9:.2f})")
                else:
                    findings.append(f"PHQ-9和SDS量表稳定性相当 (PHQ-9: {avg_phq9:.2f}, SDS: {avg_sds:.2f})")
            
        except Exception as e:
            findings.append(f"关键发现提取时发生错误: {str(e)}")
        
        return findings
    
    def _generate_detailed_analysis(self, performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """生成详细分析"""
        detailed_analysis = {}
        
        for questionnaire_type in self.questionnaire_types:
            questionnaire_data = performance_metrics[questionnaire_type]
            detailed_analysis[questionnaire_type] = {}
            
            for depression_level in self.depression_levels:
                level_data = questionnaire_data.get(depression_level, {})
                if not level_data:
                    continue
                
                # 分析该抑郁程度下各模型的表现
                level_analysis = {
                    'model_count': len(level_data),
                    'model_performance': {},
                    'level_statistics': {
                        'stability_scores': [m.get('avg_stability_score', 0) for m in level_data.values()],
                        'accuracy_scores': [m.get('avg_percentage_in_range', 0) for m in level_data.values()],
                        'cv_scores': [m.get('avg_cv', 0) for m in level_data.values()]
                    }
                }
                
                # 计算该级别的统计信息
                level_analysis['level_statistics']['avg_stability'] = np.mean(level_analysis['level_statistics']['stability_scores'])
                level_analysis['level_statistics']['avg_accuracy'] = np.mean(level_analysis['level_statistics']['accuracy_scores'])
                level_analysis['level_statistics']['avg_cv'] = np.mean(level_analysis['level_statistics']['cv_scores'])
                
                # 找出该级别的最佳和最差模型
                best_model = max(level_data.items(), key=lambda x: x[1].get('avg_stability_score', 0))
                worst_model = min(level_data.items(), key=lambda x: x[1].get('avg_stability_score', 0))
                
                level_analysis['best_model'] = {
                    'name': best_model[0],
                    'stability_score': best_model[1].get('avg_stability_score', 0),
                    'accuracy': best_model[1].get('avg_percentage_in_range', 0)
                }
                
                level_analysis['worst_model'] = {
                    'name': worst_model[0],
                    'stability_score': worst_model[1].get('avg_stability_score', 0),
                    'accuracy': worst_model[1].get('avg_percentage_in_range', 0)
                }
                
                detailed_analysis[questionnaire_type][depression_level] = level_analysis
        
        return detailed_analysis
    
    def _generate_model_rankings(self, performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """生成模型排名"""
        rankings = {}
        
        for questionnaire_type in self.questionnaire_types:
            questionnaire_data = performance_metrics[questionnaire_type]
            rankings[questionnaire_type] = {}
            
            for depression_level in self.depression_levels:
                level_data = questionnaire_data.get(depression_level, {})
                if not level_data:
                    continue
                
                # 按稳定性分数排序
                sorted_by_stability = sorted(level_data.items(), 
                                           key=lambda x: x[1].get('avg_stability_score', 0), 
                                           reverse=True)
                
                # 按准确性排序
                sorted_by_accuracy = sorted(level_data.items(), 
                                          key=lambda x: x[1].get('avg_percentage_in_range', 0), 
                                          reverse=True)
                
                # 按变异系数排序（越小越好）
                sorted_by_cv = sorted(level_data.items(), 
                                    key=lambda x: x[1].get('avg_cv', 100))
                
                rankings[questionnaire_type][depression_level] = {
                    'by_stability': [(name, metrics.get('avg_stability_score', 0)) for name, metrics in sorted_by_stability],
                    'by_accuracy': [(name, metrics.get('avg_percentage_in_range', 0)) for name, metrics in sorted_by_accuracy],
                    'by_consistency': [(name, metrics.get('avg_cv', 100)) for name, metrics in sorted_by_cv]
                }
        
        return rankings
    
    def _generate_recommendations(self, performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """生成建议"""
        recommendations = {
            'model_selection': {},
            'improvement_areas': {},
            'general_insights': []
        }
        
        # 为每个场景推荐最适合的模型
        for questionnaire_type in self.questionnaire_types:
            questionnaire_data = performance_metrics[questionnaire_type]
            recommendations['model_selection'][questionnaire_type] = {}
            
            for depression_level in self.depression_levels:
                level_data = questionnaire_data.get(depression_level, {})
                if not level_data:
                    continue
                
                # 找出该场景下的最佳模型
                best_overall = max(level_data.items(), 
                                 key=lambda x: (x[1].get('avg_stability_score', 0) + 
                                              x[1].get('avg_percentage_in_range', 0) / 100))
                
                recommendations['model_selection'][questionnaire_type][depression_level] = {
                    'recommended_model': best_overall[0],
                    'reasons': [
                        f"稳定性分数: {best_overall[1].get('avg_stability_score', 0):.2f}",
                        f"准确性: {best_overall[1].get('avg_percentage_in_range', 0):.1f}%",
                        f"变异系数: {best_overall[1].get('avg_cv', 0):.1f}%"
                    ]
                }
        
        # 识别改进领域
        all_models = set()
        for questionnaire_data in performance_metrics.values():
            for level_data in questionnaire_data.values():
                all_models.update(level_data.keys())
        
        for model in all_models:
            model_issues = []
            model_strengths = []
            
            stability_scores = []
            accuracy_scores = []
            
            for questionnaire_data in performance_metrics.values():
                for level_data in questionnaire_data.values():
                    if model in level_data:
                        stability_scores.append(level_data[model].get('avg_stability_score', 0))
                        accuracy_scores.append(level_data[model].get('avg_percentage_in_range', 0))
            
            if stability_scores:
                avg_stability = np.mean(stability_scores)
                avg_accuracy = np.mean(accuracy_scores)
                
                if avg_stability < 2.0:
                    model_issues.append("稳定性较低")
                elif avg_stability > 4.0:
                    model_strengths.append("稳定性优秀")
                
                if avg_accuracy < 50:
                    model_issues.append("准确性不足")
                elif avg_accuracy > 80:
                    model_strengths.append("准确性优秀")
                
                recommendations['improvement_areas'][model] = {
                    'issues': model_issues,
                    'strengths': model_strengths,
                    'avg_stability': avg_stability,
                    'avg_accuracy': avg_accuracy
                }
        
        # 一般性洞察
        recommendations['general_insights'] = [
            "建议在实际部署前进行充分的稳定性测试",
            "不同抑郁程度下模型表现可能存在显著差异",
            "量表类型对模型表现也有重要影响",
            "建议结合多个指标（稳定性、准确性、一致性）进行模型选择"
        ]
        
        return recommendations
    
    def _generate_markdown_report(self, report: Dict[str, Any]):
        """生成Markdown格式的报告"""
        markdown_content = []
        
        # 标题
        markdown_content.append("# 多模型稳定性测试分析报告\n")
        markdown_content.append(f"**生成时间**: {report['report_info']['generation_time']}\n")
        
        # 执行摘要
        markdown_content.append("## 执行摘要\n")
        summary = report['executive_summary']
        
        markdown_content.append(f"**分析的模型总数**: {len(summary['total_models_analyzed'])}\n")
        markdown_content.append(f"**模型列表**: {', '.join(summary['total_models_analyzed'])}\n")
        
        for questionnaire_type, analysis in summary['questionnaire_analysis'].items():
            markdown_content.append(f"\n### {questionnaire_type.upper()} 量表分析\n")
            markdown_content.append(f"- 测试模型数: {analysis['models_count']}\n")
            markdown_content.append(f"- 测试Agent总数: {analysis['total_agents']}\n")
            markdown_content.append(f"- 总测试次数: {analysis['total_tests']}\n")
        
        # 关键发现
        markdown_content.append("\n### 关键发现\n")
        for finding in summary['key_findings']:
            markdown_content.append(f"- {finding}\n")
        
        # 模型排名
        markdown_content.append("\n## 模型排名\n")
        rankings = report['model_rankings']
        
        for questionnaire_type in self.questionnaire_types:
            if questionnaire_type in rankings:
                markdown_content.append(f"\n### {questionnaire_type.upper()} 量表排名\n")
                
                for depression_level in self.depression_levels:
                    if depression_level in rankings[questionnaire_type]:
                        level_rankings = rankings[questionnaire_type][depression_level]
                        markdown_content.append(f"\n#### {depression_level}抑郁程度\n")
                        
                        # 稳定性排名
                        markdown_content.append("**按稳定性分数排名:**\n")
                        for i, (model, score) in enumerate(level_rankings['by_stability'][:5], 1):
                            markdown_content.append(f"{i}. {model}: {score:.2f}\n")
                        
                        # 准确性排名
                        markdown_content.append("\n**按准确性排名:**\n")
                        for i, (model, accuracy) in enumerate(level_rankings['by_accuracy'][:5], 1):
                            markdown_content.append(f"{i}. {model}: {accuracy:.1f}%\n")
        
        # 建议
        markdown_content.append("\n## 建议\n")
        recommendations = report['recommendations']
        
        # 模型选择建议
        markdown_content.append("### 模型选择建议\n")
        for questionnaire_type in self.questionnaire_types:
            if questionnaire_type in recommendations['model_selection']:
                markdown_content.append(f"\n#### {questionnaire_type.upper()} 量表\n")
                
                for depression_level in self.depression_levels:
                    if depression_level in recommendations['model_selection'][questionnaire_type]:
                        rec = recommendations['model_selection'][questionnaire_type][depression_level]
                        markdown_content.append(f"\n**{depression_level}抑郁程度**: {rec['recommended_model']}\n")
                        for reason in rec['reasons']:
                            markdown_content.append(f"- {reason}\n")
        
        # 一般性洞察
        markdown_content.append("\n### 一般性洞察\n")
        for insight in recommendations['general_insights']:
            markdown_content.append(f"- {insight}\n")
        
        # 保存Markdown报告
        markdown_filename = os.path.join(self.analysis_output_dir, f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(markdown_filename, 'w', encoding='utf-8') as f:
            f.write(''.join(markdown_content))
        
        print(f"✅ Markdown报告已保存: {markdown_filename}")
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """
        运行完整的分析流程
        
        Returns:
            Dict[str, Any]: 完整的分析结果
        """
        print(f"{'='*80}")
        print(f"开始多模型稳定性测试结果分析")
        print(f"{'='*80}")
        
        # 1. 加载所有测试结果
        all_results = self.load_all_test_results()
        
        if not all_results:
            print("❌ 没有找到测试结果，分析终止")
            return {}
        
        # 2. 按量表类型和抑郁程度组织结果
        organized_results = self.organize_results_by_questionnaire_and_level(all_results)
        
        # 3. 计算模型性能指标
        performance_metrics = self.calculate_model_performance_metrics(organized_results)
        
        # 4. 生成比较表格
        comparison_tables = self.generate_performance_comparison_tables(performance_metrics)
        
        # 5. 创建可视化图表
        self.create_comprehensive_visualizations(performance_metrics)
        
        # 6. 生成综合报告
        comprehensive_report = self.generate_comprehensive_report(performance_metrics, comparison_tables)
        
        print(f"\n{'='*80}")
        print(f"分析完成！")
        print(f"{'='*80}")
        print(f"📊 分析结果保存在: {self.analysis_output_dir}")
        print(f"📈 图表保存在: {self.plots_dir}")
        print(f"📋 表格和报告保存在: {self.analysis_output_dir}")
        
        return {
            'performance_metrics': performance_metrics,
            'comparison_tables': comparison_tables,
            'comprehensive_report': comprehensive_report,
            'analysis_output_dir': self.analysis_output_dir,
            'plots_dir': self.plots_dir
        }


def main():
    """主函数"""
    print("多模型稳定性测试结果分析工具")
    print("=" * 60)
    
    # 检查结果目录
    results_dir = "stability_analysis/model_comparison_results"
    if not os.path.exists(results_dir):
        print(f"❌ 结果目录不存在: {results_dir}")
        print("请确保已经运行了多模型稳定性测试")
        return
    
    # 创建分析器并运行分析
    analyzer = MultiModelAnalyzer(results_dir)
    
    try:
        analysis_results = analyzer.run_complete_analysis()
        
        if analysis_results:
            print("\n✅ 分析成功完成！")
            print(f"结果保存在: {analysis_results['analysis_output_dir']}")
        else:
            print("\n❌ 分析失败")
            
    except Exception as e:
        print(f"\n❌ 分析过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()