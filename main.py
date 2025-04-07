import config
import datetime
import os
from model.llm_client import GrokClient
from core.session import Session

def main():
    # 确保数据目录存在
    os.makedirs(getattr(config, 'DATA_DIR', 'data'), exist_ok=True)
    
    # 创建客户端实例
    grok = GrokClient(
        api_key=config.API_KEY,
        base_url=config.BASE_URL,
        default_model=config.DEFAULT_MODEL
    )
    
    # 创建会话
    session = Session(grok, config)
    
    # 启动会话（开始记忆线程）
    session.start()
    
    print(f"===== {config.APP_NAME} =====")
    print("(输入 'exit' 退出，输入 'system' 设置系统消息，输入 'models' 查看可用模型)")
    print("(输入 'history' 查看对话历史，输入 'clear' 清除对话历史)")
    print("(输入 'save:文件名' 保存对话历史，输入 'load:文件名' 加载对话历史)")
    print("(输入 'memory:on/off' 开关记忆功能，输入 'automemory:on/off' 开关自动记忆)")
    print("(输入 'vector:on/off' 开关向量检索功能)")
    print("(输入 'memories' 查看已记忆的内容)")
    print(f"当前默认模型: {config.DEFAULT_MODEL}")
    print(f"对话历史记忆: {'启用' if config.ENABLE_MEMORY else '禁用'}")
    print(f"向量检索功能: {'启用' if getattr(config, 'VECTOR_SEARCH_ENABLED', False) else '禁用'}")
    print(f"最大记忆轮数: {config.MAX_CONVERSATION_TURNS}")
    
    try:
        while True:
            user_input = input("\n请输入您的问题: ")
            
            if user_input.lower() == 'exit':
                print("再见！")
                break
                
            elif user_input.lower() == 'system':
                system_message = input("请输入系统消息(定义AI角色): ")
                session.set_system_message(system_message)
                print(f"系统消息已设置为: '{system_message}'")
                continue
            
            elif user_input.lower() == 'models':
                print("可用模型:")
                for m in config.AVAILABLE_MODELS:
                    print(f"- {m}")
                continue
                
            elif user_input.lower().startswith('model:'):
                model = user_input[6:].strip()
                session.set_model(model)
                print(f"模型已切换为: {model}")
                continue
                
            elif user_input.lower() == 'clear':
                session.clear_history()
                print("对话历史已清除")
                continue
                
            elif user_input.lower() == 'history':
                history = session.get_history()
                if not history:
                    print("对话历史为空")
                else:
                    print("\n---- 对话历史 ----")
                    for exchange in history:
                        print(f"[轮次 {exchange['turn']} | {exchange['timestamp']}]")
                        print(f"用户: {exchange['user']}")
                        print(f"助手: {exchange['assistant']}\n")
                continue
                
            elif user_input.lower().startswith('save:'):
                filename = user_input[5:].strip()
                if not filename:
                    filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                session.save_history(filename)
                print(f"对话历史已保存到: {filename}")
                continue
                
            elif user_input.lower().startswith('load:'):
                filename = user_input[5:].strip()
                if not filename:
                    print("请指定要加载的文件名")
                else:
                    session.load_history(filename)
                    print(f"已从 {filename} 加载对话历史")
                continue
                
            elif user_input.lower() == 'memory:on':
                session.toggle_memory(True)
                print("对话记忆功能已启用")
                continue
                
            elif user_input.lower() == 'memory:off':
                session.toggle_memory(False)
                print("对话记忆功能已禁用")
                continue
                
            elif user_input.lower() == 'automemory:on':
                session.toggle_auto_memory(True)
                print("自动记忆提取功能已启用")
                continue
                
            elif user_input.lower() == 'automemory:off':
                session.toggle_auto_memory(False)
                print("自动记忆提取功能已禁用")
                continue
                
            elif user_input.lower() == 'vector:on':
                session.toggle_vector_search(True)
                print("向量检索功能已启用")
                continue
                
            elif user_input.lower() == 'vector:off':
                session.toggle_vector_search(False)
                print("向量检索功能已禁用")
                continue
                
            elif user_input.lower() == 'memories':
                memories = session.get_memories()
                if not memories:
                    print("当前没有存储的记忆")
                else:
                    print("\n---- 已记忆信息 ----")
                    for i, mem in enumerate(memories, 1):
                        content = mem.get('content', '未知内容')
                        category = mem.get('category', '未分类')
                        confidence = mem.get('confidence', 0)
                        print(f"{i}. [{category}] {content} (置信度: {confidence:.2f})")
                continue
            
            # 处理用户输入并获取回复
            print("正在请求Grok...")
            response = session.process_message(user_input)
            
            print("\nGrok回答:")
            print(response)
            
    finally:
        # 确保在程序退出时停止后台线程
        session.stop()

if __name__ == "__main__":
    main()