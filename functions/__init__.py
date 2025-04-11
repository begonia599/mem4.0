"""
函数调用模块 - 包含可被大模型调用的各类工具函数
"""
from .function_registry import FunctionRegistry
from .weather import get_weather

__all__ = ['FunctionRegistry', 'get_weather']