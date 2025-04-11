"""
函数注册中心 - 管理所有可供大模型调用的函数
"""
import inspect
import json

class FunctionRegistry:
    def __init__(self):
        """
        初始化函数注册中心
        """
        self.functions = {}
        
    def register(self, func, name=None, description=None, parameters=None):
        """
        注册一个函数
        
        Args:
            func: 要注册的函数
            name (str, optional): 函数名称，如不提供则使用函数原名
            description (str, optional): 函数描述
            parameters (dict, optional): 函数参数描述，如不提供则自动从函数签名生成
        """
        func_name = name or func.__name__
        
        # 如果没有提供参数描述，尝试从函数签名生成
        if parameters is None:
            parameters = self._get_parameters_from_signature(func)
        
        # 从函数文档获取描述
        if description is None and func.__doc__:
            description = func.__doc__.strip()
        
        self.functions[func_name] = {
            "function": func,
            "description": description,
            "parameters": parameters
        }
        
        return self
    
    def _get_parameters_from_signature(self, func):
        """
        从函数签名获取参数信息
        
        Args:
            func: 函数对象
            
        Returns:
            dict: 参数描述对象
        """
        sig = inspect.signature(func)
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            # 跳过self参数
            if param_name == 'self':
                continue
                
            # 获取参数类型提示
            annotation = param.annotation
            param_type = "string"  # 默认类型
            
            if annotation != inspect.Parameter.empty:
                if annotation == str:
                    param_type = "string"
                elif annotation == int:
                    param_type = "integer"
                elif annotation == float:
                    param_type = "number"
                elif annotation == bool:
                    param_type = "boolean"
            
            # 参数描述
            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }
            
            # 如果参数没有默认值，则为必需参数
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    def get_function(self, name):
        """
        获取指定名称的函数
        
        Args:
            name (str): 函数名称
            
        Returns:
            function or None: 函数对象，如不存在则返回None
        """
        if name in self.functions:
            return self.functions[name]["function"]
        return None
    
    def get_function_definitions(self):
        """
        获取所有函数的定义，用于API调用
        
        Returns:
            list: 函数定义列表，符合OpenAI tools格式
        """
        definitions = []
        
        for name, info in self.functions.items():
            definition = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": info["description"] or f"Function {name}",
                    "parameters": info["parameters"]
                }
            }
            definitions.append(definition)
            
        return definitions
    
    def execute_function(self, name, arguments):
        """
        执行指定名称的函数
        
        Args:
            name (str): 函数名称
            arguments (dict): 函数参数
            
        Returns:
            any: 函数执行结果
            
        Raises:
            ValueError: 如果函数不存在
            Exception: 函数执行中的任何错误
        """
        func = self.get_function(name)
        if func is None:
            raise ValueError(f"函数 '{name}' 不存在")
        
        try:
            return func(**arguments)
        except Exception as e:
            raise Exception(f"执行函数 '{name}' 时出错: {str(e)}")