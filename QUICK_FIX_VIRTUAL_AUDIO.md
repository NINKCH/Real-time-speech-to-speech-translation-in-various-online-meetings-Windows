# 🚑 虚拟音频快速故障排除

## 问题：会议软件听不到翻译的声音

### 🎯 5分钟快速检查

#### 1️⃣ 运行诊断（30秒）

```bash
cd D:\Code\self_develop\RealtimeASTTranslator
python diagnose_audio.py
```

**看什么**：
- ✅ 必须看到：`✅ 找到 CABLE Input (输出设备)`
- ✅ 必须看到：`✅ 找到 CABLE Output (输入设备)`
- ❌ 如果看到：`❌ 未找到 CABLE Input` → **去步骤 5 安装 VB-Cable**

#### 2️⃣ 检查模式（10秒）

启动程序，看主界面：

```
翻译模式: [s2s (语音到语音)] ← 必须是这个！
```

❌ 如果是 `s2t (语音到文字)` → **切换到 s2s 模式**

#### 3️⃣ 检查程序日志（1分钟）

点击"开始翻译"后，看控制台：

**必须看到这些**：
```
✅ 虚拟音频输出初始化成功: device=[X]
✅ 音频输出流已启动
✅ 虚拟音频输出已启动并准备就绪
```

❌ 如果看到：
```
⚠️  未找到虚拟音频设备
⚠️  将使用默认输出设备
```
→ **去步骤 5**

#### 4️⃣ 检查音频输出（1分钟）

说话后，看控制台：

**必须看到**：
```
🔊 输出TTS音频: 19200字节 → 9600样本 (400ms) → 设备[1]
```

❌ 如果没有看到 → **问题在程序端**，检查：
- 是否有原文和译文显示？
- 模式是否真的是 s2s？

✅ 如果看到了 → **问题在会议软件端**，去步骤 6

#### 5️⃣ 安装 VB-Cable（5分钟）

1. 下载：https://vb-audio.com/Cable/
2. 解压后右键 `VBCABLE_Setup_x64.exe` → 以管理员运行
3. 安装完成后 **重启电脑**
4. 重新运行诊断：`python diagnose_audio.py`

#### 6️⃣ 配置会议软件（1分钟）

**关键：选择正确的麦克风**

```
会议软件音频设置：
┌──────────────────────────────┐
│ 麦克风：CABLE Output ←← 这个！│
│ 扬声器：[正常的扬声器]        │
└──────────────────────────────┘
```

**常见错误**：
❌ 选择了 `CABLE Input` → 错误！这是输出设备
✅ 必须选择 `CABLE Output` → 正确！这是输入设备

---

## 🔍 详细故障诊断树

```
会议软件听不到声音
    │
    ├─→ 运行 diagnose_audio.py
    │       │
    │       ├─→ 未找到 CABLE 设备
    │       │       └─→ 安装 VB-Cable + 重启
    │       │
    │       └─→ 找到 CABLE 设备
    │               └─→ 继续下一步
    │
    ├─→ 检查程序日志
    │       │
    │       ├─→ 未看到"虚拟音频输出已启动"
    │       │       ├─→ 检查模式是否为 s2s
    │       │       └─→ 重启程序
    │       │
    │       └─→ 看到"虚拟音频输出已启动"
    │               └─→ 继续下一步
    │
    ├─→ 说话测试
    │       │
    │       ├─→ 没有原文和译文
    │       │       └─→ 检查麦克风和网络
    │       │
    │       ├─→ 有原文译文，但没有🔊日志
    │       │       ├─→ 确认模式是 s2s
    │       │       └─→ 检查 _on_tts_audio 代码
    │       │
    │       └─→ 有🔊日志
    │               └─→ 继续下一步
    │
    └─→ 检查会议软件
            │
            ├─→ 麦克风选错了
            │       └─→ 改为 CABLE Output
            │
            ├─→ 麦克风静音了
            │       └─→ 取消静音
            │
            └─→ Windows音量太低
                    └─→ 调高音量
```

---

## 💉 常见问题速查

### Q1: 找不到 CABLE Input 设备

**症状**：
```
⚠️  未找到虚拟音频设备: CABLE Input
```

**解决**：
```bash
# 1. 检查是否安装
# Windows 设置 → 系统 → 声音 → 高级声音选项
# 应该能看到 CABLE Input 和 CABLE Output

# 2. 如果没有，安装 VB-Cable
https://vb-audio.com/Cable/

# 3. 安装后重启电脑

# 4. 验证
python diagnose_audio.py
```

---

### Q2: 有原文译文，但没有🔊日志

**症状**：
- GUI显示原文："你好..."
- GUI显示译文："Hello..."
- 但是没有看到：`🔊 输出TTS音频`

