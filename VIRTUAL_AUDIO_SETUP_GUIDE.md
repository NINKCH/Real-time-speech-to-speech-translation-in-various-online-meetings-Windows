# 🎙️ 虚拟音频设备配置指南

## 问题描述

您在会议中选择了 **CABLE Output (VB-Audio Virtual Cable)** 作为麦克风，但程序没有将翻译后的英文语音推送到这个虚拟麦克风。

## 📊 音频流向原理

```
┌─────────────────────────────────────────────────────────────┐
│                    正确的音频流向                            │
└─────────────────────────────────────────────────────────────┘

您的麦克风 → 程序采集
                ↓
           AST翻译服务（豆包同传2.0）
                ↓
          翻译后的英文语音
                ↓
    程序输出到 → CABLE Input (输出设备)
                ↓
          [VB-Cable 虚拟线缆]
                ↓
         CABLE Output (输入设备) ← 会议软件选择此作为麦克风
                ↓
           会议中的其他人听到
```

## ⚙️ 关键配置

### 1. VB-Cable 设备角色

| 设备名称 | 设备类型 | 用途 | 谁使用 |
|---------|---------|------|--------|
| **CABLE Input** | 输出设备 | 接收程序音频 | **程序输出到这里** |
| **CABLE Output** | 输入设备 | 提供虚拟麦克风 | **会议软件选择此作为麦克风** |

### 2. 当前程序配置

程序默认配置：
- 输出设备：`CABLE Input`（虚拟输出）
- 采样率：24000Hz
- 格式：PCM，单声道

## 🔍 诊断步骤

### 步骤 1：检查 VB-Cable 是否安装

```bash
# 运行诊断工具
python diagnose_audio.py
```

**预期输出**：
```
✅ 找到 CABLE Input (输出设备): [X] CABLE Input (VB-Audio Virtual Cable)
   → 程序应该向这里输出音频

✅ 找到 CABLE Output (输入设备): [Y] CABLE Output (VB-Audio Virtual Cable)
   → 会议软件应该选择这个作为麦克风
```

如果未找到，请：
1. 下载并安装 VB-Audio Virtual Cable
2. 下载地址：https://vb-audio.com/Cable/
3. 安装后重启计算机

### 步骤 2：运行程序并查看日志

```bash
python main.py
```

**启动时应该看到的日志**：

```
============================================================
初始化虚拟音频输出模块
============================================================
目标设备: CABLE Input
采样率: 24000Hz

扫描音频输出设备...
  [0] Speakers (Realtek High Definition Audio)
  [1] CABLE Input (VB-Audio Virtual Cable)
  [2] ...

查找目标设备: CABLE Input
✅ 精确匹配找到设备: [1] CABLE Input (VB-Audio Virtual Cable)

✅ 虚拟音频输出初始化成功: device=[1], rate=24000Hz
============================================================

启动虚拟音频输出流...
目标设备: [1] CABLE Input (VB-Audio Virtual Cable)
✅ 音频输出流已启动
   设备索引: 1
   采样率: 24000Hz
   缓冲区大小: 1024

✅ 虚拟音频输出已启动并准备就绪

💡 音频流向: 程序 → [1] → 虚拟线缆 → CABLE Output → 会议软件
```

### 步骤 3：测试音频输出

当您说话并收到翻译时，应该看到：

```
🔊 输出TTS音频: 19200字节 → 9600样本 (400ms) → 设备[1]
🔊 输出TTS音频: 19200字节 → 9600样本 (400ms) → 设备[1]
...
```

## ❌ 常见问题和解决方案

### 问题 1：未找到 CABLE Input 设备

**症状**：
```
⚠️  未找到虚拟音频设备: CABLE Input
⚠️  将使用默认输出设备
```

**解决方案**：
1. 确认已安装 VB-Cable
2. 在 Windows 声音设置中启用 CABLE Input
3. 重启程序

### 问题 2：找到设备但没有音频输出

**症状**：
- 程序日志显示找到了 CABLE Input
- 但是没有看到 `🔊 输出TTS音频` 的日志
- 会议中听不到翻译

**可能原因**：
1. **模式不是 S2S**：检查主界面，确保选择了 `s2s (语音到语音)` 模式
2. **没有收到翻译结果**：检查原文和译文框是否有内容
3. **虚拟音频输出未启动**：查看启动日志

**解决方案**：
```python
# 在 translator_app.py 中检查
if self.mode == "s2s":
    self.virtual_output = VirtualAudioOutput(sample_rate=24000)
    # 确保这行被执行
```

### 问题 3：有音频输出日志但会议听不到

**症状**：
- 看到 `🔊 输出TTS音频` 日志
- 但会议中其他人听不到

**检查清单**：
1. ✅ 会议软件是否选择了 **CABLE Output** 作为麦克风？
2. ✅ CABLE Output 是否被静音？
3. ✅ 会议软件的麦克风权限是否开启？
4. ✅ Windows 声音设置中 CABLE Output 的音量是否正常？

**测试方法**：
```bash
# 运行测试脚本
python modules/virtual_audio.py

# 应该听到 440Hz 测试音
# 在会议软件中也应该能听到（如果选择了 CABLE Output）
```

### 问题 4：延迟太大

