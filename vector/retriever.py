"""
记忆检索模块 - 负责从向量存储中检索相关记忆
"""
import faiss
import pickle

class MemoryRetriever:
    def __init__(self, embedder):
        """
        初始化记忆检索器
        
        Args:
            embedder: MemoryEmbedder实例
        """
        self.embedder = embedder
    
    def search(self, query, top_k=3):
        """
        搜索相关记忆
        
        Args:
            query (str): 查询文本
            top_k (int): 返回结果数量
            
        Returns:
            list: 检索到的记忆文本列表
            list: 相似度分数列表
        """
        # 确保模型和索引已加载
        if not self.embedder.index or self.embedder.index.ntotal == 0:
            return [], []
            
        # 向量化查询
        query_vec = self.embedder.model.encode([query], normalize_embeddings=True).astype('float32')
        
        # 执行检索
        scores, indices = self.embedder.index.search(query_vec, min(top_k, self.embedder.index.ntotal))
        
        # 获取文本结果
        results = []
        for idx in indices[0]:
            if idx >= 0 and idx < len(self.embedder.texts):  # 检查索引有效性
                results.append(self.embedder.texts[idx])
        
        return results, scores[0].tolist()
    
    def format_search_results(self, query, results, scores, prefix="根据您的记忆，我知道：\n"):
        """
        格式化搜索结果为上下文字符串
        
        Args:
            query (str): 查询文本
            results (list): 检索结果
            scores (list): 相似度分数
            prefix (str): 前缀文本
            
        Returns:
            str: 格式化后的上下文
        """
        if not results:
            return ""
            
        context = prefix
        for i, (result, score) in enumerate(zip(results, scores)):
            if score < 0.5:  # 过滤掉相似度较低的结果
                continue
            context += f"- {result}\n"
            
        return context