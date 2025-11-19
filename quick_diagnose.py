"""
一键快速诊断：为什么对方听不到英文语音
"""
import sounddevice as sd
import numpy as np
import time

print("\n" + "=" * 70)
print("快速诊断：会议对方听不到英文语音")
print("=" * 70 + "\n")

# 步骤1：检查设备[5]
print("步骤1：检查程序输出的设备[5]")
print("-" * 70)

devices = sd.query_devices()

if len(devices) <= 5:
    print(f"❌ 错误：系统只有 {len(devices)} 个设备，没有设备[5]")
    print("\n这是严重的问题！程序无法输出到设备[5]")
    exit(1)

device_5 = devices[5]
print(f"设备[5]: {device_5['name']}")

is_cable_input = 'cable input' in device_5['name'].lower()

if is_cable_input:
    print("✅ 设备[5]是 CABLE Input - 正确！")
else:
    print(f"❌ 设备[5]不是 CABLE Input - 错误！")
    print(f"   设备[5]是: {device_5['name']}")
    
    # 查找正确的CABLE Input
    for i, device in enumerate(devices):
        if 'cable input' in device['name'].lower() and device['max_output_channels'] > 0:
            print(f"\n正确的 CABLE Input 是设备[{i}]: {device['name']}")
            print("\n❌ 问题找到了：程序输出到了错误的设备！")
            print("\n解决方案：")
            print("1. 关闭程序")
            print("2. 重新运行: python main.py")
            print("3. 让程序重新扫描设备")
            exit(1)
    
    print("\n❌ 系统中没有找到 CABLE Input 设备！")
    print("请安装 VB-Audio Virtual Cable")
    exit(1)

# 步骤2：检查CABLE Output
print("\n步骤2：检查 CABLE Output（会议软件麦克风）")
print("-" * 70)

cable_output_found = False
cable_output_index = None

for i, device in enumerate(devices):
    if 'cable output' in device['name'].lower() and device['max_input_channels'] > 0:
        cable_output_found = True
        cable_output_index = i
        print(f"✅ 找到 CABLE Output: [{i}] {device['name']}")
        break

if not cable_output_found:
    print("❌ 未找到 CABLE Output 设备")
    print("   会议软件无法使用虚拟麦克风")
    exit(1)

# 步骤3：音频链路测试
print("\n步骤3：测试音频链路")
print("-" * 70)
print("\n⚠️  准备播放测试音...")
print("   请确保：")
print("   1. 会议软件已打开")
print("   2. 会议软件麦克风选择了 'CABLE Output'")
print("   3. 告诉对方准备听测试音")

input("\n按 Enter 开始播放测试音...")

print("\n🔊 播放3秒测试音到 CABLE Input...")
print("   对方应该能听到一个清晰的 'beep' 声\n")

# 生成测试音
sample_rate = 24000
duration = 3
t = np.linspace(0, duration, int(sample_rate * duration))
frequency = 440
audio = (0.3 * np.sin(2 * np.pi * frequency * t)).astype(np.float32)

try:
    sd.play(audio, samplerate=sample_rate, device=5)
    print("播放中...")
    sd.wait()
    print("✅ 播放完成")
except Exception as e:
    print(f"❌ 播放失败: {e}")
    exit(1)

# 询问结果
print("\n" + "=" * 70)
result = input("会议对方能听到这个测试音吗？(y/n): ").strip().lower()
print("=" * 70 + "\n")

