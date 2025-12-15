"""
小红书 API 异常定义
"""
from enum import Enum
from typing import NamedTuple, Optional


class ErrorInfo(NamedTuple):
    """错误信息"""
    code: int
    msg: str


class ErrorEnum(Enum):
    """错误枚举"""
    IP_BLOCK = ErrorInfo(-510001, "网络连接异常，请检查网络设置或重启试试")
    SIGN_FAULT = ErrorInfo(-1, "签名错误")
    NOTE_ABNORMAL = ErrorInfo(-510001, "笔记状态异常，无法查看")
    NOTE_SECRETE_FAULT = ErrorInfo(-510001, "当前内容无法展示")


class XhsException(Exception):
    """小红书异常基类"""
    
    def __init__(self, message: str, response=None):
        self.message = message
        self.response = response
        super().__init__(self.message)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(message={self.message!r})"
    
    def __str__(self):
        return self.message


class DataFetchError(XhsException):
    """数据获取错误"""
    
    def __init__(self, data, response=None):
        if isinstance(data, dict):
            message = data.get('msg', str(data))
        else:
            message = str(data)
        super().__init__(message, response)
        self.data = data


class IPBlockError(XhsException):
    """IP被封禁错误"""
    pass


class NeedVerifyError(XhsException):
    """需要验证码错误"""
    
    def __init__(self, message: str, response=None, verify_type: str = None, verify_uuid: str = None):
        super().__init__(message, response)
        self.verify_type = verify_type
        self.verify_uuid = verify_uuid


class SignError(XhsException):
    """签名错误"""
    pass