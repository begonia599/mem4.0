from openai import OpenAI
from .prompt_manager import PromptManager
from typing import Type, TypeVar, Any, Optional
import json

# 泛型类型变量，用于类型提示
T = TypeVar('T')

class GrokClient:
    def __init__(self, api_key, base_url, default_model="grok-2"):
        """
        初始化 Grok API 客户端
        
        Args:
            api_key (str): API 密钥
            base_url (str): API 基础 URL
            default_model (str): 默认使用的模型
        """
        self.default_model = default_model
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
    
    def ask(self, prompt, model=None, system_message=None, history_messages=None):
        """
        向 Grok API 发送请求获取回复
        
        Args:
            prompt (str): 用户的提问或提示
            model (str, optional): 使用的模型名称，如不指定则使用默认模型
            system_message (str, optional): 系统消息，设置AI角色
            history_messages (list, optional): 历史对话消息列表
            
        Returns:
            str: Grok 的回复内容
        """
        if model is None:
            model = self.default_model
            
        messages = []
        
        # 如果提供了系统消息，添加到消息列表
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # 如果提供了历史消息，添加到消息列表
        if history_messages:
            messages.extend(history_messages)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": prompt})
        
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
            )
            print(messages)
            return completion.choices[0].message.content
        except Exception as e:
            return f"请求出错: {str(e)}"
    
    def ask_with_template(self, prompt, template_name, model=None, history_messages=None, **template_vars):
        """使用模板发送请求"""
        system_message = None
        if template_name:
            if template_vars:
                system_message = PromptManager.format_prompt(template_name, **template_vars)
            else:
                system_message = PromptManager.get_prompt(template_name)
                
        return self.ask(prompt, model, system_message, history_messages)
    
    def ask_json(self, prompt, system_message=None, model=None, history_messages=None, response_model: Optional[Type[T]] = None):
        """
        请求并返回结构化JSON响应
        
        Args:
            prompt (str): 用户的提问或提示
            system_message (str, optional): 系统消息
            model (str, optional): 使用的模型名称
            history_messages (list, optional): 历史对话消息
            response_model (Type, optional): Pydantic模型类，用于验证和解析响应
            
        Returns:
            T or dict: 结构化的响应对象，如果指定了response_model则返回该类型的实例
        """
        if model is None:
            model = self.default_model
            
        messages = []
        
        # 如果提供了系统消息，添加到消息列表
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # 如果提供了历史消息，添加到消息列表
        if history_messages:
            messages.extend(history_messages)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": prompt})
        
        try:
            if response_model:
                # 使用parse API进行结构化解析
                completion = self.client.beta.chat.completions.parse(
                    model=model,
                    messages=messages,
                    response_format=response_model,
                )
                return completion.choices[0].message.parsed
            else:
                # 直接获取JSON响应
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    response_format={"type": "json_object"},
                )
                json_str = completion.choices[0].message.content
                return json.loads(json_str)
                
        except Exception as e:
            print(f"JSON请求出错: {str(e)}")
            if response_model:
                # 返回空模型实例
                return response_model()
            return {"error": str(e)}
    
    # 在GrokClient类中添加支持函数调用的方法

    def ask_with_functions(self, prompt, functions, model=None, system_message=None, history_messages=None):
        """
        使用函数调用能力向API发送请求，采用单次调用模式
        """
        if model is None:
            model = self.default_model
            
        messages = []
        
        # 如果提供了系统消息，添加到消息列表
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # 如果提供了历史消息，添加到消息列表
        if history_messages:
            messages.extend(history_messages)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": prompt})
        
        try:
            # 发送带函数定义的请求
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=functions,
                tool_choice="auto",
                timeout=60
            )
            
            response_message = completion.choices[0].message
            
            # 检查是否有工具调用
            if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
                # 提取工具调用信息
                tool_call = response_message.tool_calls[0]
                function_call = {
                    "name": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments)
                }
                
                return {
                    "content": response_message.content or "",
                    "function_call": function_call,
                    "has_function_call": True
                }
            else:
                # 没有工具调用，只返回内容
                return {
                    "content": response_message.content,
                    "has_function_call": False
                }
                
        except Exception as e:
            print(f"⚠️ 函数调用请求出错: {str(e)}")
            return {
                "content": f"请求出错: {str(e)}",
                "error": str(e),
                "has_function_call": False
            }