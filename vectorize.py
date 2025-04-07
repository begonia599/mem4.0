import numpy as np
import faiss
import os
import pickle
from sentence_transformers import SentenceTransformer

# 模型加载函数
def load_model(model_name):
    print("正在加载模型...")
    model = SentenceTransformer(model_name)
    print("模型加载完成！")
    return model

# 文本向量化和存储函数
def process_and_store(model, input_file, vectors_file, texts_file, index_file):
    # 读取输入文本
    with open(input_file, 'r', encoding='utf-8') as f:
        texts = [line.strip() for line in f if line.strip()]

    # 批量向量化
    print(f"正在向量化 {len(texts)} 条文本...")
    vectors = model.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=True)

    # 保存向量和文本
    os.makedirs(os.path.dirname(vectors_file), exist_ok=True)
    np.save(vectors_file, vectors)
    with open(texts_file, 'wb') as f:
        pickle.dump(texts, f)
    print(f"向量已保存至 {vectors_file}")
    print(f"文本列表已保存至 {texts_file}")

    # 创建FAISS索引并保存
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)  # 内积（等价于余弦相似度，需向量归一化）
    index.add(vectors)
    faiss.write_index(index, index_file)
    print(f"FAISS索引已保存至 {index_file}")
    print(f"索引包含 {index.ntotal} 条数据")

def main():
    # 固定参数
    input_file = 'input.txt'  # 输入文本文件路径，每行一个文本
    vectors_file = 'data/vectors.npy'  # 输出向量文件路径(.npy)
    texts_file = 'data/texts.pkl'  # 输出文本列表文件路径(.pkl)
    index_file = 'data/index.faiss'  # 输出FAISS索引文件路径
    model_name = 'BAAI/bge-large-zh-v1.5'  # 模型名称，默认: paraphrase-multilingual-MiniLM-L12-v2

    # 加载模型
    model = load_model(model_name)

    while True:
        # 用户输入操作
        user_input = input("请输入操作（1-存入信息，exit-退出）：")
        
        if user_input == '1':
            process_and_store(model, input_file, vectors_file, texts_file, index_file)
        elif user_input.lower() == 'exit':
            print("退出程序...")
            break
        else:
            print("无效输入，请输入 '1' 或 'exit'。")

if __name__ == "__main__":
    main()
