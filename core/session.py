"""
会话管理模块 - 控制对话和记忆的整体流程
"""
import threading
import queue
import time
import os
from .memory_manager import MemoryManager
from .response_manager import ResponseManager
from vector.embedder import MemoryEmbedder
from vector.retriever import MemoryRetriever

class Session:
    def __init__(self, llm_client, config):
        """
        初始化会话管理器
        
        Args:
            llm_client: LLM 客户端实例
            config: 配置对象
        """
        self.llm_client = llm_client
        self.config = config
        
        # 创建队列用于线程间通信
        self.memory_queue = queue.Queue()  # 发送到记忆管理器的队列
        self.response_queue = queue.Queue()  # 从记忆管理器接收的队列
        
        # 初始化向量化组件（如果启用）
        self.embedder = None
        self.retriever = None
        if hasattr(config, 'VECTOR_SEARCH_ENABLED') and config.VECTOR_SEARCH_ENABLED:
            try:
                self.embedder = MemoryEmbedder(config)
                self.embedder.load_or_create_index()
                self.retriever = MemoryRetriever(self.embedder)
                print("向量检索功能已初始化")
            except Exception as e:
                print(f"向量检索功能初始化失败: {e}")
        
        # 创建管理器
        self.memory_manager = MemoryManager(llm_client, self.memory_queue, self.response_queue, self.embedder)
        self.response_manager = ResponseManager(llm_client, config)
        
        # 会话状态
        self.system_message = None
        self.model = config.DEFAULT_MODEL
        self.enable_memory = config.ENABLE_MEMORY
        self.auto_memory = False
        self.running = False
        self.memories = []
        
        # 线程
        self.memory_thread = None
        
    def start(self):
        """启动会话，包括记忆处理线程"""
        if self.running:
            return
            
        self.running = True
        self.memory_thread = threading.Thread(target=self._memory_processor)
        self.memory_thread.daemon = True  # 守护线程，主线程结束时自动退出
        self.memory_thread.start()
        
    def stop(self):
        """停止会话及相关线程"""
        self.running = False
        if self.memory_thread:
            self.memory_thread.join(timeout=1.0)
    
    def process_message(self, user_message):
        """
        处理用户消息，生成回复
        
        Args:
            user_message (str): 用户输入的消息
            
        Returns:
            str: 助手的回复
        """
        # 获取上下文历史（如果启用）
        history_messages = None
        if self.enable_memory:
            history_messages = self.response_manager.get_history_messages()
        
        # 检索相关记忆（如果启用向量检索）
        memory_context = ""
        if self.retriever and self.config.VECTOR_SEARCH_ENABLED:
            try:
                print("🔎 正在检索相关记忆...")
                results, scores = self.memory_manager.query_memories(
                    user_message, 
                    self.retriever, 
                    self.config.TOP_K
                )
                
                if results:
                    memory_context = self.retriever.format_search_results(
                        user_message, results, scores
                    )
                    print(f"🔍 找到 {len(results)} 条相关记忆")
                    # 可以选择性地显示检索到的部分记忆
                    if len(results) > 0:
                        print(f"📚 相关度最高的记忆: {results[0][:50]}...")
                else:
                    print("📭 未找到相关记忆")
            except Exception as e:
                print(f"❗ 记忆检索失败: {e}")
        
        # 添加记忆上下文到用户消息
        enhanced_message = user_message
        if memory_context:
            enhanced_message = memory_context + "\n\n" + user_message
        
        # 生成回复
        response = self.llm_client.ask(
            prompt=enhanced_message,
            model=self.model,
            system_message=self.system_message,
            history_messages=history_messages
        )
        
        # 保存对话记录（保存原始用户消息，而非增强后的消息）
        self.response_manager.add_exchange(user_message, response)
        
        # 如果启用自动记忆，将消息发送到记忆处理队列
        if self.auto_memory:
            self.memory_queue.put({
                "type": "analyze",
                "content": user_message,
                "timestamp": time.time()
            })
        
        return response
    
    def _memory_processor(self):
        """记忆处理线程的主循环"""
        while self.running:
            try:
                # 非阻塞方式获取任务，超时后检查running状态
                try:
                    task = self.memory_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                # 处理不同类型的记忆任务
                if task["type"] == "analyze":
                    # 分析内容是否需要记忆
                    print("\n🔄 后台正在分析对话内容...")
                    if self.memory_manager.should_remember(task["content"]):
                        print("🧠 检测到重要信息，开始提取记忆...")
                        success = self.memory_manager.extract_memory(task["content"])
                        if success:
                            print("✅ 记忆提取和存储完成")
                        else:
                            print("⚠️ 记忆提取流程完成，但未提取到有效记忆")
                    else:
                        print("📝 分析完成，此内容无需记忆")
                
                # 标记任务完成
                self.memory_queue.task_done()
                
                # 检查是否有来自记忆管理器的响应
                while not self.response_queue.empty():
                    response = self.response_queue.get()
                    if response["type"] == "memory":
                        self.memories.append(response["content"])
                        print(f"新记忆已添加: {response['content']['content']}")
                    self.response_queue.task_done()
                    
            except Exception as e:
                print(f"记忆处理线程错误: {e}")
                
    # 便捷方法
    def set_system_message(self, message):
        self.system_message = message
        
    def set_model(self, model):
        self.model = model
        
    def toggle_memory(self, enable):
        self.enable_memory = enable
        
    def toggle_auto_memory(self, enable):
        self.auto_memory = enable
        
    def get_memories(self):
        return self.memories
        
    def clear_history(self):
        self.response_manager.clear_history()
        
    def get_history(self, turns=None):
        return self.response_manager.get_history(turns)
        
    def save_history(self, filename):
        self.response_manager.save_history(filename)
        
    def load_history(self, filename):
        self.response_manager.load_history(filename)
        
    def toggle_vector_search(self, enable):
        """开关向量检索功能"""
        self.config.VECTOR_SEARCH_ENABLED = enable