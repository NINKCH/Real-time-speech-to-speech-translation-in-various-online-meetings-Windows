# 🔍 排查清单：虚拟麦克风没有录入英文语音

## 问题：CABLE Output（虚拟麦克风）没有接收到翻译后的英文语音

---

## 🎯 排查流程

### 第1步：检查程序是否输出音频（30秒）

**检查日志**：

启动翻译程序后，说话测试，观察控制台：

```
应该看到：
🔊 输出TTS音频: 38936字节 → 19468样本 (811ms) → 设备[5]
🔊 输出TTS音频: 38412字节 → 19206样本 (800ms) → 设备[5]
```

**结果判断**：

✅ **有🔊日志**：
- 程序正在输出音频
- 继续下一步

❌ **没有🔊日志**：
- 程序没有输出音频
- 问题在程序端
- 检查：
  - 模式是否为 `s2s`（不是 `s2t`）
  - 是否有译文显示
  - 是否有错误日志

---

### 第2步：检查输出设备索引（1分钟）

**运行诊断**：

```bash
python diagnose_full_chain.py
```

**检查点**：

```
程序输出到设备[5]
CABLE Input 是设备[X]
```

✅ **索引相同**（5 == 5）：
- 设备正确
- 继续下一步

❌ **索引不同**（5 != X）：
- **问题找到了！**
- 程序输出到错误的设备
- 解决方案：
  ```bash
  # 关闭程序
  # 重新运行
  python main.py
  ```

---

### 第3步：测试CABLE链路（2分钟）

**运行完整测试**：

```bash
python diagnose_full_chain.py
```

按照提示进行回环测试。

**结果判断**：

✅ **回环测试成功**（录到了测试音）：
- CABLE链路正常
- 问题在会议软件或程序TTS
- 跳到第4步

❌ **回环测试失败**（没录到测试音）：
- CABLE链路故障
- 解决方案：
  1. **重启电脑**（最有效）
  2. 检查Windows音量设置
  3. 重新安装VB-Cable

---

### 第4步：检查会议软件配置（1分钟）

**打开会议软件音频设置**：

检查点：

```
□ 麦克风选择：CABLE Output (VB-Audio Virtual Cable)
□ 麦克风未静音
□ 点击"测试麦克风"有音量指示
```

**测试方法**：

1. 保持会议软件的麦克风测试界面打开
2. 运行：
   ```bash
   python test_cable_audio.py
   ```
3. 播放测试音
4. 观察会议软件的麦克风音量条是否跳动

✅ **音量条跳动**：
- 会议软件能接收CABLE音频
- 但可能接收不到程序的TTS音频
- 跳到第5步

❌ **音量条不跳动**：
- 会议软件配置有问题
- 检查：
  - 麦克风真的选对了吗？
  - 会议软件是否有麦克风权限？
  - 尝试重启会议软件

---

### 第5步：检查程序TTS音频质量（2分钟）

**对比测试**：

1. **测试A**：播放测试音
   ```bash
   python test_cable_audio.py
   ```
   会议对方能听到？→ Yes

2. **测试B**：运行程序翻译
   ```bash
   python main.py
   # 开始翻译，说话
   ```
   会议对方能听到？→ No

**结论**：

如果测试A能听到，测试B听不到：
- CABLE链路正常
- 测试音能传输
- **问题在程序的TTS音频数据**

可能原因：
- TTS音频太小声
- 音频格式有问题
- 音频数据异常

---

## 🛠️ 常见问题和解决方案

### 问题1：没有🔊输出日志

**症状**：
```
有原文译文显示
但没有 🔊 输出TTS音频
```

**原因**：模式不是s2s

**解决**：
1. 停止翻译
2. 选择模式：`s2s (语音到语音)`
3. 重新开始翻译

---

### 问题2：设备索引不匹配

**症状**：
```
程序输出到设备[5]
但 CABLE Input 是设备[3]
```

**原因**：音频设备列表变化

**解决**：
```bash
# 重启程序
python main.py
```

---

### 问题3：回环测试失败

**症状**：
```
播放测试音到 CABLE Input
但从 CABLE Output 录不到
```

**原因**：VB-Cable驱动问题

**解决**（按顺序尝试）：
1. **重启电脑**（最有效，90%能解决）
2. 检查Windows音量：
   ```
   Windows设置 → 声音
   → 输出 → CABLE Input → 音量不为0
   → 输入 → CABLE Output → 音量不为0
   ```
3. 重新安装VB-Cable

---

### 问题4：测试音能听到，程序翻译听不到

**症状**：
```
test_cable_audio.py 播放的测试音 → 会议能听到 ✅
程序翻译的英文 → 会议听不到 ❌
```

**原因**：程序TTS音频问题

**检查**：
1. 日志中是否持续有🔊输出？
2. 音频字节数是否正常（>1000）？
3. 设备索引是否正确？

