# -*- coding: utf-8 -*-
"""
交互模块
包含自我描述生成和社交媒体发言生成功能
"""

# 自我描述生成相关函数
from .interaction_self_description import (
    generate_self_description,
    quick_self_description,
    generate_multiple_self_descriptions,
    print_patient_info
)

# 社交媒体发言生成相关函数
from .interaction_social import (
    generate_social_post,
    quick_social_post,
    generate_social_post_series,
    generate_platform_comparison,
    get_supported_platforms,
    get_supported_post_types,
    print_social_post_result
)

__all__ = [
    # 自我描述生成
    'generate_self_description',
    'quick_self_description',
    'generate_multiple_self_descriptions',
    'print_patient_info',
    
    # 社交媒体发言生成
    'generate_social_post',
    'quick_social_post',
    'generate_social_post_series',
    'generate_platform_comparison',
    'get_supported_platforms',
    'get_supported_post_types',
    'print_social_post_result'
]
