"""
对话历史管理模块
"""
import json
from datetime import datetime

class ConversationHistory:
    def __init__(self, max_turns=10):
        """
        初始化对话历史管理器
        
        Args:
            max_turns (int): 最大保存的对话轮数
        """
        self.max_turns = max_turns
        self.history = []  # 存储完整对话历史
        self.turn_count = 0  # 当前对话轮数
    
    def add_exchange(self, user_message, assistant_message):
        """
        添加一轮对话（用户提问和助手回答）
        
        Args:
            user_message (str): 用户消息
            assistant_message (str): 助手回复
        """
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 添加新的对话轮
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
    
    def get_messages_for_api(self):
        """
        获取格式化的对话历史，用于API请求
        
        Returns:
            list: 适合OpenAI API格式的消息列表
        """
        messages = []
        
        for exchange in self.history:
            messages.append({"role": "user", "content": exchange["user"]})
            messages.append({"role": "assistant", "content": exchange["assistant"]})
        
        return messages
    
    def get_recent_history(self, turns=None):
        """
        获取最近的对话历史
        
        Args:
            turns (int, optional): 获取的轮数，默认全部
            
        Returns:
            list: 最近的对话历史
        """
        if turns is None or turns >= len(self.history):
            return self.history
        
        return self.history[-turns:]
    
    def clear(self):
        """
        清空对话历史
        """
        self.history = []
        self.turn_count = 0
    
    def save_to_file(self, filename):
        """
        将对话历史保存到文件
        
        Args:
            filename (str): 文件名
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filename):
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