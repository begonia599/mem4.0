"""
记忆提取模块 - 从用户输入中提取结构化的记忆信息
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from model.prompts import MEMORY_EXTRACTION_PROMPT

# 定义记忆数据模型
class MemoryItem(BaseModel):
    content: str = Field(description="记忆的具体内容")
    category: str = Field(description="记忆的分类，如'个人信息'、'偏好'、'计划'、'关系'等")
    confidence: float = Field(description="提取的置信度，范围0-1", ge=0, le=1)
    source: str = Field(description="记忆的来源内容")
    timestamp: str = Field(description="记忆创建时间")

class MemoryExtraction(BaseModel):
    memories: List[MemoryItem] = Field(description="提取的记忆列表")

class MemoryExtractor:
    def __init__(self, llm_client):
        """
        初始化记忆提取器
        
        Args:
            llm_client: LLM 客户端实例
        """
        self.llm_client = llm_client
        
    def extract(self, user_input):
        """
        从用户输入中提取结构化记忆
        
        Args:
            user_input (str): 用户输入内容
            
        Returns:
            list: 提取的记忆项列表
        """
        try:
            # 使用LLM进行结构化提取
            extraction = self.llm_client.ask_json(
                prompt=user_input,
                system_message=MEMORY_EXTRACTION_PROMPT,
                response_model=MemoryExtraction
            )
            
            # 添加时间戳和来源
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for memory in extraction.memories:
                if not memory.timestamp:
                    memory.timestamp = current_time
                if not memory.source:
                    memory.source = user_input[:100] + ("..." if len(user_input) > 100 else "")
                    
            return extraction.memories
            
        except Exception as e:
            print(f"记忆提取失败: {e}")
            return []