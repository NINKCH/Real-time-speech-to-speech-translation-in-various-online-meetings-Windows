"""
配置文件
豆包同声传译 2.0 API 实时翻译器
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目路径
PROJECT_ROOT = Path(__file__).parent
LOGS_DIR = PROJECT_ROOT / "logs"
PROTOS_DIR = PROJECT_ROOT / "protos"

# 确保目录存在
LOGS_DIR.mkdir(exist_ok=True)
PROTOS_DIR.mkdir(exist_ok=True)

# ==================== API配置 ====================

# 豆包同声传译 2.0 API
AST_CONFIG = {
    "app_key": os.getenv("DOUBAO_APP_KEY", ""),
    "access_key": os.getenv("DOUBAO_ACCESS_KEY", ""),
    "resource_id": os.getenv("DOUBAO_RESOURCE_ID", "volc.service_type.10053"),
    
    # WebSocket URL
    "ws_url": "wss://openspeech.bytedance.com/api/v4/ast/v2/translate",
    
    # 翻译配置
    "mode": "s2s",  # s2s (语音到语音) 或 s2t (语音到文本)
    "source_language": "zh",  # 源语言
    "target_language": "en",  # 目标语言
    
    # 音频配置
    "source_audio_rate": 16000,  # 输入音频采样率
    "target_audio_rate": 24000,  # TTS输出采样率
    "target_audio_format": "pcm",  # pcm 或 ogg_opus
}

# ==================== 音频配置 ====================

# 音频采集配置
AUDIO_CAPTURE_CONFIG = {
    "sample_rate": 16000,  # 采样率（必须与AST_CONFIG一致）
    "chunk_duration": 0.08,  # 音频块时长（秒），建议80ms
    "device_index": None,  # 设备索引（None=默认设备）
}

# 虚拟音频输出配置
VIRTUAL_AUDIO_CONFIG = {
    "device_name": "CABLE Input",  # VB-Cable虚拟设备名
    "sample_rate": 24000,  # 采样率（必须与AST_CONFIG一致）
    "auto_detect": True,  # 自动检测虚拟设备
}

# ==================== GUI配置 ====================

GUI_CONFIG = {
    "window_title": "豆包实时同声传译 - Realtime AST Translator",
    "window_size": (900, 700),
    "font_family": "Segoe UI",
    "font_size": 10,
    "update_interval_ms": 100,  # GUI更新间隔
}

# ==================== 日志配置 ====================

LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "file": LOGS_DIR / "translator.log",
    "console_output": True,
}

# ==================== 语言选项 ====================

LANGUAGES = {
    "zh": "中文",
    "en": "英语",
    "ja": "日语",
    "ko": "韩语",
    "es": "西班牙语",
    "fr": "法语",
    "de": "德语",
    "ru": "俄语",
    "ar": "阿拉伯语",
    "pt": "葡萄牙语",
    "it": "意大利语",
}

# ==================== 验证配置 ====================

def validate_config() -> tuple:
    """
    验证配置
    
    Returns:
        (errors, warnings) 错误和警告列表
    """
    errors = []
    warnings = []
    
    # 检查API密钥
    if not AST_CONFIG["app_key"]:
        errors.append("豆包 APP_KEY 未配置")
    if not AST_CONFIG["access_key"]:
        errors.append("豆包 ACCESS_KEY 未配置")
    
    # 检查采样率一致性
    if AUDIO_CAPTURE_CONFIG["sample_rate"] != AST_CONFIG["source_audio_rate"]:
        errors.append("音频采集采样率与API配置不一致")
    
    if VIRTUAL_AUDIO_CONFIG["sample_rate"] != AST_CONFIG["target_audio_rate"]:
        errors.append("虚拟音频采样率与API配置不一致")
    
    # 检查模式
    if AST_CONFIG["mode"] not in ["s2s", "s2t"]:
        errors.append(f"无效的模式: {AST_CONFIG['mode']}")
    
    # 检查语言
    if AST_CONFIG["source_language"] not in LANGUAGES:
        warnings.append(f"未知的源语言: {AST_CONFIG['source_language']}")
    if AST_CONFIG["target_language"] not in LANGUAGES:
        warnings.append(f"未知的目标语言: {AST_CONFIG['target_language']}")
    
    if AST_CONFIG["source_language"] == AST_CONFIG["target_language"]:
        warnings.append("源语言和目标语言相同")
    
    return errors, warnings


def print_config_summary():
    """打印配置摘要"""
    print("=" * 60)
    print("配置摘要 - Configuration Summary")
    print("=" * 60)
    print(f"模式: {AST_CONFIG['mode']}")
    print(f"翻译方向: {AST_CONFIG['source_language']} -> {AST_CONFIG['target_language']}")
    print(f"输入采样率: {AUDIO_CAPTURE_CONFIG['sample_rate']}Hz")
    print(f"输出采样率: {VIRTUAL_AUDIO_CONFIG['sample_rate']}Hz")
    print(f"虚拟设备: {VIRTUAL_AUDIO_CONFIG['device_name']}")
    print("=" * 60)


if __name__ == "__main__":
    # 验证配置
    errors, warnings = validate_config()
    
    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("⚠️ 配置警告:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors:
        print("✅ 配置验证通过")
        print_config_summary()