**症状**：
- 音频有明显延迟

**解决方案**：
1. 调整缓冲区大小（在 `virtual_audio.py` 中）
2. 检查网络延迟（翻译本身需要时间）
3. 使用有线连接而不是 WiFi

## 🧪 测试工具

### 1. 诊断音频设备

```bash
python diagnose_audio.py
```

功能：
- 列出所有音频设备
- 检测 VB-Cable 设备
- 测试音频输出到 CABLE Input

### 2. 测试虚拟音频模块

```bash
python modules/virtual_audio.py
```

功能：
- 测试 VirtualAudioOutput 类
- 播放测试音到 CABLE Input
- 验证音频流是否正常

### 3. 完整流程测试

```bash
# 1. 启动程序
python main.py

# 2. 选择 s2s 模式
# 3. 点击"开始翻译"
# 4. 说话并观察日志

# 预期日志：
# ✅ 虚拟音频输出已启动
# 🔊 输出TTS音频: XXX字节 → XXX样本
```

## 📝 配置文件检查

### translator_app.py

确保这些代码存在：

```python
# 在 _init_components 方法中
if self.mode == "s2s":
    self.virtual_output = VirtualAudioOutput(sample_rate=24000)

# 在 _on_tts_audio 方法中
def _on_tts_audio(self, audio_bytes: bytes):
    """TTS音频回调"""
    if self.virtual_output and self.virtual_output.is_running():
        self.virtual_output.play_bytes(audio_bytes, format="pcm")
        logger.debug(f"播放TTS音频: {len(audio_bytes)} 字节")

# 在 _start_async 方法中
if self.virtual_output:
    self.virtual_output.start()
```

### virtual_audio.py

设备配置：

```python
def __init__(self, device_name: str = "CABLE Input", sample_rate: int = 24000):
    # device_name 应该是 "CABLE Input"（不是 CABLE Output）
    # 这是输出设备，程序将音频输出到这里
```

## 🎯 完整配置步骤

### 1. 安装 VB-Cable

1. 访问 https://vb-audio.com/Cable/
2. 下载 VB-CABLE Driver
3. 解压并运行 `VBCABLE_Setup_x64.exe`（以管理员权限）
4. 重启计算机

### 2. Windows 声音设置

**播放设备**：
- 找到 `CABLE Input (VB-Audio Virtual Cable)`
- 右键 → 启用（如果禁用）
- 设置为默认通信设备（可选）

**录制设备**：
- 找到 `CABLE Output (VB-Audio Virtual Cable)`
- 右键 → 启用（如果禁用）
- **不要设为默认设备**（避免干扰正常麦克风）

### 3. 会议软件设置

以腾讯会议/Zoom 为例：

**音频设置**：
- 麦克风：选择 `CABLE Output (VB-Audio Virtual Cable)`
- 扬声器：选择正常的扬声器
- 测试麦克风：运行程序后应该能听到翻译

### 4. 程序设置

**主界面**：
- 源语言：中文（或您说的语言）
- 目标语言：英文（或目标语言）
- 模式：**必须选择 s2s (语音到语音)**
- 点击"开始翻译"

## 🐛 调试技巧

### 增加日志输出

如果需要更详细的调试信息，可以修改：

```python
# 在 translator_app.py 中
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 监控音频队列

```python
# 在 _on_tts_audio 中添加
print(f"队列大小: {self.virtual_output.get_queue_size()}")
```

### 检查音频数据

```python
# 在 _on_tts_audio 中添加
print(f"收到音频: {len(audio_bytes)} 字节")
if len(audio_bytes) == 0:
    print("⚠️ 警告：收到空音频数据")
```

## 📞 获取支持

如果仍然有问题：

1. **运行完整诊断**：
   ```bash
   python diagnose_audio.py > audio_diagnosis.txt
   python main.py 2>&1 | tee program_log.txt
   ```

2. **检查的内容**：
   - VB-Cable 是否正确安装
   - 设备是否被识别
   - 模式是否为 s2s
   - 是否有 TTS 音频输出日志
   - 队列是否有数据

3. **提供信息**：
   - 操作系统版本
   - VB-Cable 版本
   - 程序日志
   - 音频诊断结果

## ✅ 验证清单

在报告问题前，请确认：

- [ ] VB-Cable 已安装并重启
- [ ] Windows 声音设置中能看到 CABLE Input 和 CABLE Output
- [ ] 程序日志显示找到了 CABLE Input 设备
- [ ] 程序日志显示虚拟音频输出已启动
- [ ] 模式选择为 **s2s (语音到语音)**
- [ ] 能看到原文和译文显示
- [ ] 能看到 `🔊 输出TTS音频` 日志
- [ ] 会议软件选择了 **CABLE Output** 作为麦克风
- [ ] 会议软件麦克风未静音
- [ ] 运行过 `diagnose_audio.py` 测试

## 🎉 成功标志

当一切正常工作时，您应该：

1. ✅ 程序启动时看到虚拟音频初始化成功
2. ✅ 说话后看到原文和译文显示
3. ✅ 看到 `🔊 输出TTS音频` 日志
4. ✅ 会议中其他人能听到翻译后的英文
5. ✅ 音质清晰，延迟可接受

---

**祝使用愉快！** 🚀
