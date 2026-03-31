# 豆包实时同声传译器

[English](README.md) | 简体中文

基于豆包同声传译 2.0 API (WebSocket) 的实时语音翻译应用，支持语音到语音(s2s)和语音到文本(s2t)翻译。

## 核心特性

- **一体化方案**：使用豆包AST 2.0 API，STT+翻译+TTS一个接口搞定
- **超低延迟**：WebSocket流式传输，延迟仅1-2秒
- **虚拟麦克风**：输出到VB-Cable，可在任何会议软件中使用
- **多语言支持**：支持中英日韩等多种语言互译
- **图形界面**：简洁易用的PyQt6界面
- **音色克隆**：零样本声音复刻，保留说话人原音色特征

## 使用场景

- 国际会议实时翻译（Zoom、Teams、Google Meet、腾讯会议等）
- 在线教育跨语言教学
- 商务洽谈实时沟通
- 直播活动同声传译

## 系统要求

### 软件环境
- 操作系统: Windows 10/11
- Python: 3.12.7
- Conda环境: rttdb（推荐）

### 硬件要求
- 最低配置: 4核CPU, 8GB RAM
- 推荐配置: 8核CPU, 16GB RAM
- 网络: 稳定的互联网连接

### 必需软件
- **VB-Audio Virtual Cable**: 虚拟音频驱动
  - 下载地址: https://vb-audio.com/Cable/

## 快速开始

### 1. 环境准备

```bash
conda create -n rttdb python=3.12.7
conda activate rttdb
pip install -r requirements.txt
```

### 2. 安装虚拟音频驱动

1. 下载 VB-Audio Virtual Cable: https://vb-audio.com/Cable/
2. 以管理员身份运行安装程序
3. 重启电脑
4. 在"声音设置"中应该能看到 "CABLE Input" 和 "CABLE Output"

### 3. 配置API密钥

#### 方式1: 通过GUI配置（推荐）

1. 启动程序: `python main.py`
2. 点击 **"设置"** 按钮
3. 填入API密钥（App Key、Access Key）
4. 点击 **"保存"**

#### 方式2: 手动配置

创建 `.env` 文件:
```
DOUBAO_APP_KEY=your_app_key_here
DOUBAO_ACCESS_KEY=your_access_key_here
DOUBAO_RESOURCE_ID=volc.service_type.10053
```

#### 获取API密钥

