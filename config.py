"""
Grok API 配置文件
"""
import os

# API 配置
API_KEY = "xai-R6uxRo22ikTCYBS9UOcVL3OLhQ4FYSnzsFYMPb7yhwVG61MoHrEGXgnA18L2T2UBr9kXmZleSc4Ly4wm"
BASE_URL = "https://api.x.ai/v1"

# 模型配置
DEFAULT_MODEL = "grok-2-latest"
AVAILABLE_MODELS = [
    "grok-2-latest",
    "grok-1",
]

# 对话配置
MAX_CONVERSATION_TURNS = 10  # 最大对话轮数
ENABLE_MEMORY = True         # 是否启用记忆功能

# 向量化配置
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
EMBEDDING_MODEL = "BAAI/bge-large-zh-v1.5"  # 嵌入模型名称
VECTORS_FILE = os.path.join(DATA_DIR, "vectors.npy")  # 向量文件路径
TEXTS_FILE = os.path.join(DATA_DIR, "texts.pkl")  # 文本文件路径
INDEX_FILE = os.path.join(DATA_DIR, "index.faiss")  # 索引文件路径
TOP_K = 3  # 检索返回结果数量
VECTOR_SEARCH_ENABLED = True  # 是否启用向量检索

# 应用配置
APP_NAME = "API "

# 在文件末尾添加高德地图API配置
AMAP_KEY = "d0ffe5458588590f9fb67f1aa2931faa"  # 替换为实际的密钥