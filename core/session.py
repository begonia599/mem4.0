"""
会话管理模块 - 控制对话和记忆的整体流程
"""
import threading
import queue
import time
import os
import json
from .memory_manager import MemoryManager
from .response_manager import ResponseManager
from vector.embedder import MemoryEmbedder
from vector.retriever import MemoryRetriever
from functions.function_registry import FunctionRegistry

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
        
        # 初始化函数注册中心
        self.function_registry = FunctionRegistry()
        
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
        处理用户消息，生成回复 - 采用简化的函数调用流程
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
        
        # 获取函数定义
        function_definitions = self.function_registry.get_function_definitions()
        
        if function_definitions:
            print("🔧 正在分析是否需要调用工具函数...")
            
            # 生成回复（使用函数调用能力）
            response_data = self.llm_client.ask_with_functions(
                prompt=enhanced_message,
                functions=function_definitions,
                model=self.model,
                system_message=self.system_message,
                history_messages=history_messages
            )
            
            # 检查是否有函数调用
            if response_data.get("has_function_call", False):
                function_call = response_data["function_call"]
                function_name = function_call["name"]
                arguments = function_call["arguments"]
                
                print(f"🔧 需要调用函数: {function_name}")
                print(f"📋 参数: {json.dumps(arguments, ensure_ascii=False)}")
                
                try:
                    # 执行函数
                    print(f"⚙️ 正在执行函数...")
                    function_result = self.function_registry.execute_function(function_name, arguments)
                    print(f"✅ 函数执行完成")
                    
                    # 特殊处理天气查询等直接响应的功能
                    if function_name == "get_weather":
                        weather = function_result
                        response = (
                            f"我查到了{weather.get('city', '该城市')}的天气！"
                            f"现在是{weather.get('weather', '未知天气')}，温度{weather.get('temperature', '未知')}℃，"
                            f"湿度{weather.get('humidity', '未知')}%，{weather.get('winddirection', '未知')}风"
                            f"{weather.get('windpower', '未知')}级。"
                        )
                    else:
                        # 将函数结果内嵌到提示中，直接生成回复
                        result_prompt = (
                            f"{user_message}\n\n"
                            f"函数 {function_name} 已执行，返回结果:\n"
                            f"{json.dumps(function_result, ensure_ascii=False, indent=2)}\n\n"
                            f"请基于以上结果回答用户的问题。"
                        )
                        
                        response = self.llm_client.ask(
                            prompt=result_prompt,
                            model=self.model,
                            system_message=self.system_message
                        )
                    
                    # 保存对话记录
                    self.response_manager.add_exchange(user_message, response)
                    
                    # 自动记忆处理
                    if self.auto_memory:
                        self.memory_queue.put({
                            "type": "analyze",
                            "content": user_message,
                            "timestamp": time.time()
                        })
                    
                    return response
                    
                except Exception as e:
                    error_msg = f"函数执行失败: {str(e)}"
                    print(f"❌ {error_msg}")
                    return error_msg
            else:
                # 无函数调用，正常处理
                response = response_data["content"]
        else:
            # 没有可用函数，使用普通模式
            response = self.llm_client.ask(
                prompt=enhanced_message,
                model=self.model,
                system_message=self.system_message,
                history_messages=history_messages
            )
        
        # 保存对话记录
        self.response_manager.add_exchange(user_message, response)
        
        # 自动记忆处理
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

    def register_function(self, func, name=None, description=None, parameters=None):
        """注册一个可调用的函数"""
        self.function_registry.register(func, name, description, parameters)