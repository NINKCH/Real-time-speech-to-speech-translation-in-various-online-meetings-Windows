# 豆包实时同声传译器

基于豆包同声传译 2.0 API (WebSocket) 的实时语音翻译应用，支持语音到语音(s2s)和语音到文本(s2t)翻译。

## ✨ 核心特性

- **🎯 一体化方案**：使用豆包AST 2.0 API，STT+翻译+TTS一个接口搞定
- **⚡ 超低延迟**：WebSocket流式传输，延迟仅1-2秒
- **🎤 虚拟麦克风**：输出到VB-Cable，可在任何会议软件中使用
- **🌐 多语言支持**：支持中英日韩等多种语言互译
- **🎨 图形界面**：简洁易用的PyQt6界面
- **🔊 音色克隆**：保留说话人原音色特征

## 🎯 使用场景

- 国际会议实时翻译（Zoom、Teams、Google Meet等）
- 在线教育跨语言教学
- 商务洽谈实时沟通
- 直播活动同声传译

## 📋 系统要求

### 软件环境
- **操作系统**: Windows 10/11
- **Python**: 3.12.7
- **Conda环境**: rttdb（推荐）

### 硬件要求
- **最低配置**: 4核CPU, 8GB RAM
- **推荐配置**: 8核CPU, 16GB RAM
- **网络**: 稳定的互联网连接（云端处理）

### 必需软件
- **VB-Audio Virtual Cable**: 虚拟音频驱动
  - 下载地址: https://vb-audio.com/Cable/
  - 用于创建虚拟麦克风设备

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建conda环境
conda create -n rttdb python=3.12.7
conda activate rttdb

# 进入项目目录
cd D:\Code\self_develop\RealtimeASTTranslator

# 安装依赖
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
2. 点击 **"⚙ 设置"** 按钮
3. 填入API密钥:
   - App Key
   - Access Key
4. 点击 **"💾 保存"**

#### 方式2: 手动配置

```bash
# 复制配置模板
copy .env.example .env

# 编辑.env文件，填入你的API密钥
notepad .env
```

**.env 文件内容**:
```
DOUBAO_APP_KEY=your_app_key_here
DOUBAO_ACCESS_KEY=your_access_key_here
DOUBAO_RESOURCE_ID=volc.service_type.10053
```

### 4. 获取API密钥

