"""
文本 API 客户端
"""
from .openai_client import OpenAITextClient
from .mock_client import MockTextClient

__all__ = ['OpenAITextClient', 'MockTextClient']