**原因**：模式不是 s2s，或者虚拟音频输出未启动

**解决**：
```python
# 1. 检查主界面模式
翻译模式: [s2s (语音到语音)]  ← 必须是这个

# 2. 重启程序，看初始化日志
✅ 虚拟音频输出初始化成功: device=[1]

# 3. 如果还是没有，检查代码
# translator_app.py 的 _on_tts_audio 方法
def _on_tts_audio(self, audio_bytes: bytes):
    if self.virtual_output and self.virtual_output.is_running():
        self.virtual_output.play_bytes(audio_bytes, format="pcm")
```

---

### Q3: 有🔊日志，但会议听不到

**症状**：
```
🔊 输出TTS音频: 19200字节 → 9600样本 (400ms) → 设备[1]
```
但是会议中听不到

**检查清单**：
```
□ 会议软件麦克风选择了 CABLE Output？
□ 会议软件麦克风没有静音？
□ Windows 音量设置中 CABLE Output 音量正常？
□ 会议软件有麦克风权限？
```

**测试方法**：
```bash
# 1. 运行测试程序
python modules/virtual_audio.py

# 2. 应该听到 440Hz 测试音
# 3. 如果在会议中也能听到，说明配置正确
# 4. 如果听不到，检查会议软件麦克风设置
```

---

### Q4: 延迟太大

**症状**：说话后很久才听到翻译

**原因**：
1. 网络延迟（翻译本身需要时间）
2. 音频缓冲区太大
3. VB-Cable缓冲设置

**解决**：
```python
# 1. 调整缓冲区大小（在 virtual_audio.py）
self.buffer_size = 512  # 默认是 1024，可以改小

# 2. 使用有线网络

# 3. 调整 VB-Cable 缓冲
# Control Panel → VB-Audio Virtual Cable → 缓冲区设置
```

---

### Q5: 音质不好

**症状**：音频断断续续或有杂音

**原因**：
1. 网络不稳定
2. CPU占用过高
3. 音频设备驱动问题

**解决**：
```bash
# 1. 检查网络
ping www.volcengine.com

# 2. 检查CPU占用
# 任务管理器 → 性能

# 3. 更新音频驱动

# 4. 降低音质要求（如果API支持）
target_audio_rate = 16000  # 从 24000 降到 16000
```

---

## 🧪 测试命令合集

```bash
# 完整诊断流程
cd D:\Code\self_develop\RealtimeASTTranslator

# 1. 音频设备诊断
python diagnose_audio.py

# 2. 虚拟音频模块测试
python modules/virtual_audio.py

# 3. 启动程序（观察日志）
python main.py

# 4. 检查环境
conda activate rttdb
pip list | grep sounddevice

# 5. 列出音频设备
python -c "import sounddevice; print(sounddevice.query_devices())"
```

---

## 📋 配置检查脚本

创建 `check_config.py`：

```python
import sounddevice as sd

print("\n=== 音频设备检查 ===\n")

devices = sd.query_devices()
cable_input_found = False
cable_output_found = False

for i, device in enumerate(devices):
    if 'cable input' in device['name'].lower() and device['max_output_channels'] > 0:
        print(f"✅ CABLE Input: [{i}] {device['name']}")
        cable_input_found = True
    if 'cable output' in device['name'].lower() and device['max_input_channels'] > 0:
        print(f"✅ CABLE Output: [{i}] {device['name']}")
        cable_output_found = True

if cable_input_found and cable_output_found:
    print("\n🎉 VB-Cable 配置正确！")
    print("\n下一步：")
    print("1. 启动程序: python main.py")
    print("2. 选择 s2s 模式")
    print("3. 会议软件选择 CABLE Output 作为麦克风")
else:
    print("\n❌ VB-Cable 配置有问题！")
    if not cable_input_found:
        print("  - 未找到 CABLE Input")
    if not cable_output_found:
        print("  - 未找到 CABLE Output")
    print("\n请安装 VB-Cable: https://vb-audio.com/Cable/")
```

运行：
```bash
python check_config.py
```

---

## 📞 需要帮助？

提供这些信息：

```bash
# 1. 系统信息
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# 2. 音频设备列表
python -c "import sounddevice; print(sounddevice.query_devices())"

# 3. 程序日志
python main.py > log.txt 2>&1

# 4. 诊断结果
python diagnose_audio.py > diagnosis.txt
```

然后提供：
- `log.txt`
- `diagnosis.txt`
- 会议软件截图（麦克风设置）

---

**快速记忆口诀** 🎵

```
程序输出到 Input，
会议选择用 Output。
s2s 模式必须选，
看到🔊才算通。
```
