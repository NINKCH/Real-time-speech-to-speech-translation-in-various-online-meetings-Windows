# 项目技术总结

## 项目概述

**项目名称**: 豆包实时同声传译器 (Realtime AST Translator)

**技术方案**: 基于豆包同声传译 2.0 API (WebSocket + Protobuf)

**Python环境**: 3.12.7 (Conda环境: rttdb)

## 核心特性

### 一体化API架构

| 对比项 | 传统方案 | 本项目 |
|--------|----------|--------|
| STT | 本地模型 | 云端API |
| 翻译 | HTTP API | WebSocket |
| TTS | Edge TTS | 内置TTS |
| 协议 | 三个独立模块 | 一个WebSocket |
| 延迟 | 2-4秒 | 1-2秒 |
| 音色 | 机器声音 | 原声音复刻 |

### 技术优势

- 超低延迟: WebSocket流式传输
- 零样本声音复刻: 保留说话人音色
- Protobuf协议: 高效二进制序列化
- 简化架构: 一个API完成所有任务

## 项目结构

```
RealtimeASTTranslator/
├── main.py                      # GUI入口
├── translator_app.py            # 应用核心
├── config.py                    # 配置管理
│
├── modules/
│   ├── ast_client_protobuf.py   # WebSocket客户端
│   ├── audio_capture.py         # 音频采集
│   └── virtual_audio.py         # 虚拟音频输出
│
├── gui/
│   ├── main_window.py           # 主窗口
│   ├── settings_dialog.py       # 设置对话框
│   └── voice_clone_test_dialog.py  # 声音复刻验证
│
├── utils/
│   └── logger.py                # 日志工具
│
├── python_protogen/             # Protobuf协议
│
└── logs/                        # 日志目录
```

## 技术栈

### 核心依赖

- **websockets**: WebSocket实时通信
- **sounddevice**: 音频采集和播放
- **numpy**: 音频数据处理
- **PyQt6**: 图形界面
- **protobuf**: 二进制协议序列化
- **python-dotenv**: 环境变量管理

### API接口

- **豆包同声传译 2.0 API**
  - WebSocket URL: `wss://openspeech.bytedance.com/api/v4/ast/v2/translate`
  - 鉴权: Header-based (App Key + Access Key)
  - 模式: s2s, s2t

### 虚拟音频

- **VB-Audio Virtual Cable**
  - CABLE Input: 程序输出
  - CABLE Output: 会议软件输入

## 数据流程

```
[麦克风 16kHz PCM]
    ↓ 80ms/块
[AudioCapture]
    ↓ numpy.ndarray
[ASTClient - Protobuf序列化]
    ↓ WebSocket发送
[豆包AST 2.0 服务器]
    ├→ STT → 原文字幕
    ├→ 翻译 → 译文字幕
    └→ TTS → 24kHz PCM
          ↓
[VirtualAudioOutput]
    ↓
[CABLE Input]
    ↓
[会议软件选择 CABLE Output]
```

## 核心模块

### ast_client_protobuf.py

- WebSocket连接管理
- Protobuf消息序列化/反序列化
- 事件处理（原文/译文/TTS）
- 回调机制

### audio_capture.py

- 16kHz采样率，单声道
- 80ms音频块缓冲
- 独立线程运行

### virtual_audio.py

- 24kHz TTS输出
- VB-Cable设备检测
- 队列缓冲管理

### translator_app.py

- 模块整合
- 异步事件循环
- 回调转发

## 配置说明

### 环境变量 (.env)

```bash
DOUBAO_APP_KEY=xxx
DOUBAO_ACCESS_KEY=xxx
DOUBAO_RESOURCE_ID=volc.service_type.10053
```

### 音频配置 (config.py)

```python
AUDIO_CAPTURE_CONFIG = {
    "sample_rate": 16000,
    "chunk_duration": 0.08,  # 80ms
}

VIRTUAL_AUDIO_CONFIG = {
    "sample_rate": 24000,
    "device_name": "CABLE Input",
}
```

## 性能指标

| 指标 | 数值 |
|------|------|
| 端到端延迟 | 1-2秒 |
| 音频采集延迟 | 80ms |
| 内存占用 | ~200MB |
| CPU占用 | 5-10% |

## 使用场景

1. **国际会议**: Zoom、Teams、Google Meet
2. **在线教育**: 跨语言授课
3. **商务沟通**: 跨国会议
4. **直播活动**: 同声传译

## 已知限制

1. 需要稳定的互联网连接
2. 所有处理在云端，无离线模式
3. 语言支持取决于API

## 开发说明

### 运行测试

```bash
python main.py
```

### 查看日志

```bash
Get-Content logs/translator.log -Wait
```

### 修改配置

编辑 `config.py` 调整：
- 音频采样率
- 音频块大小
- GUI更新频率
- 日志级别

---

**版本**: v1.0.0  
**状态**: 已完成
