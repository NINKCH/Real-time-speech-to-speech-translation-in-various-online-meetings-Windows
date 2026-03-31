import json
import os
from typing import Callable, Optional

_settings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_settings.json")

_current_language = "en"

_callbacks: list[Callable[[str], None]] = []

TRANSLATIONS = {
    "en": {
        "app_title": "Realtime AST Translator",
        "status_ready": "Ready",
        "translation_config": "Translation Config",
        "source_language": "Source:",
        "target_language": "Target:",
        "mode": "Mode:",
        "mode_s2s": "s2s (Speech-to-Speech)",
        "mode_s2t": "s2t (Speech-to-Text)",
        "debug_mode": "Debug",
        "debug_mode_tooltip": "Save audio files to audio_debug directory for debugging",
        "btn_start": "▶ Start",
        "btn_stop": "■ Stop",
        "btn_clear": "Clear",
        "btn_settings": "Settings",
        "btn_info": "Info",
        "btn_voice_clone": "Voice Clone",
        "btn_voice_clone_tooltip": "Test zero-shot voice cloning",
        "btn_info_tooltip": "Learn about zero-shot voice cloning",
        "original_text": "Original",
        "translated_text": "Translation",
        "error_config": "Config Error",
        "error_config_msg": "Please configure DOUBAO_APP_KEY and DOUBAO_ACCESS_KEY in .env file\n\nGet API keys: https://console.volcengine.com/",
        "error_start": "Start Failed",
        "error_start_msg": "Unable to start translation service. Check network and API config.",
        "error": "Error",
        "voice_clone_title": "Zero-Shot Voice Cloning",
        "voice_clone_info": (
            "Doubao AST 2.0 has built-in zero-shot voice cloning!\n\n"
            "Automatically enabled, no setup needed\n"
            "Learns your voice as you speak\n"
            "Uses your voice for translated output\n\n"
            "Steps:\n"
            "1. Make sure mode is s2s (Speech-to-Speech)\n"
            "2. Click Start\n"
            "3. Speak into your microphone\n"
            "4. Hear your own voice in English!\n\n"
            "Want to test it?\n"
            "Click the Voice Clone button!"
        ),
        "btn_view_doc": "View Doc",
        "btn_test_clone": "Test Clone",
        "btn_close": "Close",
        "hint": "Hint",
        "doc_not_found": "Documentation file not found",
        "btn_language": "🌐 English/中文",
        "settings_title": "Settings",
        "api_config_group": "Doubao AST API Config",
        "app_key_placeholder": "Enter App Key",
        "access_key_placeholder": "Enter Access Key",
        "api_help": (
            '<html><body style="font-size: 11px; color: #888;">'
            "Get API keys from "
            '<a href="https://console.volcengine.com/">Volcengine Console</a>'
            "</body></html>"
        ),
        "virtual_audio_group": "Virtual Audio Config",
        "virtual_audio_help": (
            '<html><body style="font-size: 11px; color: #888;">'
            "Install VB-Cable for virtual audio routing. "
            '<a href="https://vb-audio.com/Cable/">Download VB-Cable</a>'
            "</body></html>"
        ),
        "btn_save": "Save",
        "btn_test_connection": "Test Connection",
        "btn_cancel": "Cancel",
        "warning_fill_keys": "Please fill in App Key and Access Key",
        "settings_saved": "Settings saved!\nPlease restart the app.",
        "save_failed": "Save failed: {e}",
        "test_connection_title": "Test Connection",
        "test_connection_msg": (
            "Connection test is under development...\n\n"
            "Please save settings and start translation to test."
        ),
        "voice_clone_tool_title": "Zero-Shot Voice Clone Tool",
        "feature_desc_group": "Feature Description",
        "feature_desc_text": (
            "This tool tests the zero-shot voice cloning feature of Doubao AST.\n\n"
            "It records a short audio sample, then uses it to synthesize speech\n"
            "in the target language with the speaker's voice characteristics.\n\n"
            "Note: This feature is automatically enabled during s2s translation."
        ),
        "clone_text_group": "Clone Text",
        "clone_test_text": "Hello, this is a voice cloning test. The quick brown fox jumps over the lazy dog.",
        "clone_progress_group": "Clone Progress",
        "clone_result_group": "Clone Result",
        "waiting_clone": "Waiting for clone...",
        "btn_play_clone": "▶ Play Audio",
        "btn_save_sample": "Save Sample",
        "btn_start_clone": "Start Clone",
        "btn_stop_clone": "Stop",
        "btn_close_dialog": "Close",
        "config_error": "Config Error",
        "config_error_msg": "Please configure DOUBAO_APP_KEY and DOUBAO_ACCESS_KEY in .env file",
        "cloning": "Cloning...",
        "clone_success": (
            "Clone successful!\n"
            "Audio length: {duration:.2f}s\n"
            "Sample rate: {rate}Hz\n"
            "Click play to listen"
        ),
        "clone_failed": "Clone Failed",
        "no_audio_to_play": "No audio to play",
        "no_audio_to_save": "No audio to save",
        "playing": "Playing cloned audio...",
        "playback_finished": "Playback finished",
        "play_failed": "Play Failed",
        "play_failed_msg": "Unable to play audio: {e}",
        "save_audio_title": "Save Cloned Audio",
        "save_success_title": "Save Successful",
        "save_success_msg": "Cloned audio saved to:\n{path}",
        "save_failed_title": "Save Failed",
        "save_failed_msg": "Unable to save audio: {e}",
        "confirm_close_title": "Confirm Close",
        "confirm_close_msg": "Cloning is in progress. Close anyway?",
        "clone_complete": "Clone complete",
        "lang_zh": "Chinese (zh)",
        "lang_en": "English (en)",
        "lang_ja": "Japanese (ja)",
        "lang_ko": "Korean (ko)",
        "lang_es": "Spanish (es)",
        "lang_fr": "French (fr)",
        "lang_de": "German (de)",
        "lang_ru": "Russian (ru)",
        "lang_ar": "Arabic (ar)",
        "lang_pt": "Portuguese (pt)",
        "lang_it": "Italian (it)",
    },
    "zh": {
        "app_title": "豆包实时同声传译",
        "status_ready": "就绪",
        "translation_config": "翻译配置",
        "source_language": "源语言:",
        "target_language": "目标语言:",
        "mode": "模式:",
        "mode_s2s": "s2s (语音到语音)",
        "mode_s2t": "s2t (语音到文本)",
        "debug_mode": "调试模式",
        "debug_mode_tooltip": "启用后将保存音频文件到audio_debug目录用于调试",
        "btn_start": "▶ 开始翻译",
        "btn_stop": "■ 停止",
        "btn_clear": "🗑 清空",
        "btn_settings": "⚙ 设置",
        "btn_info": "ℹ️ 功能说明",
        "btn_voice_clone": "🔬 声音克隆",
        "btn_voice_clone_tooltip": "测试零样本声音克隆功能",
        "btn_info_tooltip": "了解零样本声音复刻功能",
        "original_text": "原文",
        "translated_text": "译文",
        "error_config": "配置错误",
        "error_config_msg": "请先在.env文件中配置 DOUBAO_APP_KEY 和 DOUBAO_ACCESS_KEY\n\n获取地址：https://console.volcengine.com/",
        "error_start": "启动失败",
        "error_start_msg": "无法启动翻译服务，请检查网络连接和API配置",
        "error": "错误",
        "voice_clone_title": "🎤 零样本声音复刻",
        "voice_clone_info": (
            "豆包同声传译2.0 内置零样本声音复刻功能！\n\n"
            "✨ 自动启用，无需配置\n"
            "✨ 边说话边学习您的音色\n"
            "✨ 翻译时自动使用您的声音\n\n"
            "只需：\n"
            "1. 确保模式选择 s2s (语音到语音)\n"
            "2. 点击开始翻译\n"
            "3. 对着麦克风说话\n"
            "4. 听您自己的声音说英文！\n\n"
            "💡 想测试克隆效果？\n"
            "点击声音克隆按钮进行测试！"
        ),
        "btn_view_doc": "查看文档",
        "btn_test_clone": "测试克隆",
        "btn_close": "关闭",
        "hint": "提示",
        "doc_not_found": "文档文件不存在",
        "btn_language": "🌐 中文/English",
        "settings_title": "设置",
        "api_config_group": "豆包同声传译 API 配置",
        "app_key_placeholder": "请输入 App Key",
        "access_key_placeholder": "请输入 Access Key",
        "api_help": (
            '<html><body style="font-size: 11px; color: #888;">'
            "获取 API 密钥："
            '<a href="https://console.volcengine.com/">火山引擎控制台</a>'
            "</body></html>"
        ),
        "virtual_audio_group": "虚拟音频配置",
        "virtual_audio_help": (
            '<html><body style="font-size: 11px; color: #888;">'
            "安装 VB-Cable 实现虚拟音频路由。"
            '<a href="https://vb-audio.com/Cable/">下载 VB-Cable</a>'
            "</body></html>"
        ),
        "btn_save": "💾 保存",
        "btn_test_connection": "🔧 测试连接",
        "btn_cancel": "取消",
        "warning_fill_keys": "请填写 App Key 和 Access Key",
        "settings_saved": "设置已保存！\n请重启应用使配置生效",
        "save_failed": "保存失败：{e}",
        "test_connection_title": "测试连接",
        "test_connection_msg": "连接测试功能开发中...\n\n请先保存配置，然后启动翻译测试连接",
        "voice_clone_tool_title": "🔬 零样本声音克隆工具",
        "feature_desc_group": "📖 功能说明",
        "feature_desc_text": (
            "此工具用于测试豆包同声传译的零样本声音克隆功能。\n\n"
            "录制一段短音频样本，然后使用该样本\n"
            "合成目标语言的语音，保留说话人的音色特征。\n\n"
            "注意：此功能在 s2s 翻译模式下自动启用。"
        ),
        "clone_text_group": "📝 克隆文本",
        "clone_test_text": "你好，这是一个声音克隆测试。天空是蓝色的，草地是绿色的，今天天气真好。",
        "clone_progress_group": "📊 克隆进度",
        "clone_result_group": "🎵 克隆结果",
        "waiting_clone": "等待克隆...",
        "btn_play_clone": "▶️ 播放克隆音频",
        "btn_save_sample": "💾 保存样本",
        "btn_start_clone": "🚀 开始克隆",
        "btn_stop_clone": "⏹️ 停止",
        "btn_close_dialog": "关闭",
        "config_error": "配置错误",
        "config_error_msg": "请先在.env文件中配置 DOUBAO_APP_KEY 和 DOUBAO_ACCESS_KEY",
        "cloning": "克隆中...",
        "clone_success": (
            "✅ 克隆成功！\n"
            "音频长度: {duration:.2f}秒\n"
            "采样率: {rate}Hz\n"
            "点击播放按钮试听效果"
        ),
        "clone_failed": "克隆失败",
        "no_audio_to_play": "没有可播放的音频",
        "no_audio_to_save": "没有可保存的音频",
        "playing": "▶️ 正在播放克隆音频...",
        "playback_finished": "⏹️ 播放完成",
        "play_failed": "播放失败",
        "play_failed_msg": "无法播放音频: {e}",
        "save_audio_title": "保存克隆音频",
        "save_success_title": "保存成功",
        "save_success_msg": (
            "克隆音频已保存到:\n{path}\n\n"
            "您可以使用任何音频播放器打开此文件，\n"
            "验证是否克隆出了您的声音。"
        ),
        "save_failed_title": "保存失败",
        "save_failed_msg": "无法保存音频: {e}",
        "confirm_close_title": "确认关闭",
        "confirm_close_msg": "克隆正在进行，确定要关闭吗？",
        "clone_complete": "✅ 克隆完成",
        "lang_zh": "中文(zh)",
        "lang_en": "英语(en)",
        "lang_ja": "日语(ja)",
        "lang_ko": "韩语(ko)",
        "lang_es": "西班牙语(es)",
        "lang_fr": "法语(fr)",
        "lang_de": "德语(de)",
        "lang_ru": "俄语(ru)",
        "lang_ar": "阿拉伯语(ar)",
        "lang_pt": "葡萄牙语(pt)",
        "lang_it": "意大利语(it)",
    },
}


