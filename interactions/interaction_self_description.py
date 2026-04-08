#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自我描述生成交互函数
提供简单易用的接口来生成病人的自我状态阐述
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, Union
from core.agent_base import PatientAgent
from utils import MultiLLMClient, TextGenerator
from utils.config import get_available_models


def generate_self_description(
    patient: Optional[PatientAgent] = None,
    model: str = "gpt-3.5-turbo",
    api_key: Optional[str] = None,
    scenario: Optional[str] = None,
    style: Optional[str] = None,
    time_perspective: Optional[str] = None,
    save_to_file: bool = True,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成病人的自我状态阐述
    
    Args:
        patient: 病人Agent对象。如果为None，将创建一个随机病人
        model: 要使用的LLM模型名称
        api_key: API密钥。如果为None，将从环境变量中获取
        scenario: 指定场景类型（如"人际关系"、"身体健康"等）
        style: 指定表达风格（如"叙述型"、"对话型"等）
        time_perspective: 指定时间维度（如"当下状态"、"过去回顾"等）
        save_to_file: 是否保存结果到文件
        output_dir: 输出目录。如果为None，使用默认的logs目录
        
    Returns:
        dict: 包含生成结果的字典
            - success: bool, 是否成功
            - content: str, 生成的内容（如果成功）
            - metadata: dict, 生成的元数据（如果成功）
            - patient_info: dict, 病人信息
            - file_path: str, 保存的文件路径（如果save_to_file=True）
            - error: str, 错误信息（如果失败）
    
    Example:
        >>> # 使用随机病人生成自述
        >>> result = generate_self_description()
        
        >>> # 使用指定病人和参数
        >>> patient = PatientAgent(depression_level="轻度", age=25)
        >>> result = generate_self_description(
        ...     patient=patient,
        ...     model="gpt-4",
        ...     scenario="人际关系",
        ...     style="内心独白"
        ... )
    """
    try:
        # 1. 处理病人对象
        if patient is None:
            patient = PatientAgent()
            
        # 2. 处理API密钥
        if api_key is None:
            # 根据模型类型获取对应的环境变量
            if "gpt" in model.lower() or "openai" in model.lower():
                api_key = os.getenv("OPENAI_API_KEY")
            elif "deepseek" in model.lower():
                api_key = os.getenv("DEEPSEEK_API_KEY")
            elif "gemini" in model.lower():
                api_key = os.getenv("GEMINI_API_KEY")
            else:
                api_key = os.getenv("OPENAI_API_KEY")  # 默认
                
        if not api_key:
            return {
                "success": False,
                "error": f"未找到模型 {model} 对应的API密钥，请设置相应的环境变量"
            }
        
        # 3. 初始化LLM客户端
        llm_client = MultiLLMClient(model=model, api_key=api_key)
        
        # 4. 创建文本生成器
        text_generator = TextGenerator(patient, llm_client)
        
        # 5. 生成自述
        result = text_generator.generate_and_save_self_description(
            scenario=scenario,
            style=style,
            time_perspective=time_perspective
        )
        
        if not result["success"]:
            return {
                "success": False,
                "error": result.get("error", "生成失败"),
                "patient_info": _get_patient_summary(patient)
            }
        
        # 6. 准备返回结果
        data = result["data"]
        return_result = {
            "success": True,
            "content": data["generated_content"],
            "metadata": data["generation_metadata"],
            "patient_info": _get_patient_summary(patient),
            "generation_params": {
                "scenario": scenario,
                "style": style,
                "time_perspective": time_perspective,
                "model": model
            }
        }
        
        # 7. 保存到文件（如果需要）
        if save_to_file:
            file_path = _save_result_to_file(
                data=data,
                patient=patient,
                content_type="self_description",
                output_dir=output_dir
            )
            return_result["file_path"] = file_path
            
        return return_result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"生成过程中发生错误: {str(e)}",
            "error_type": type(e).__name__,
            "patient_info": _get_patient_summary(patient) if patient else None
        }


def quick_self_description(
    depression_level: str = "正常",
    age: int = 25,
    gender: str = "女",
    model: str = "gpt-3.5-turbo"
) -> Dict[str, Any]:
    """
    快速生成自我状态阐述（简化版接口）
    
    Args:
        depression_level: 抑郁等级（"正常", "轻度", "中度", "重度"）
        age: 年龄
        gender: 性别（"男", "女"）
        model: LLM模型名称
        
    Returns:
        dict: 生成结果
        
    Example:
        >>> result = quick_self_description(depression_level="轻度", age=30, gender="男")
        >>> print(result["content"])
    """
    # 根据抑郁等级设置合适的评分
    score_mapping = {
        "正常": 2,
        "轻度": 8,
        "中度": 15,
        "重度": 22
    }
    
    patient = PatientAgent(
        depression_level=depression_level,
        age=age,
        gender=gender,
        questionnaire_score=score_mapping.get(depression_level, 2)
    )
    
    return generate_self_description(patient=patient, model=model)


def generate_multiple_self_descriptions(
    patient: PatientAgent,
    model: str = "gpt-3.5-turbo",
    api_key: Optional[str] = None,
    count: int = 3,
    vary_params: bool = True,
    save_to_file: bool = True,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    为同一个病人生成多个自我状态阐述
    
    Args:
        patient: 病人Agent对象
        model: LLM模型名称
        api_key: API密钥
        count: 生成数量
        vary_params: 是否变换生成参数（场景、风格、时间维度）
        save_to_file: 是否保存到文件
        output_dir: 输出目录
        
    Returns:
        dict: 包含多个生成结果的字典
    """
    results = []
    errors = []
    
    for i in range(count):
        # 如果需要变换参数，随机选择不同的参数组合
        scenario = None
        style = None
        time_perspective = None
        
        if vary_params:
            scenarios = ["人际关系", "身体健康", "工作学习", "情感体验", "日常生活"]
            styles = ["叙述型", "对话型", "内心独白", "故事型"]
            times = ["当下状态", "过去回顾", "未来展望"]
            
            import random
            scenario = random.choice(scenarios)
            style = random.choice(styles)
            time_perspective = random.choice(times)
        
        result = generate_self_description(
            patient=patient,
            model=model,
            api_key=api_key,
            scenario=scenario,
            style=style,
            time_perspective=time_perspective,
            save_to_file=save_to_file,
            output_dir=output_dir
        )
        
        if result["success"]:
            results.append(result)
        else:
            errors.append(f"第{i+1}次生成失败: {result['error']}")
    
    return {
        "success": len(results) > 0,
        "total_requested": count,
        "successful_count": len(results),
        "failed_count": len(errors),
        "results": results,
        "errors": errors,
        "patient_info": _get_patient_summary(patient)
    }


def _get_patient_summary(patient: PatientAgent) -> Dict[str, Any]:
    """获取病人的简要信息"""
    return {
        "patient_id": getattr(patient, 'patient_id', "unknown"),
        "age": patient.age,
        "gender": patient.gender,
        "depression_level": patient.depression_level,
        "score": patient.score,
        "education": patient.education,
        "occupation": patient.occupation
    }


def _save_result_to_file(
    data: Dict[str, Any],
    patient: PatientAgent,
    content_type: str,
    output_dir: Optional[str] = None
) -> str:
    """保存结果到文件"""
    # 确定输出目录
    if output_dir is None:
        patient_id = getattr(patient, 'patient_id', f"patient_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        output_dir = f"logs/{patient_id}"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"{content_type}_{timestamp}.json")
    
    # 准备保存数据
    save_data = {
        "timestamp": datetime.now().isoformat(),
        "content_type": content_type,
        "patient_info": _get_patient_summary(patient),
        "result": data
    }
    
    # 保存文件
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    return filename


def get_available_models() -> Dict[str, list]:
    """
    获取可用的模型列表
    
    Returns:
        dict: 按提供商分组的模型列表
    """
    return get_available_models()


def print_patient_info(patient: PatientAgent):
    """
    打印病人信息
    
    Args:
        patient: 病人Agent对象
    """
    print(f"""
📋 病人信息:
   - ID: {getattr(patient, 'patient_id', 'unknown')}
   - 年龄: {patient.age}岁
   - 性别: {patient.gender}
   - 教育: {patient.education}
   - 职业: {patient.occupation}
   - 抑郁等级: {patient.depression_level}
   - PHQ-9分数: {patient.score}
   - 核心信念: {patient.core_belief}
   - 中间信念: {patient.intermediate_belief}
   - 应对策略: {patient.coping_strategy}
""")


if __name__ == "__main__":
    # 示例用法
    print("🧠 自我描述生成示例")
    print("=" * 50)
    
    # 示例1: 快速生成
    print("\n1️⃣ 快速生成示例:")
    result = quick_self_description(depression_level="轻度", age=28, gender="女")
    if result["success"]:
        print("✅ 生成成功!")
        print(f"内容预览: {result['content'][:100]}...")
    else:
        print(f"❌ 生成失败: {result['error']}")
    
    # 示例2: 详细配置
    print("\n2️⃣ 详细配置示例:")
    patient = PatientAgent(depression_level="中度", age=35, gender="男")
    result = generate_self_description(
        patient=patient,
        scenario="人际关系",
        style="内心独白",
        time_perspective="当下状态"
    )
    if result["success"]:
        print("✅ 生成成功!")
        print_patient_info(patient)
    else:
        print(f"❌ 生成失败: {result['error']}")
