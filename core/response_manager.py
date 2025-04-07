"""
响应管理模块 - 处理对话历史和响应生成
"""
import json
from datetime import datetime

class ResponseManager:
    def __init__(self, llm_client, config):
        """
        初始化响应管理器
        
        Args:
            llm_client: LLM 客户端实例
            config: 配置对象
        """
        self.llm_client = llm_client
        self.max_turns = config.MAX_CONVERSATION_TURNS
        self.history = []
        self.turn_count = 0
        
    def add_exchange(self, user_message, assistant_message):
        """
        添加一轮对话到历史
        
        Args:
            user_message (str): 用户消息
            assistant_message (str): 助手回复
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.history.append({
            "turn": self.turn_count + 1,
            "timestamp": timestamp,
            "user": user_message,
            "assistant": assistant_message
        })
        
        self.turn_count += 1
        
        # 如果超过最大轮数，移除最早的对话
        if len(self.history) > self.max_turns:
            self.history.pop(0)
    
    def get_history_messages(self):
        """
        获取适合API调用的历史消息格式
        
        Returns:
            list: 消息列表
        """
        messages = []
        
        for exchange in self.history:
            messages.append({"role": "user", "content": exchange["user"]})
            messages.append({"role": "assistant", "content": exchange["assistant"]})
        
        return messages
    
    def get_history(self, turns=None):
        """
        获取历史对话
        
        Args:
            turns (int, optional): 获取的轮数，默认全部
            
        Returns:
            list: 对话历史
        """
        if turns is None or turns >= len(self.history):
            return self.history
        
        return self.history[-turns:]
    
    def clear_history(self):
        """清空对话历史"""
        self.history = []
        self.turn_count = 0
    
    def save_history(self, filename):
        """
        保存对话历史到文件
        
        Args:
            filename (str): 文件名
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def load_history(self, filename):
        """
        从文件加载对话历史
        
        Args:
            filename (str): 文件名
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
                
                # 更新对话轮数
                if self.history:
                    self.turn_count = max(exchange["turn"] for exchange in self.history)
        except FileNotFoundError:
            print(f"文件不存在: {filename}")
        except json.JSONDecodeError:
            print(f"文件格式错误: {filename}")