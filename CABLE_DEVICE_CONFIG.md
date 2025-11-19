# 🔧 CABLE设备配置指南

## 🎯 问题

您有**3个**CABLE Input设备：

```
设备[6]:  CABLE Input (VB-Audio Virtual C)        - 44100Hz ← 程序当前使用
设备[14]: CABLE Input (VB-Audio Virtual Cable)   - 44100Hz
设备[16]: CABLE Input (VB-Audio Virtual Cable)   - 48000Hz
```

程序和会议软件必须使用**同一对**CABLE设备！

---

## ✅ 解决方案1：在会议软件中切换CABLE Output（最简单）

### 步骤

1. **保持程序运行**（使用设备[6]）
2. **开始翻译**
3. **在会议软件中切换不同的CABLE Output麦克风**
4. **每切换一个，说话测试**
5. **找到能让对方听到的那个**

### 会议软件可能的CABLE Output选项

```
○ CABLE Output (VB-Audio Virtual C...)        ← 对应设备[6]  ✅ 试试这个
○ CABLE Output (VB-Audio Virtual Cable)       ← 对应设备[14]或[16]
○ CABLE Output (VB-Audio Point)
```

---

## ✅ 解决方案2：修改程序使用指定的CABLE设备

如果您希望程序使用特定的CABLE Input（例如设备[16]），可以修改代码：

### 方法A：指定设备索引

编辑 `modules/virtual_audio.py`，在 `__init__` 方法中添加设备索引参数：

```python
def __init__(self, device_name: str = "CABLE Input", sample_rate: int = 24000, device_index: int = None):
    """
    初始化虚拟音频输出
    
    Args:
        device_name: 虚拟设备名称
        sample_rate: 采样率
        device_index: 指定设备索引（如果提供则直接使用）
    """
    self.device_name = device_name
    self.sample_rate = sample_rate
    self.buffer_size = 1024
    self.force_device_index = device_index  # 强制使用的设备索引
    
    # ... 其余代码
```

然后在 `_find_device` 方法开头添加：

```python
def _find_device(self) -> Optional[int]:
    """查找虚拟音频设备"""
    # 如果指定了设备索引，直接使用
    if self.force_device_index is not None:
        devices = sd.query_devices()
        device = devices[self.force_device_index]
        print(f"✅ 使用指定设备: [{self.force_device_index}] {device['name']}")
        
        # 自动调整采样率
        device_sample_rate = int(device['default_samplerate'])
        if device_sample_rate != self.sample_rate:
            print(f"   自动调整采样率: {self.sample_rate}Hz → {device_sample_rate}Hz")
            self.sample_rate = device_sample_rate
        
        return self.force_device_index
    
    # 否则按名称查找（原有逻辑）
    # ...
```

然后在 `translator_app.py` 中修改：

```python
# 创建虚拟音频输出
if self.mode == "s2s":
    # 方式1：指定设备索引
    self.virtual_output = VirtualAudioOutput(sample_rate=24000, device_index=16)
    
    # 方式2：或者指定更精确的设备名称
    # self.virtual_output = VirtualAudioOutput(
    #     device_name="CABLE Input (VB-Audio Virtual Cable)",
    #     sample_rate=24000
    # )
```

### 方法B：指定更精确的设备名称

在 `translator_app.py` 第104行修改：

```python
# 创建虚拟音频输出
if self.mode == "s2s":
    # 使用完整设备名称进行精确匹配
    self.virtual_output = VirtualAudioOutput(
        device_name="CABLE Input (VB-Audio Virtual Cable)",  # 精确的完整名称
        sample_rate=24000
    )
```

---

## ✅ 解决方案3：卸载多余的CABLE设备（彻底解决）

如果您只使用一对CABLE设备，可以卸载其他的：

### 检查安装了哪些虚拟音频软件

按 `Win+R` → 输入 `appwiz.cpl` → 查找：

```
- VB-CABLE Virtual Audio Device
- VoiceMeeter
- VB-Audio Virtual Apps
```

### 建议

保留一个就够了：
- 只保留 **VB-Audio Virtual Cable** (CABLE Input/Output)
- 卸载其他重复的虚拟音频设备

---

## 🎯 推荐顺序

### 优先级1：快速测试（5分钟）

```bash
# 1. 运行配对分析
python list_cable_pairs.py

# 2. 启动程序
python main.py

# 3. 开始翻译

# 4. 在会议软件中逐个切换CABLE Output测试
#    找到能听到的那个
```

### 优先级2：如果找到了正确的配对

记录下来：
```
程序使用：设备[6] CABLE Input (VB-Audio Virtual C)
会议软件选择：CABLE Output (VB-Audio Virtual C...)  ← 完整名称
```

以后只要保持这个配置即可。

### 优先级3：如果测试都不行

修改程序使用其他CABLE设备：
```python
# 在 translator_app.py 第104行
self.virtual_output = VirtualAudioOutput(sample_rate=24000, device_index=16)
```

试试设备[14]或[16]。

---

## 📊 配对关系检查表

| CABLE Input | 采样率 | 对应的 CABLE Output | 会议软件应选择 |
|-------------|--------|---------------------|----------------|
| 设备[6]  - VB-Audio Virtual C | 44100Hz | 需要确认 | 待测试 |
| 设备[14] - VB-Audio Virtual Cable | 44100Hz | 需要确认 | 待测试 |
| 设备[16] - VB-Audio Virtual Cable | 48000Hz | 可能是设备[22] | 待测试 |

运行 `python list_cable_pairs.py` 查看完整配对分析。

---

## 💡 调试技巧

### 同时播放测试音和程序翻译

**终端1**（测试音）：
```bash
# 修改 test_cable_audio.py 使用特定设备
# 找到哪个设备能让会议听到
```

**终端2**（程序）：
```bash
python main.py
# 使用相同的设备
```

### 实时监控CABLE Output

在会议软件的麦克风测试界面：
- 保持打开
- 观察音量条
- 运行程序说话
- 看是否有波动

---

## 🎉 成功标志

```
✅ 运行配对分析找到对应关系
✅ 会议软件选择正确的CABLE Output
✅ 程序输出到对应的CABLE Input
✅ 说话时会议软件麦克风测试有音量指示
✅ 会议对方能听到英文翻译
```

---

**现在立即运行**：

```bash
python list_cable_pairs.py
```

查看配对分析，然后在会议软件中测试不同的CABLE Output！
