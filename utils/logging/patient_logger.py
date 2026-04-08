# -*- coding: utf-8 -*-
"""
日志管理模块
用于保存病人的自述、社交媒体发言记录
"""

import os
import json
from datetime import datetime
import uuid

class PatientLogger:
    def __init__(self, patient_id=None, log_dir="logs"):
        """
        初始化日志记录器
        
        Args:
            patient_id: 病人ID，如果为None则自动生成
            log_dir: 日志保存目录
        """
        self.patient_id = patient_id if patient_id else str(uuid.uuid4())[:8]
        self.log_dir = log_dir
        
        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 为每个病人创建专门的目录
        self.patient_log_dir = os.path.join(log_dir, f"patient_{self.patient_id}")
        if not os.path.exists(self.patient_log_dir):
            os.makedirs(self.patient_log_dir)
    
    def _get_timestamp(self):
        """获取当前时间戳"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def log_self_description(self, content, context=None):
        """
        记录病人自我状态阐述
        
        Args:
            content: 自述内容
            context: 上下文信息（如触发条件等）
        """
        log_entry = {
            "timestamp": self._get_timestamp(),
            "type": "self_description",
            "patient_id": self.patient_id,
            "content": content,
            "context": context
        }
        
        filename = os.path.join(self.patient_log_dir, "self_descriptions.jsonl")
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_social_post(self, content, platform="general", context=None):
        """
        记录社交媒体发言
        
        Args:
            content: 发言内容
            platform: 平台类型
            context: 上下文信息
        """
        log_entry = {
            "timestamp": self._get_timestamp(),
            "type": "social_post",
            "patient_id": self.patient_id,
            "platform": platform,
            "content": content,
            "context": context
        }
        
        filename = os.path.join(self.patient_log_dir, "social_posts.jsonl")
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    

    
    def save_patient_profile(self, profile_data):
        """
        保存病人档案
        
        Args:
            profile_data: 病人档案数据字典
        """
        profile_with_meta = {
            "timestamp": self._get_timestamp(),
            "patient_id": self.patient_id,
            "profile": profile_data
        }
        
        filename = os.path.join(self.patient_log_dir, "patient_profile.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(profile_with_meta, f, ensure_ascii=False, indent=2)
    

    
    def get_social_posts_history(self, limit=None):
        """
        获取社交媒体发言历史
        
        Args:
            limit: 限制返回的发言数量
            
        Returns:
            list: 发言历史列表
        """
        filename = os.path.join(self.patient_log_dir, "social_posts.jsonl")
        posts = []
        
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    posts.append(json.loads(line.strip()))
        
        if limit:
            posts = posts[-limit:]
            
        return posts
    
    def get_self_descriptions_history(self, limit=None):
        """
        获取自述历史
        
        Args:
            limit: 限制返回的自述数量
            
        Returns:
            list: 自述历史列表
        """
        filename = os.path.join(self.patient_log_dir, "self_descriptions.jsonl")
        descriptions = []
        
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    descriptions.append(json.loads(line.strip()))
        
        if limit:
            descriptions = descriptions[-limit:]
            
        return descriptions
    
    def log_response(self, response: str, prompt_type: str, metadata=None):
        """
        记录LLM响应
        
        Args:
            response: LLM生成的响应内容
            prompt_type: prompt类型 (self_description, social_post, etc.)
            metadata: 额外的元数据
            
        Returns:
            str: 日志文件路径
        """
        log_entry = {
            "timestamp": self._get_timestamp(),
            "type": prompt_type,
            "patient_id": self.patient_id,
            "content": response,
            "metadata": metadata or {}
        }
        
        if prompt_type == "self_description":
            filename = os.path.join(self.patient_log_dir, "self_descriptions.jsonl")
        elif prompt_type == "social_post":
            filename = os.path.join(self.patient_log_dir, "social_posts.jsonl")
        else:
            filename = os.path.join(self.patient_log_dir, f"{prompt_type}.jsonl")
        
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        return filename
    
    def get_responses_by_type(self, response_type: str, limit=None):
        """
        根据类型获取响应历史
        
        Args:
            response_type: 响应类型
            limit: 限制返回数量
            
        Returns:
            list: 响应历史列表
        """
        if response_type == "self_description":
            return self.get_self_descriptions_history(limit)
        elif response_type == "social_post":
            return self.get_social_posts_history(limit)
        else:
            filename = os.path.join(self.patient_log_dir, f"{response_type}.jsonl")
            responses = []
            
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    for line in f:
                        responses.append(json.loads(line.strip()))
            
            if limit:
                responses = responses[-limit:]
                
            return responses
    
    def get_all_responses(self, limit=None):
        """
        获取所有响应历史
        
        Args:
            limit: 限制返回数量
            
        Returns:
            list: 所有响应历史列表
        """
        all_responses = []
        
        # 获取自述
        all_responses.extend(self.get_self_descriptions_history())
        
        # 获取社交媒体发言
        all_responses.extend(self.get_social_posts_history())
        
        # 获取其他类型的响应
        for file in os.listdir(self.patient_log_dir):
            if file.endswith('.jsonl') and file not in ['self_descriptions.jsonl', 'social_posts.jsonl']:
                filename = os.path.join(self.patient_log_dir, file)
                if os.path.exists(filename):
                    with open(filename, "r", encoding="utf-8") as f:
                        for line in f:
                            all_responses.append(json.loads(line.strip()))
        
        # 按时间戳排序
        all_responses.sort(key=lambda x: x.get('timestamp', ''))
        
        if limit:
            all_responses = all_responses[-limit:]
            
        return all_responses
