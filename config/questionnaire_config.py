# -*- coding: utf-8 -*-
"""
心理量表配置
包含PHQ-9和SDS量表的完整配置信息
"""

# PHQ-9量表完整内容
PHQ9_QUESTIONNAIRE = {
    "description": "患者健康问卷抑郁量表（PHQ-9）",
    "instruction": "在过去的2个星期中，您有多少次被以下任何一个问题困扰：",
    "options": ["完全不会", "有过几天", "一半以上的日子", "几乎每天"],
    "scores": [0, 1, 2, 3],
    "questions": [
        {
            "id": 1,
            "question": "做什么事都感到没有兴趣或乐趣",
            "options": ["完全不会", "有过几天", "一半以上的日子", "几乎每天"],
            "scores": [0, 1, 2, 3]
        },
        {
            "id": 2,
            "question": "感到心情低落、沮丧或绝望",
            "options": ["完全不会", "有过几天", "一半以上的日子", "几乎每天"],
            "scores": [0, 1, 2, 3]
        },
        {
            "id": 3,
            "question": "入睡困难、很难熟睡或睡太多",
            "options": ["完全不会", "有过几天", "一半以上的日子", "几乎每天"],
            "scores": [0, 1, 2, 3]
        },
        {
            "id": 4,
            "question": "感到疲劳或无精打采",
            "options": ["完全不会", "有过几天", "一半以上的日子", "几乎每天"],
            "scores": [0, 1, 2, 3]
        },
        {
            "id": 5,
            "question": "胃口不好或吃太多",
            "options": ["完全不会", "有过几天", "一半以上的日子", "几乎每天"],
            "scores": [0, 1, 2, 3]
        },
        {
            "id": 6,
            "question": "觉得自己很糟，或很失败，或让自己或家人很失望",
            "options": ["完全不会", "有过几天", "一半以上的日子", "几乎每天"],
            "scores": [0, 1, 2, 3]
        },
        {
            "id": 7,
            "question": "注意很难集中，例如阅读报纸或看电视",
            "options": ["完全不会", "有过几天", "一半以上的日子", "几乎每天"],
            "scores": [0, 1, 2, 3]
        },
        {
            "id": 8,
            "question": "动作或说话速度缓慢到别人可觉察的程度，或正好相反—您烦躁或坐立不安，动来动去的情况比平常更严重",
            "options": ["完全不会", "有过几天", "一半以上的日子", "几乎每天"],
            "scores": [0, 1, 2, 3]
        },
        {
            "id": 9,
            "question": "有不如死掉或用某种方式伤害自己的念头",
            "options": ["完全不会", "有过几天", "一半以上的日子", "几乎每天"],
            "scores": [0, 1, 2, 3]
        },
        {
            "id": 10,
            "question": "这些问题在您工作、处理家庭事务，或与他人相处上造成了多大困难",
            "options": ["毫无困难", "有点困难", "非常困难", "极度困难"],
            "scores": [0, 1, 2, 3]
        }
    ],
    "scoring": {
        "0-4": "无抑郁症状",
        "5-9": "轻度抑郁",
        "10-14": "中度抑郁",
        "15+": "重度抑郁"
    }
}

# SDS量表完整内容
SDS_QUESTIONNAIRE = {
    "description": "抑郁自评量表（SDS）",
    "instruction": "请仔细阅读每一条，把意思弄明白，然后根据您最近一星期的实际情况，选择最适合您的答案",
    "options": ["没有或很少时间", "小部分时间", "相当多时间", "绝大部分或全部时间"],
    "scores": [1, 2, 3, 4],
    "questions": [
        {
            "id": 1,
            "question": "我觉得闷闷不乐，情绪低沉",
            "type": "positive",  # 正向题
            "scores": [1, 2, 3, 4]
        },
        {
            "id": 2,
            "question": "我觉得一天之中早晨最好",
            "type": "negative",  # 反向题
            "scores": [4, 3, 2, 1]
        },
        {
            "id": 3,
            "question": "我一阵阵哭出来或觉得想哭",
            "type": "positive",
            "scores": [1, 2, 3, 4]
        },
        {
            "id": 4,
            "question": "我晚上睡眠不好",
            "type": "positive",
            "scores": [1, 2, 3, 4]
        },
        {
            "id": 5,
            "question": "我吃得跟平常一样多",
            "type": "negative",
            "scores": [4, 3, 2, 1]
        },
        {
            "id": 6,
            "question": "我与异性密切接触时和以往一样感到愉快",
            "type": "negative",
            "scores": [4, 3, 2, 1]
        },
        {
            "id": 7,
            "question": "我发觉我的体重下降",
            "type": "positive",
            "scores": [1, 2, 3, 4]
        },
        {
            "id": 8,
            "question": "我有便秘的苦恼",
            "type": "positive",
            "scores": [1, 2, 3, 4]
        },
        {
            "id": 9,
            "question": "我心跳比平时快",
            "type": "positive",
            "scores": [1, 2, 3, 4]
        },
        {
            "id": 10,
            "question": "我无缘无故地感到疲乏",
            "type": "positive",
            "scores": [1, 2, 3, 4]
        },
        {
            "id": 11,
            "question": "我的头脑跟平常一样清楚",
            "type": "negative",
            "scores": [4, 3, 2, 1]
        },
        {
            "id": 12,
            "question": "我觉得经常做的事情并没有困难",
            "type": "negative",
            "scores": [4, 3, 2, 1]
        },
        {
            "id": 13,
            "question": "我觉得不安而平静不下来",
            "type": "positive",
            "scores": [1, 2, 3, 4]
        },
        {
            "id": 14,
            "question": "我对将来抱有希望",
            "type": "negative",
            "scores": [4, 3, 2, 1]
        },
        {
            "id": 15,
            "question": "我比平常容易生气激动",
            "type": "positive",
            "scores": [1, 2, 3, 4]
        },
        {
            "id": 16,
            "question": "我觉得作出决定是容易的",
            "type": "negative",
            "scores": [4, 3, 2, 1]
        },
        {
            "id": 17,
            "question": "我觉得自己是个有用的人，有人需要我",
            "type": "negative",
            "scores": [4, 3, 2, 1]
        },
        {
            "id": 18,
            "question": "我的生活过得很有意思",
            "type": "negative",
            "scores": [4, 3, 2, 1]
        },
        {
            "id": 19,
            "question": "我认为如果我死了别人会生活得好些",
            "type": "positive",
            "scores": [1, 2, 3, 4]
        },
        {
            "id": 20,
            "question": "我平常感兴趣的事我仍然照样感兴趣",
            "type": "negative",
            "scores": [4, 3, 2, 1]
        }
    ],
    "scoring": {
        "calculation": "原始分乘以1.25后取整得到标准分",
        "interpretation": {
            "<50": "无抑郁",
            "50-59": "轻度抑郁", 
            "60-69": "中度抑郁",
            "70+": "重度抑郁"
        },
        "note": "抑郁评定的临界值为T分50，分值越高，抑郁倾向越明显"
    }
}