if result == 'y':
    print("🎉 太好了！CABLE 音频链路正常！")
    print("\n这说明：")
    print("  ✅ 设备[5]配置正确")
    print("  ✅ CABLE Input → CABLE Output 链路正常")
    print("  ✅ 会议软件配置正确")
    print("  ✅ Windows 音量设置正常")
    
    print("\n" + "=" * 70)
    print("❓ 那为什么对方听不到翻译的英文语音？")
    print("=" * 70)
    
    print("\n可能的原因：")
    print("\n1. 程序的TTS音频数据有问题")
    print("   → 检查日志中是否持续有 🔊 输出TTS音频")
    print("   → 确认模式是 s2s（语音到语音）")
    
    print("\n2. 音频数据格式转换有问题")
    print("   → 检查 translator_app.py 的 _on_tts_audio 方法")
    
    print("\n3. 音频太小声")
    print("   → 调高 Windows 中 CABLE Output 的音量")
    print("   → 或调高会议软件麦克风音量")
    
    print("\n建议操作：")
    print("1. 重启程序并重新测试")
    print("2. 观察日志中 🔊 的频率")
    print("3. 说话时应该持续看到 🔊 日志")
    print("4. 如果没有 🔊 日志，检查模式是否为 s2s")
    
    print("\n" + "=" * 70)
    print("额外测试：检查音频是否真的在播放")
    print("=" * 70)
    
    print("\n让我们再播放一段更明显的测试音...")
    input("按 Enter 播放'哔哔哔'三声...")
    
    # 播放三声
    for i in range(3):
        print(f"\n第{i+1}声...")
        beep = (0.3 * np.sin(2 * np.pi * 880 * t[:sample_rate])).astype(np.float32)
        sd.play(beep, samplerate=sample_rate, device=5)
        sd.wait()
        time.sleep(0.5)
    
    result2 = input("\n对方能听到这三声'哔哔哔'吗？(y/n): ").strip().lower()
    
    if result2 == 'y':
        print("\n✅ 音频输出完全正常！")
        print("\n问题一定在程序的TTS音频数据")
        print("\n请检查：")
        print("1. 程序是否真的在输出TTS音频")
        print("2. 说话时是否持续看到 🔊 日志")
        print("3. 🔊 日志的频率是否正常（每秒几次）")
    else:
        print("\n⚠️  第二次测试也听不到")
        print("可能是间歇性问题或网络延迟")

else:
    print("❌ 对方听不到测试音")
    print("\n这说明音频链路有问题！")
    
    print("\n" + "=" * 70)
    print("问题定位")
    print("=" * 70)
    
    print("\n问题可能在：")
    
    print("\n1️⃣ 会议软件麦克风设置")
    print("   → 打开会议软件音频设置")
    print("   → 确认麦克风是：CABLE Output (VB-Audio Virtual Cable)")
    print("   → 确认麦克风未静音")
    print("   → 点击'测试麦克风'看是否有音量指示")
    
    print("\n2️⃣ Windows 音量设置")
    print("   → 右键任务栏音量图标 → 声音设置")
    print("   → 输入设备 → 选择 CABLE Output")
    print("   → 点击'设备属性'")
    print("   → 确认音量不是0，设备未禁用")
    print("   → 说话时查看音量条是否有波动")
    
    print("\n3️⃣ VB-Cable 驱动")
    print("   → VB-Cable 可能需要重新安装")
    print("   → 或者重启电脑")
    
    print("\n4️⃣ 会议软件权限")
    print("   → Windows 设置 → 隐私 → 麦克风")
    print("   → 确保会议软件有麦克风权限")
    
    print("\n建议操作顺序：")
    print("1. 检查会议软件麦克风设置（最常见）")
    print("2. 检查 Windows 音量设置")
    print("3. 重启会议软件")
    print("4. 重启 VB-Cable 驱动（重启电脑）")

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70 + "\n")

print("总结：")
print(f"  设备[5]: {device_5['name']}")
print(f"  是否CABLE Input: {'✅ 是' if is_cable_input else '❌ 否'}")
print(f"  测试音能否听到: {result}")

print("\n下一步：")
if result == 'y':
    print("  → 问题在程序的TTS音频数据")
    print("  → 检查程序日志和配置")
else:
    print("  → 问题在音频链路配置")
    print("  → 检查会议软件和系统设置")

print("\n" + "=" * 70 + "\n")
