# -*- coding: utf-8 -*-
"""
基本配置信息
包含年龄、性别、教育、职业等基础人口统计学信息
"""

# 年龄范围
MIN_AGE = 13
MAX_AGE = 39

# 性别选项
GENDERS = ["男", "女", "非二元"]

# 教育程度
EDUCATION_LEVELS = ["初中", "高中", "本科", "硕士", "博士"]

# 职业状态
OCCUPATION_STATUS = ["学生", "办公室职员", "无业", "自由职业者"]

# 婚姻状况
MARITAL_STATUS = ["单身", "恋爱", "已婚", "离异"]

# 抑郁标签
DEPRESSION_TAGS = ["抑郁", "非抑郁"]

# 非抑郁人群只有正常状态
NON_DEPRESSED_LEVELS = ["正常"]

# 抑郁人群按PHQ-9量表分级
DEPRESSED_LEVELS = ["轻度", "中度", "重度"]

# 所有可能的抑郁等级（用于显示）
ALL_DEPRESSION_LEVELS = NON_DEPRESSED_LEVELS + DEPRESSED_LEVELS

# Big Five人格特质
PERSONALITY_TRAITS = ["外向性", "宜人性", "责任心", "神经质", "开放性"]

# 语言风格选项
LANGUAGE_STYLES = [
    "大方交流",
    "正式书面语、用词准确", 
    "文艺化、比喻丰富",
    "消极表达、用词悲观",
    "情绪化表达、用词激烈",
    "简洁明了、不爱多说",
    "模糊表达、回避直接"
]

# 表达语调
EXPRESSION_TONES = ["消极", "中性", "积极"]

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "filename": "mindverse.log",
    "max_bytes": 10485760,  # 10MB
    "backup_count": 5
}

# 缓存配置
CACHE_CONFIG = {
    "enabled": True,
    "max_size": 1000,
    "ttl": 3600,  # 1小时
    "cache_dir": "cache"
}
