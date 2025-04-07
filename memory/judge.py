"""
记忆判断模块 - 判断用户输入是否包含需要记忆的信息
"""
from model.prompts import MEMORY_JUDGE_PROMPT

class MemoryJudge:
    def __init__(self, llm_client):
        """
        初始化记忆判断器
        
        Args:
            llm_client: LLM 客户端实例
        """
        self.llm_client = llm_client
        
    def should_remember(self, user_input):
        """
        判断用户输入是否包含需要记忆的信息
        
        Args:
            user_input (str): 用户输入
            
        Returns:
            bool: 是否应该记忆
        """
        # 使用 LLM 进行判断
        response = self.llm_client.ask(
            prompt=user_input,
            system_message=MEMORY_JUDGE_PROMPT
        )
        
        # 处理回复
        return response.lower().strip() in ["是", "yes", "true", "1"]
    