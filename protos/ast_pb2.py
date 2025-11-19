"""
豆包同声传译 2.0 API 协议定义
简化版 - 使用字典结构代替完整的protobuf
"""

# 事件类型映射
class EventType:
    # 客户端事件
    StartSession = 100
    UpdateConfig = 201
    TaskRequest = 200
    FinishSession = 102
    
    # 服务端事件
    SessionStarted = 150
    SourceSubtitleStart = 650
    SourceSubtitleResponse = 651
    SourceSubtitleEnd = 652
    TranslationSubtitleStart = 653
    TranslationSubtitleResponse = 654
    TranslationSubtitleEnd = 655
    TTSSentenceStart = 350
    TTSResponse = 352
    TTSSentenceEnd = 351
    UsageResponse = 154
    SessionFinished = 152
    SessionFailed = 153
    AudioMuted = 250


# 事件名称映射
EVENT_NAMES = {
    100: "StartSession",
    201: "UpdateConfig",
    200: "TaskRequest",
    102: "FinishSession",
    150: "SessionStarted",
    650: "SourceSubtitleStart",
    651: "SourceSubtitleResponse",
    652: "SourceSubtitleEnd",
    653: "TranslationSubtitleStart",
    654: "TranslationSubtitleResponse",
    655: "TranslationSubtitleEnd",
    350: "TTSSentenceStart",
    352: "TTSResponse",
    351: "TTSSentenceEnd",
    154: "UsageResponse",
    152: "SessionFinished",
    153: "SessionFailed",
    250: "AudioMuted",
}


def create_start_session_message(
    session_id: str,
    mode: str = "s2s",
    source_language: str = "zh",
    target_language: str = "en",
    source_audio_rate: int = 16000,
    target_audio_format: str = "pcm",
    target_audio_rate: int = 24000,
    hot_words: list = None,
    glossary: dict = None,
    uid: str = "",
    did: str = ""
) -> dict:
    """创建建联请求消息"""
    message = {
        "event": EventType.StartSession,
        "request_meta": {
            "session_id": session_id
        },
        "user": {
            "uid": uid or "default_user",
            "did": did or "default_device",
            "platform": "Windows",
            "sdk_version": "1.0.0"
        },
        "source_audio": {
            "format": "wav",
            "codec": "raw",
            "rate": source_audio_rate,
            "bits": 16,
            "channel": 1
        },
        "target_audio": {
            "format": target_audio_format,
            "rate": target_audio_rate
        },
        "request": {
            "mode": mode,
            "source_language": source_language,
            "target_language": target_language
        }
    }
    
    # 添加语料库（如果有）
    if hot_words or glossary:
        message["request"]["corpus"] = {}
        if hot_words:
            message["request"]["corpus"]["hot_words_list"] = hot_words
        if glossary:
            message["request"]["corpus"]["glossary_list"] = glossary
    
    return message


def create_task_request_message(audio_data: bytes) -> dict:
    """创建音频数据请求消息"""
    return {
        "event": EventType.TaskRequest,
        "source_audio": {
            "data": audio_data
        }
    }


def create_update_config_message(hot_words: list = None, glossary: dict = None) -> dict:
    """创建配置更新消息"""
    message = {
        "event": EventType.UpdateConfig,
        "request": {
            "corpus": {}
        }
    }
    
    if hot_words:
        message["request"]["corpus"]["hot_words_list"] = hot_words
    if glossary:
        message["request"]["corpus"]["glossary_list"] = glossary
    
    return message


def create_finish_session_message() -> dict:
    """创建结束会话消息"""
    return {
        "event": EventType.FinishSession
    }


def get_event_name(event_type: int) -> str:
    """获取事件名称"""
    return EVENT_NAMES.get(event_type, f"Unknown({event_type})")
