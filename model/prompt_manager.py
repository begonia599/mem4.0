"""
提示词管理模块
"""
from . import prompts

class PromptManager:
    """提示词模板管理器"""
    
    @staticmethod
    def get_prompt(prompt_name):
        """获取指定名称的提示词模板"""
        return getattr(prompts, prompt_name, None)
    
    @staticmethod
    def list_prompts():
        """列出所有可用的提示词模板名称"""
        return [name for name in dir(prompts) if name.isupper() and isinstance(getattr(prompts, name), str)]
    
    @staticmethod
    def format_prompt(prompt_name, **kwargs):
        """格式化提示词模板"""
        template = PromptManager.get_prompt(prompt_name)
        if template:
            return template.format(**kwargs)
        return None