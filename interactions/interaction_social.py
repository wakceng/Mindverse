#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社交媒体发言生成交互函数
提供简单易用的接口来生成病人的社交媒体发言内容
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from core.agent_base import PatientAgent
from utils import MultiLLMClient, TextGenerator
from utils.config import get_available_models


def generate_social_post(
    patient: Optional[PatientAgent] = None,
    model: str = "gpt-3.5-turbo",
    api_key: Optional[str] = None,
    platform: str = "微博",
    context: Optional[str] = None,
    post_type: Optional[str] = None,
    save_to_file: bool = True,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成病人的社交媒体发言
    
    Args:
        patient: 病人Agent对象。如果为None，将创建一个随机病人
        model: 要使用的LLM模型名称
        api_key: API密钥。如果为None，将从环境变量中获取
        platform: 社交媒体平台（"微博", "朋友圈", "Twitter", "Instagram"等）
        context: 发言的上下文背景
        post_type: 发言类型（"日常分享", "情感表达", "观点发表"等）
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
        >>> # 使用随机病人生成微博发言
        >>> result = generate_social_post()
        
        >>> # 使用指定病人和参数
        >>> patient = PatientAgent(depression_level="轻度", age=25)
        >>> result = generate_social_post(
        ...     patient=patient,
        ...     platform="朋友圈",
        ...     post_type="情感表达"
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
        
        # 5. 生成社交媒体发言
        result = text_generator.generate_and_save_social_post(
            platform=platform,
            context=context,
            post_type=post_type
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
                "platform": platform,
                "context": context,
                "post_type": post_type,
                "model": model
            }
        }
        
        # 7. 保存到文件（如果需要）
        if save_to_file:
            file_path = _save_result_to_file(
                data=data,
                patient=patient,
                content_type="social_post",
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


def quick_social_post(
    depression_level: str = "正常",
    age: int = 25,
    gender: str = "女",
    platform: str = "微博",
    model: str = "gpt-3.5-turbo"
) -> Dict[str, Any]:
    """
    快速生成社交媒体发言（简化版接口）
    
    Args:
        depression_level: 抑郁等级（"正常", "轻度", "中度", "重度"）
        age: 年龄
        gender: 性别（"男", "女"）
        platform: 社交媒体平台
        model: LLM模型名称
        
    Returns:
        dict: 生成结果
        
    Example:
        >>> result = quick_social_post(depression_level="轻度", platform="朋友圈")
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
    
    return generate_social_post(patient=patient, platform=platform, model=model)


def generate_social_post_series(
    patient: PatientAgent,
    model: str = "gpt-3.5-turbo",
    api_key: Optional[str] = None,
    platforms: List[str] = None,
    post_types: List[str] = None,
    days: int = 7,
    posts_per_day: int = 1,
    save_to_file: bool = True,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    为同一个病人生成一系列社交媒体发言（模拟多天的发言）
    
    Args:
        patient: 病人Agent对象
        model: LLM模型名称
        api_key: API密钥
        platforms: 社交媒体平台列表。如果为None，将使用默认平台
        post_types: 发言类型列表。如果为None，将使用随机类型
        days: 模拟天数
        posts_per_day: 每天发言数量
        save_to_file: 是否保存到文件
        output_dir: 输出目录
        
    Returns:
        dict: 包含多个生成结果的字典
    """
    if platforms is None:
        platforms = ["微博", "朋友圈"]
    
    if post_types is None:
        post_types = ["日常分享", "情感表达", "观点发表", "生活感悟"]
    
    results = []
    errors = []
    
    import random
    
    for day in range(days):
        day_results = []
        
        for post_idx in range(posts_per_day):
            # 随机选择平台和发言类型
            platform = random.choice(platforms)
            post_type = random.choice(post_types)
            
            # 生成不同的上下文背景
            contexts = [
                f"第{day+1}天的日常生活",
                f"今天的心情和感受",
                f"最近的思考和体验",
                None  # 有时不指定上下文，让系统随机生成
            ]
            context = random.choice(contexts)
            
            result = generate_social_post(
                patient=patient,
                model=model,
                api_key=api_key,
                platform=platform,
                context=context,
                post_type=post_type,
                save_to_file=save_to_file,
                output_dir=output_dir
            )
            
            if result["success"]:
                result["day"] = day + 1
                result["post_index"] = post_idx + 1
                day_results.append(result)
                results.append(result)
            else:
                error_msg = f"第{day+1}天第{post_idx+1}条发言生成失败: {result['error']}"
                errors.append(error_msg)
        
    return {
        "success": len(results) > 0,
        "total_requested": days * posts_per_day,
        "successful_count": len(results),
        "failed_count": len(errors),
        "days_simulated": days,
        "posts_per_day": posts_per_day,
        "results": results,
        "errors": errors,
        "patient_info": _get_patient_summary(patient)
    }


def generate_platform_comparison(
    patient: PatientAgent,
    model: str = "gpt-3.5-turbo",
    api_key: Optional[str] = None,
    platforms: List[str] = None,
    same_context: bool = True,
    context: Optional[str] = None,
    save_to_file: bool = True,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    为同一个病人在不同平台生成发言，用于比较不同平台的表达差异
    
    Args:
        patient: 病人Agent对象
        model: LLM模型名称
        api_key: API密钥
        platforms: 要比较的平台列表
        same_context: 是否使用相同的上下文（便于比较）
        context: 统一的上下文背景
        save_to_file: 是否保存到文件
        output_dir: 输出目录
        
    Returns:
        dict: 包含各平台生成结果的比较
    """
    if platforms is None:
        platforms = ["微博", "朋友圈", "Twitter", "Instagram"]
    
    if same_context and context is None:
        context = "分享今天的心情和感受"
    
    results = {}
    errors = []
    
    for platform in platforms:
        result = generate_social_post(
            patient=patient,
            model=model,
            api_key=api_key,
            platform=platform,
            context=context if same_context else None,
            post_type="情感表达",  # 统一使用情感表达类型便于比较
            save_to_file=save_to_file,
            output_dir=output_dir
        )
        
        if result["success"]:
            results[platform] = result
        else:
            errors.append(f"{platform}平台生成失败: {result['error']}")
    
    return {
        "success": len(results) > 0,
        "platforms_requested": platforms,
        "successful_platforms": list(results.keys()),
        "failed_count": len(errors),
        "comparison_results": results,
        "errors": errors,
        "patient_info": _get_patient_summary(patient),
        "context_used": context if same_context else "各平台使用不同上下文"
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


def get_supported_platforms() -> List[str]:
    """
    获取支持的社交媒体平台列表
    
    Returns:
        list: 支持的平台名称列表
    """
    return ["微博", "朋友圈", "Twitter", "Instagram", "TikTok", "小红书"]


def get_supported_post_types() -> List[str]:
    """
    获取支持的发言类型列表
    
    Returns:
        list: 支持的发言类型列表
    """
    return ["日常分享", "情感表达", "观点发表", "生活感悟", "工作动态", "健康状态"]


def print_social_post_result(result: Dict[str, Any], show_metadata: bool = False):
    """
    格式化打印社交媒体发言结果
    
    Args:
        result: 生成结果
        show_metadata: 是否显示元数据
    """
    if not result["success"]:
        print(f"❌ 生成失败: {result['error']}")
        return
    
    print("📱 社交媒体发言生成结果")
    print("=" * 50)
    
    params = result.get("generation_params", {})
    print(f"🔹 平台: {params.get('platform', '未知')}")
    print(f"🔹 类型: {params.get('post_type', '未知')}")
    print(f"🔹 模型: {params.get('model', '未知')}")
    
    print(f"\n📝 发言内容:")
    print("-" * 30)
    print(result["content"])
    print("-" * 30)
    
    if show_metadata:
        metadata = result.get("metadata", {})
        print(f"\n📊 生成统计:")
        print(f"   - 总tokens: {metadata.get('total_tokens', 0)}")
        print(f"   - 生成时间: {metadata.get('generation_time', 0):.2f}秒")
        print(f"   - 预估成本: ${metadata.get('cost_estimate_usd', 0):.6f}")


if __name__ == "__main__":
    # 示例用法
    print("📱 社交媒体发言生成示例")
    print("=" * 50)
    
    # 示例1: 快速生成
    print("\n1️⃣ 快速生成示例:")
    result = quick_social_post(depression_level="轻度", platform="朋友圈")
    print_social_post_result(result)
    
    # 示例2: 平台比较
    print("\n2️⃣ 平台比较示例:")
    patient = PatientAgent(depression_level="中度", age=28, gender="女")
    comparison = generate_platform_comparison(
        patient=patient,
        platforms=["微博", "朋友圈"],
        context="今天心情有些低落"
    )
    
    if comparison["success"]:
        print("✅ 平台比较生成成功!")
        for platform, result in comparison["comparison_results"].items():
            print(f"\n{platform}平台发言:")
            print(f"  {result['content'][:50]}...")
    else:
        print(f"❌ 平台比较失败: {comparison['errors']}")
