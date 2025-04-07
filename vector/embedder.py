"""
记忆向量化模块 - 负责将记忆转换为向量并保存
"""
import os
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer

class MemoryEmbedder:
    def __init__(self, config):
        """
        初始化记忆向量化器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.model_name = config.EMBEDDING_MODEL
        self.vectors_file = config.VECTORS_FILE
        self.texts_file = config.TEXTS_FILE
        self.index_file = config.INDEX_FILE
        
        self.model = None
        self.texts = []
        self.index = None
        
        # 创建数据目录
        os.makedirs(os.path.dirname(self.vectors_file), exist_ok=True)
        
    def load_model(self):
        """加载嵌入模型"""
        if not self.model:
            print("正在加载嵌入模型...")
            self.model = SentenceTransformer(self.model_name)
            print(f"嵌入模型 '{self.model_name}' 加载完成！")
    
    def load_or_create_index(self):
        """加载或创建向量索引"""
        # 加载模型
        self.load_model()
        
        # 尝试加载现有索引和文本
        try:
            self.index = faiss.read_index(self.index_file)
            with open(self.texts_file, 'rb') as f:
                self.texts = pickle.load(f)
            print(f"已加载向量索引，包含 {self.index.ntotal} 条记忆")
            return True
        except (FileNotFoundError, Exception) as e:
            print(f"未找到现有索引或加载失败: {e}")
            # 创建新的索引
            dim = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatIP(dim)
            self.texts = []
            print(f"已创建新的向量索引，维度: {dim}")
            return False
    
    def add_memories(self, memories):
        """
        添加新的记忆到向量存储
        
        Args:
            memories: 记忆列表，每个记忆应有 content 属性
        """
        if not memories:
            return
            
        # 确保模型和索引已加载
        if not self.model or not self.index:
            self.load_or_create_index()
        
        # 提取记忆内容
        memory_texts = [memory.content if hasattr(memory, 'content') else memory['content'] 
                        for memory in memories]
        
        # 向量化
        vectors = self.model.encode(memory_texts, normalize_embeddings=True)
        vectors = vectors.astype('float32')
        
        # 添加到索引
        self.index.add(vectors)
        self.texts.extend(memory_texts)
        
        # 保存更新后的索引和文本
        self._save_index()
        
        print(f"已添加 {len(memories)} 条新记忆到向量存储，总计 {self.index.ntotal} 条")
    
    def _save_index(self):
        """保存索引和文本到文件"""
        faiss.write_index(self.index, self.index_file)
        with open(self.texts_file, 'wb') as f:
            pickle.dump(self.texts, f)