1. 访问 [火山引擎控制台](https://console.volcengine.com/)
2. 开通 **"同声传译"** 服务
3. 创建应用并获取 App Key 和 Access Key

### 4. 启动应用

```bash
conda activate rttdb
python main.py
```

## 使用说明

### 界面语言

应用支持中英文界面切换。点击主窗口的 **🌐 中文/English** 按钮即可切换语言，设置会自动保存。

### GUI操作流程

1. **选择语言**: 源语言（你说话的语言）和目标语言（翻译后的语言）
2. **选择模式**:
   - **s2s (语音到语音)**: 输出语音，可用于会议（推荐）
   - **s2t (语音到文本)**: 仅输出文本
3. **点击"开始翻译"**: 对着麦克风说话
4. **查看结果**: 左侧显示原文，右侧显示译文
5. **在会议中使用**: 会议软件麦克风选择 **"CABLE Output"**

### 零样本声音复刻

S2S模式自动启用零样本声音复刻功能：

- **零配置**: 不需要提前训练
- **零等待**: 不需要Speaker ID
- **零样本**: 边说话边学习音色
- **实时复刻**: 自动应用到翻译输出

工作原理：
```
你说中文 → 系统实时学习你的音色 → 翻译 → 用你的声音说英文
```

### 验证声音复刻效果

1. 点击主界面的 **"验证复刻"** 按钮
2. 点击 **"开始测试"**
3. 朗读测试文本（约10秒）
4. 点击 **"播放复刻音频"** 听取效果
5. 可选择 **"保存样本"** 保存音频

## 在线会议配置

### 关键配置原则

1. **Windows输入设备**: 保持真实麦克风（不要选CABLE Output）
2. **程序**: 自动采集真实麦克风，输出到CABLE Input
3. **会议软件**: 麦克风选择 CABLE Output

### 音频流向

```
[真实麦克风] → [程序采集翻译] → [CABLE Input] → [VB-Cable] → [CABLE Output] → [会议软件]
```

### 各平台配置

**Zoom**: Settings → Audio → Microphone: **CABLE Output**

**Microsoft Teams**: Settings → Devices → Microphone: **CABLE Output**

**Google Meet**: 设置 → 音频 → 麦克风: **CABLE Output**

**腾讯会议**: 设置 → 音频 → 麦克风: **CABLE Output**

## 项目结构

```
RealtimeASTTranslator/
├── main.py                 # GUI主程序入口
├── translator_app.py       # 翻译应用核心
├── config.py              # 配置文件
├── requirements.txt       # Python依赖
│
├── modules/              # 核心模块
│   ├── ast_client_protobuf.py  # WebSocket客户端（Protobuf）
│   ├── audio_capture.py        # 音频采集
│   └── virtual_audio.py        # 虚拟音频输出
│
├── gui/                  # GUI界面
│   ├── main_window.py          # 主窗口
│   ├── settings_dialog.py      # 设置对话框
│   └── voice_clone_test_dialog.py  # 声音复刻验证
│
├── utils/                # 工具模块
│   └── logger.py               # 日志工具
│
├── python_protogen/      # Protobuf协议定义
│
├── logs/                 # 日志目录
│
├── README.md             # 英文文档
├── README_CN.md          # 本文档（中文）
├── QUICK_START.md        # 快速开始
├── PROJECT_SUMMARY.md    # 项目总结
└── TROUBLESHOOTING.md    # 故障排除
```

## 技术架构

### 核心技术栈

- **WebSocket**: websockets库，实时双向通信
- **音频处理**: sounddevice, numpy
- **GUI**: PyQt6
- **协议**: Protobuf
- **配置**: python-dotenv

### 数据流程

```
[麦克风 16kHz PCM]
    ↓
[AudioCapture]
    ↓
[ASTClient (WebSocket + Protobuf)]
    ↓
[豆包AST 2.0 API服务器]
    ├→ STT识别 → 原文字幕
    ├→ 实时翻译 → 译文字幕
    └→ TTS合成 → 音频流 (24kHz PCM)
          ↓
[VirtualAudioOutput]
    ↓
[VB-Cable Input]
    ↓
[会议软件选择 CABLE Output]
```

### 关键特性

1. **异步处理**: asyncio事件循环处理WebSocket通信
2. **流式传输**: 80ms音频块实时发送，降低延迟
3. **Protobuf协议**: 高效的二进制序列化
4. **零样本声音复刻**: 实时音色学习和应用

## 常见问题

### Q1: 提示"未找到虚拟音频设备"

安装 VB-Audio Virtual Cable 并重启电脑。

### Q2: 会议软件听不到翻译语音

1. 确认选择了 **"CABLE Output"** 而不是 "CABLE Input"
2. 在系统声音设置中测试 CABLE Output 设备
3. 检查应用是否运行在 s2s 模式

### Q3: 连接失败/认证错误

1. 检查.env文件中的API密钥是否正确
2. 确认已在火山引擎控制台开通服务
3. 检查网络连接

### Q4: Windows默认输入设备应该选什么？

**保持真实麦克风**，不要选CABLE Output。详见 TROUBLESHOOTING.md。

### Q5: 延迟较高

1. 检查网络状况
2. 确认使用的是豆包AST 2.0 API（延迟仅1-2秒）

### Q6: 音频断断续续

1. 检查CPU占用率
2. 关闭其他占用音频设备的程序

## 性能指标

| 指标 | 数值 |
|------|------|
| 端到端延迟 | 1-2秒 |
| 音频采集延迟 | 80ms |
| 网络传输延迟 | 500-800ms |
| TTS合成延迟 | 300-500ms |
| 内存占用 | ~200MB |
| CPU占用 | 5-10% (4核) |

## 支持的语言

- zh - 中文
- en - 英语
- ja - 日语
- ko - 韩语
- es - 西班牙语
- fr - 法语
- de - 德语
- ru - 俄语
- ar - 阿拉伯语

## 调试与日志

日志文件位置: `logs/translator.log`

查看实时日志:
```bash
Get-Content logs/translator.log -Wait  # Windows PowerShell
```

修改配置: 编辑 `config.py`

## 版本历史

### v1.0.0 (2025-11-18)
- 豆包AST 2.0 API WebSocket集成
- Protobuf协议支持
- 虚拟麦克风输出
- PyQt6 GUI界面
- 多语言支持
- 零样本声音复刻
- s2s和s2t模式

## 许可证

本项目仅供学习和个人使用。

## 相关链接

- [豆包API文档](https://console.volcengine.com/)
- [VB-Audio Virtual Cable](https://vb-audio.com/Cable/)
- [PyQt6文档](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