def _load_language_from_settings() -> str:
    global _current_language
    try:
        with open(_settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        lang = settings.get("language", "en")
        if lang in TRANSLATIONS:
            _current_language = lang
    except (FileNotFoundError, json.JSONDecodeError):
        _current_language = "en"


def tr(key: str, **kwargs) -> str:
    text = TRANSLATIONS.get(_current_language, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text
    return text


def get_language() -> str:
    return _current_language


def set_language(lang: str) -> None:
    global _current_language
    if lang not in TRANSLATIONS:
        return
    _current_language = lang
    try:
        with open(_settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}
    settings["language"] = lang
    try:
        with open(_settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except OSError:
        pass
    for cb in _callbacks:
        try:
            cb(lang)
        except Exception:
            pass


def on_language_changed(callback: Callable[[str], None]) -> None:
    _callbacks.append(callback)


def get_language_names() -> list[tuple[str, str]]:
    return [("en", "English"), ("zh", "中文")]


def get_translated_languages() -> list[str]:
    if _current_language == "en":
        return [
            "Chinese (zh)", "English (en)", "Japanese (ja)", "Korean (ko)",
            "Spanish (es)", "French (fr)", "German (de)", "Russian (ru)",
            "Arabic (ar)", "Portuguese (pt)", "Italian (it)",
        ]
    return [
        "中文(zh)", "英语(en)", "日语(ja)", "韩语(ko)",
        "西班牙语(es)", "法语(fr)", "德语(de)", "俄语(ru)",
        "阿拉伯语(ar)", "葡萄牙语(pt)", "意大利语(it)",
    ]


_load_language_from_settings()
