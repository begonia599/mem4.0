import faiss
import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer

def load_model(model_name):
    print("正在加载模型...")
    model = SentenceTransformer(model_name)
    print("模型加载完成！")
    return model

def retrieve_and_display(index, texts, model, query, top_k=2):
    # 向量化查询文本
    query_vec = model.encode([query], normalize_embeddings=True).astype('float32')

    # 执行检索
    distances, indices = index.search(query_vec, top_k)

    # 输出结果
    print(f"查询：'{query}'")
    print("="*50)
    for i, (idx, dist) in enumerate(zip(indices[0], distances[0])):
        print(f"结果 {i+1} (距离：{dist:.4f}):")
        print(texts[idx])
        print("-"*50)

def main():
    # 固定参数
    index_file = 'data/index.faiss'  # FAISS索引文件路径
    texts_file = 'data/texts.pkl'  # 文本列表文件路径(.pkl)
    model_name = 'BAAI/bge-large-zh-v1.5'  # 模型名称，默认: paraphrase-multilingual-MiniLM-L12-v2
    top_k = 2  # 返回结果数量

    # 加载模型
    model = load_model(model_name)

    # 加载FAISS索引和文本列表
    index = faiss.read_index(index_file)
    with open(texts_file, 'rb') as f:
        texts = pickle.load(f)

    while True:
        # 用户输入查询文本
        query = input("请输入查询文本（输入 'exit' 退出程序）：")
        
        if query.lower() == 'exit':
            print("退出程序...")
            break

        # 查询并输出结果
        retrieve_and_display(index, texts, model, query)

if __name__ == "__main__":
    main()
