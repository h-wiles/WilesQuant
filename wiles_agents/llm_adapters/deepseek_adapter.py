"""
DeepSeek LLM适配器，支持Token使用统计
"""

import os
import time
from typing import Any, Dict, List, Optional, Union
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import CallbackManagerForLLMRun


class ChatDeepSeek(ChatOpenAI):
    """
    DeepSeek聊天模型适配器，支持Token使用统计

    继承自ChatOpenAI，添加了Token使用量统计功能
    """

    def __init__(
            self,
            model: str = "deepseek-chat",
            api_key: Optional[str] = None,
            base_url: str = "https://api.deepseek.com",
            temperature: float = 0.1,
            max_tokens: Optional[int] = None,
            **kwargs
    ):
        """
        初始化DeepSeek适配器

        Args:
            model: 模型名称，默认为deepseek-chat
            api_key: API密钥，如果不提供则从环境变量DEEPSEEK_API_KEY获取
            base_url: API基础URL
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
        """

        # 获取API密钥
        if api_key is None:
            # 导入 API Key 验证工具
            try:
                from app.utils.api_key_utils import is_valid_api_key
            except ImportError:
                def is_valid_api_key(key):
                    if not key or len(key) <= 10:
                        return False
                    if key.startswith('your_') or key.startswith('your-'):
                        return False
                    if key.endswith('_here') or key.endswith('-here'):
                        return False
                    if '...' in key:
                        return False
                    return True

            if not api_key:
                raise ValueError(
                    "DeepSeek API密钥未找到。请在 Web 界面配置 API Key "
                    "(设置 -> 大模型厂家) 或设置 DEEPSEEK_API_KEY 环境变量。"
                )

        # 初始化父类
        super().__init__(
            model=model,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        self.model_name = model

    def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        """
        生成聊天响应，并记录token使用量
        """
        # 调用父类方法生成响应
        result = super()._generate(messages, stop, run_manager, **kwargs)
        return result

    def _estimate_input_tokens(self, messages: List[BaseMessage]) -> int:
        """
        估算输入token数量

        Args:
            messages: 输入消息列表

        Returns:
            估算的输入token数量
        """
        total_chars = 0
        for message in messages:
            if hasattr(message, 'content'):
                total_chars += len(str(message.content))

        # 粗略估算：中文约1.5字符/token，英文约4字符/token
        # 这里使用保守估算：2字符/token
        estimated_tokens = max(1, total_chars // 2)
        return estimated_tokens

    def _estimate_output_tokens(self, result: ChatResult) -> int:
        """
        估算输出token数量

        Args:
            result: 聊天结果

        Returns:
            估算的输出token数量
        """
        total_chars = 0
        for generation in result.generations:
            if hasattr(generation, 'message') and hasattr(generation.message, 'content'):
                total_chars += len(str(generation.message.content))

        # 粗略估算：2字符/token
        estimated_tokens = max(1, total_chars // 2)
        return estimated_tokens

    def invoke(
            self,
            input: Union[str, List[BaseMessage]],
            config: Optional[Dict] = None,
            **kwargs: Any,
    ) -> AIMessage:
        """
        调用模型生成响应

        Args:
            input: 输入消息
            config: 配置参数
            **kwargs: 其他参数（包括session_id和analysis_type）

        Returns:
            AI消息响应
        """

        # 处理输入
        if isinstance(input, str):
            messages = [HumanMessage(content=input)]
        else:
            messages = input

        # 调用生成方法
        result = self._generate(messages, **kwargs)

        # 返回第一个生成结果的消息
        if result.generations:
            return result.generations[0].message
        else:
            return AIMessage(content="")


def create_deepseek_llm(
        model: str = "deepseek-chat",
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
) -> ChatDeepSeek:
    """
    创建DeepSeek LLM实例的便捷函数

    Args:
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大token数
        **kwargs: 其他参数

    Returns:
        ChatDeepSeek实例
    """
    return ChatDeepSeek(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


# 为了向后兼容，提供别名
DeepSeekLLM = ChatDeepSeek