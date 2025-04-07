基于Grok API的智能对话系统，具有高级记忆管理和向量检索功能。MemGPT4让大语言模型拥有"记忆"能力，通过多线程处理实现信息提取、向量化存储和智能检索。

🚀 功能特点
记忆管理 - 自动提取和保存关键信息，使AI能够"记住"对话中的重要内容
向量检索 - 基于语义相似度从历史记忆中检索相关信息
多线程处理 - 对话和记忆流并行处理，提高响应速度
结构化记忆 - 带类别、置信度的结构化记忆存储
灵活配置 - 可自定义模型、记忆行为和检索参数
对话历史管理 - 保存和加载对话历史
🧠 记忆模块运行原理
当用户输入问题时，程序将分两个线程并行处理信息：

对话线程：检索相关历史记忆，将检索结果与用户问题结合，生成增强回复
记忆线程：判断用户信息是否需要记忆，如需要则提取结构化信息，进行向量化存储

e:\memgpt4\
├── config.py                  # 配置文件（API密钥、模型配置等）
├── main.py                    # 主程序入口
├── test.py                    # JSON格式输出测试样例
├── vectorize.py               # 独立的文本向量化工具脚本
├── retrieve.py                # 独立的向量检索工具脚本
│
├── model/                     # 模型相关模块
│   ├── __init__.py            # 包初始化文件
│   ├── llm_client.py          # LLM客户端实现
│   ├── prompt_manager.py      # 提示词管理器
│   └── prompts.py             # 提示词模板定义
│
├── memory/                    # 记忆相关模块
│   ├── __init__.py            # 包初始化文件
│   ├── history.py             # 对话历史管理
│   ├── judge.py               # 记忆判断模块
│   └── extract.py             # 记忆提取模块
│
├── core/                      # 核心业务逻辑
│   ├── __init__.py            # 包初始化文件
│   ├── memory_manager.py      # 记忆管理器
│   ├── response_manager.py    # 响应管理器
│   └── session.py             # 会话管理
│
└── vector/                    # 向量搜索模块
    ├── __init__.py            # 包初始化文件
    ├── embedder.py            # 记忆向量化模块
    └── retriever.py           # 向量检索模块
📋 安装指南
前置条件
Python 3.8+
pip 包管理器

安装步骤
1.克隆仓库
git clone https://github.com/yourusername/memgpt4.git
cd memgpt4
2.安装依赖
pip install -r requirements.txt
3.配置API密钥 编辑 config.py 文件，设置您的大模型 API密钥：
API_KEY = "你的大模型 API密钥"

🚀 快速开始
1.运行主程序
python main.py
2.命令参考
- exit              退出程序
- system            设置系统消息/AI角色
- models            查看可用模型
- model:模型名       切换使用的模型
- clear             清除对话历史
- history           查看对话历史
- save:文件名       保存对话历史到文件
- load:文件名       从文件加载对话历史
- memory:on/off     开关对话记忆功能
- automemory:on/off 开关自动记忆提取功能
- vector:on/off     开关向量检索功能
- memories          查看已提取的记忆

⚙️ 配置选项
config.py 文件中的主要配置选项：

配置项	说明
API_KEY	Grok API密钥
BASE_URL	API基础URL
DEFAULT_MODEL	默认使用的模型名称
MAX_CONVERSATION_TURNS	最大保存的对话轮数
ENABLE_MEMORY	是否启用对话记忆
EMBEDDING_MODEL	用于向量化的嵌入模型名称
TOP_K	向量检索返回的结果数量
VECTOR_SEARCH_ENABLED	是否启用向量检索功能

🛠 依赖项
openai - OpenAI兼容接口
faiss-cpu - 高效向量检索库
sentence-transformers - 文本向量化
numpy - 科学计算
pydantic - 数据验证

🔧 高级用法
独立向量化工具
使用 vectorize.py 脚本可以将文本文件中的内容向量化存储：
python vectorize.py
独立检索工具
使用 retrieve.py 脚本可以查询已存储的向量记忆：
python retrieve.py

🤝 贡献指南
欢迎为该项目做出贡献：

Fork本仓库
创建您的特性分支 (git checkout -b feature/amazing-feature)
提交您的更改 (git commit -m 'Add some amazing feature')
将您的更改推送到分支 (git push origin feature/amazing-feature)
打开Pull Request
📜 许可证
该项目采用MIT许可证 - 详情参见 LICENSE 文件

📄 版权声明
本项目使用了Grok API，但不隶属于或得到xAI的官方认可。