1. 访问 [火山引擎控制台](https://console.volcengine.com/)
2. 开通 **"同声传译"** 服务
3. 创建应用并获取:
   - **App Key**
   - **Access Key**

### 5. 启动应用

```bash
# 激活环境
conda activate rttdb

# 启动GUI
python main.py
```

## 📖 使用说明

### GUI使用流程

1. **选择语言**: 
   - 源语言: 你说话的语言（如：中文）
   - 目标语言: 翻译后的语言（如：英语）

2. **选择模式**:
   - **s2s (语音到语音)**: 输出语音，可用于会议
   - **s2t (语音到文本)**: 仅输出文本

3. **点击"开始翻译"**: 对着麦克风说话

4. **查看结果**:
   - 左侧显示识别的原文
   - 右侧显示翻译后的文本
   - s2s模式下，翻译语音自动输出到虚拟麦克风

5. **在会议中使用**:
   - 打开会议软件（Zoom/Teams/Google Meet等）
   - 音频设置 → 麦克风 → 选择 **"CABLE Output (VB-Audio Virtual Cable)"**
   - 开始会议，对方听到的是翻译后的语音

### 命令行测试

```bash
# 测试音频采集
python modules/audio_capture.py

# 测试虚拟音频输出
python modules/virtual_audio.py

# 测试AST客户端
python modules/ast_client.py

# 测试完整应用
python translator_app.py
```

## 🔧 项目结构

```
RealtimeASTTranslator/
├── main.py                 # GUI主程序入口
├── translator_app.py       # 翻译应用核心
├── config.py              # 配置文件
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量模板
├── .gitignore            # Git忽略文件
│
├── modules/              # 核心模块
│   ├── ast_client.py     # WebSocket客户端
│   ├── audio_capture.py  # 音频采集
│   └── virtual_audio.py  # 虚拟音频输出
│
├── protos/               # 协议定义
│   ├── ast_service.proto # Protobuf定义
│   └── ast_pb2.py        # Python协议实现
│
├── gui/                  # GUI界面
│   ├── main_window.py    # 主窗口
│   └── settings_dialog.py # 设置对话框
│
├── utils/                # 工具模块
│   └── logger.py         # 日志工具
│
└── logs/                 # 日志目录
```

## 🎤 在线会议配置

### Zoom

1. Settings → Audio
2. Microphone: **CABLE Output (VB-Audio Virtual Cable)**
3. 测试麦克风，确认能听到翻译语音

### Microsoft Teams

1. Settings → Devices
2. Microphone: **CABLE Output (VB-Audio Virtual Cable)**

### Google Meet

1. 浏览器权限设置
2. 麦克风: **CABLE Output (VB-Audio Virtual Cable)**

### 腾讯会议

1. 设置 → 音频
2. 麦克风: **CABLE Output (VB-Audio Virtual Cable)**

## ⚙️ 技术架构

### 核心技术栈

- **WebSocket**: websockets库，实时双向通信
- **音频处理**: sounddevice, numpy
- **GUI**: PyQt6
- **日志**: Python logging
- **配置**: python-dotenv

### 数据流程

```
[麦克风] 
   ↓ (16kHz PCM)
[AudioCapture]
   ↓
[ASTClient (WebSocket)]
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
3. **回调机制**: 通过回调函数更新GUI
4. **线程安全**: 使用pyqtSignal在线程间通信

## ❓ 常见问题

### Q1: 提示"未找到虚拟音频设备"

**A**: 请安装 VB-Audio Virtual Cable 并重启电脑。

### Q2: 会议软件听不到翻译语音

**A**: 
1. 确认选择了 **"CABLE Output"** 而不是 "CABLE Input"
2. 在系统声音设置中测试 CABLE Output 设备
3. 检查应用是否运行在 s2s 模式

### Q3: 连接失败/认证错误

**A**:
1. 检查.env文件中的API密钥是否正确
2. 确认已在火山引擎控制台开通服务
3. 检查网络连接

### Q4: 延迟较高

**A**:
1. 检查网络状况
2. 确认使用的是豆包AST 2.0 API（延迟仅1-2秒）
3. 减少本地网络拥堵

### Q5: 音频断断续续

**A**:
1. 检查CPU占用率
2. 关闭其他占用音频设备的程序
3. 降低音频块大小（config.py中的chunk_duration）

## 📝 版本历史

### v1.0.0 (2025-11-18)
- ✅ 初始版本
- ✅ 豆包AST 2.0 API WebSocket集成
- ✅ 虚拟麦克风输出
- ✅ PyQt6 GUI界面
- ✅ 多语言支持
- ✅ s2s和s2t模式

## 📄 许可证

本项目仅供学习和个人使用。

## 🔗 相关链接

- [豆包API文档](https://console.volcengine.com/)
- [VB-Audio Virtual Cable](https://vb-audio.com/Cable/)
- [PyQt6文档](https://www.riverbankcomputing.com/static/Docs/PyQt6/)

## 👨‍💻 开发说明

### 调试日志

日志文件位置: `logs/translator.log`

查看实时日志:
```bash
tail -f logs/translator.log  # Linux/Mac
Get-Content logs/translator.log -Wait  # Windows PowerShell
```

### 修改配置

编辑 `config.py` 文件可调整:
- 音频采样率
- 音频块大小
- GUI更新频率
- 日志级别

## 🆘 技术支持

如遇问题，请提供:
1. 错误信息截图
2. logs/translator.log 日志文件
3. 系统环境信息
4. 复现步骤

---

**Enjoy real-time translation! 🎉**
