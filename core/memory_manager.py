"""
记忆管理模块 - 处理大模型对话中的记忆提取和管理
"""
from model.prompts import MEMORY_JUDGE_PROMPT
from memory.extract import MemoryExtractor
import time

class MemoryManager:
    def __init__(self, llm_client, input_queue, output_queue, embedder=None):
        """
        初始化记忆管理器
        
        Args:
            llm_client: LLM 客户端实例
            input_queue: 接收任务的队列
            output_queue: 发送结果的队列
            embedder: 向量化器实例(可选)
        """
        self.llm_client = llm_client
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.extractor = MemoryExtractor(llm_client)
        self.embedder = embedder
        
    def should_remember(self, content):
        """
        判断内容是否包含需要记忆的信息
        
        Args:
            content (str): 用户输入内容
            
        Returns:
            bool: 是否应该记忆
        """
        print("📝 正在分析内容是否包含重要信息...")
        response = self.llm_client.ask(
            prompt=content,
            system_message=MEMORY_JUDGE_PROMPT
        )
        
        result = response.lower().strip() in ["是", "yes", "true", "1"]
        if result:
            print("✅ 检测到包含值得记忆的信息")
        else:
            print("❌ 未检测到需要记忆的重要信息")
        return result

    def extract_memory(self, content):
        """
        从内容中提取结构化记忆
        
        Args:
            content (str): 用户输入内容
            
        Returns:
            bool: 是否成功提取记忆
        """
        print("🔍 正在分析并提取结构化记忆...")
        # 使用提取器获取结构化记忆
        memories = self.extractor.extract(content)
        
        if not memories:
            print("⚠️ 未能提取出结构化记忆")
            return False
        
        print(f"📌 成功提取出 {len(memories)} 条记忆")
        
        # 向量化记忆并添加到索引（如果启用）
        if self.embedder and memories:
            try:
                print("🧠 正在将记忆向量化存储...")
                self.embedder.add_memories(memories)
                print("💾 记忆向量化存储完成")
            except Exception as e:
                print(f"❗ 向量化记忆失败: {e}")
        
        # 将提取的记忆发送到输出队列
        for memory in memories:
            self.output_queue.put({
                "type": "memory",
                "content": memory.dict()
            })
            
        return len(memories) > 0
        
    def query_memories(self, query, retriever=None, top_k=3):
        """
        根据查询从记忆中检索相关信息
        
        Args:
            query (str): 查询内容
            retriever: 检索器实例(可选)
            top_k (int): 返回结果数量
            
        Returns:
            list: 相关记忆列表
            list: 相似度分数列表
        """
        if retriever:
            return retriever.search(query, top_k)
        return [], []