**解决**：
```python
# 检查 translator_app.py 中的 _on_tts_audio 方法
def _on_tts_audio(self, audio_bytes: bytes):
    if self.virtual_output and self.virtual_output.is_running():
        # 添加调试
        print(f"DEBUG: 收到TTS音频 {len(audio_bytes)} 字节")
        self.virtual_output.play_bytes(audio_bytes, format="pcm")
```

---

### 问题5：会议软件麦克风测试没有音量指示

**症状**：
```
会议软件选择了 CABLE Output
点击"测试麦克风"
播放 test_cable_audio.py
但没有音量指示
```

**原因**：会议软件权限或配置问题

**解决**：
1. **检查麦克风权限**：
   ```
   Windows设置 → 隐私 → 麦克风
   确保会议软件有权限
   ```

2. **重启会议软件**

3. **重新选择麦克风**：
   - 先选择其他麦克风
   - 再选回 CABLE Output

---

## 📊 完整排查矩阵

| 症状 | 可能原因 | 排查工具 | 解决方案 |
|------|---------|---------|---------|
| 没有🔊日志 | 模式不是s2s | 查看界面 | 切换到s2s模式 |
| 设备[5]不是CABLE | 设备索引变化 | `diagnose_full_chain.py` | 重启程序 |
| 回环测试失败 | VB-Cable故障 | `diagnose_full_chain.py` | 重启电脑 |
| 测试音能听到，翻译听不到 | TTS音频问题 | 对比测试 | 检查日志和代码 |
| 会议软件无音量指示 | 会议软件配置 | `test_cable_audio.py` | 检查权限和设置 |

---

## 🚀 快速诊断命令

```bash
# 1. 完整链路诊断（最全面）
python diagnose_full_chain.py

# 2. 测试CABLE音频
python test_cable_audio.py

# 3. 快速诊断
python quick_diagnose.py

# 4. 检查设备配置
python check_virtual_audio.py
```

---

## 💡 调试技巧

### 增加程序调试日志

编辑 `translator_app.py`：

```python
def _on_tts_audio(self, audio_bytes: bytes):
    """TTS音频回调"""
    print(f"DEBUG: 收到TTS音频")
    print(f"  - 字节数: {len(audio_bytes)}")
    print(f"  - 虚拟输出运行: {self.virtual_output.is_running() if self.virtual_output else 'None'}")
    
    if self.virtual_output and self.virtual_output.is_running():
        self.virtual_output.play_bytes(audio_bytes, format="pcm")
        print(f"  - 已发送到虚拟输出")
    else:
        print(f"  - ⚠️ 虚拟输出未运行！")
```

### 监控CABLE Output

同时运行两个终端：

**终端1**（运行程序）：
```bash
python main.py
```

**终端2**（监控CABLE Output）：
```bash
# 持续从CABLE Output录音并显示音量
python -c "
import sounddevice as sd
import numpy as np
import time

# 找到CABLE Output
devices = sd.query_devices()
cable_output = None
for i, d in enumerate(devices):
    if 'cable output' in d['name'].lower() and d['max_input_channels'] > 0:
        cable_output = i
        break

if cable_output is None:
    print('未找到CABLE Output')
    exit()

print(f'监控设备[{cable_output}]...')
print('按Ctrl+C停止')

def callback(indata, frames, time, status):
    volume = np.linalg.norm(indata) * 10
    print(f'音量: {\"█\" * int(volume):50}', end='\r')

with sd.InputStream(device=cable_output, callback=callback):
    while True:
        time.sleep(0.1)
"
```

这样可以实时看到CABLE Output是否有音频数据。

---

## 🎯 最终检查清单

运行程序前：

```
□ VB-Cable已安装
□ Windows输入设备是真实麦克风（不是CABLE Output）
□ 模式选择为 s2s
```

运行程序后：

```
□ 日志显示"虚拟音频输出初始化成功"
□ 说话时有原文和译文显示
□ 持续看到🔊输出日志
□ 设备索引正确（与CABLE Input匹配）
```

会议软件配置：

```
□ 麦克风选择 CABLE Output
□ 麦克风未静音
□ 有麦克风权限
□ 测试麦克风有音量指示
```

---

## 🆘 如果以上都不行

**终极解决方案**：

1. **完全重置**：
   ```bash
   # 1. 停止所有程序
   # 2. 重启电脑
   # 3. 重新运行
   python main.py
   ```

2. **重新安装VB-Cable**：
   - 卸载现有VB-Cable
   - 重启电脑
   - 重新安装
   - 重启电脑

3. **使用替代方案**：
   - 考虑使用 VoiceMeeter（更强大但更复杂）
   - 或使用屏幕共享+音频共享功能

---

**立即开始排查**：
```bash
python diagnose_full_chain.py
```
