"""
测试设备[16] CABLE Input 到会议软件的完整链路
"""
import sounddevice as sd
import numpy as np
import time

print("\n" + "=" * 70)
print("测试设备[16] CABLE Input")
print("=" * 70 + "\n")

devices = sd.query_devices()

# 检查设备[16]
if len(devices) <= 16:
    print(f"❌ 错误：系统只有 {len(devices)} 个设备，没有设备[16]")
    exit(1)

device_16 = devices[16]
print(f"设备[16]信息：")
print(f"  名称: {device_16['name']}")
print(f"  输出通道: {device_16['max_output_channels']}")
print(f"  采样率: {device_16['default_samplerate']}Hz")

if device_16['max_output_channels'] == 0:
    print(f"\n❌ 设备[16]不是输出设备！无法播放音频")
    exit(1)

print("\n" + "=" * 70)
print("重要说明")
print("=" * 70 + "\n")

print("这个测试会播放测试音到设备[16]")
print("如果会议软件的CABLE Output对应设备[16]，对方应该能听到\n")

print("⚠️  请确保：")
print("  1. 会议软件已打开")
print("  2. 会议软件麦克风选择了: CABLE Output (VB-Audio Virtual Cable)")
print("  3. 麦克风未静音")
print("  4. 告诉会议对方准备听测试音\n")

input("按 Enter 开始播放测试音...\n")

# 使用48000Hz采样率（设备[16]的采样率）
sample_rate = int(device_16['default_samplerate'])
duration = 5

print(f"🔊 播放 {duration} 秒测试音到设备[16]...")
print(f"   使用采样率: {sample_rate}Hz")
print(f"   这和程序使用的配置完全一样\n")

# 生成明显的测试音
t = np.linspace(0, duration, int(sample_rate * duration))
# 440Hz (A4音) + 880Hz泛音，容易识别
audio = 0.3 * np.sin(2 * np.pi * 440 * t)
audio += 0.2 * np.sin(2 * np.pi * 880 * t)
audio = audio.astype(np.float32)

try:
    print("播放中...")
    sd.play(audio, samplerate=sample_rate, device=16)
    sd.wait()
    print("✅ 播放完成\n")
except Exception as e:
    print(f"❌ 播放失败: {e}\n")
    exit(1)

print("=" * 70)
result = input("会议对方能听到这个测试音吗？(y/n): ").strip().lower()
print("=" * 70 + "\n")

if result == 'y':
    print("🎉 太好了！设备[16]的CABLE链路正常！\n")
    print("这说明：")
    print("  ✅ 设备[16] → CABLE Output → 会议软件 链路正常")
    print("  ✅ 测试音能传输")
    print("  ❌ 但程序的TTS音频不能传输\n")
    
    print("=" * 70)
    print("问题定位：程序TTS音频问题")
    print("=" * 70 + "\n")
    
    print("可能的原因：")
    print("\n1️⃣ 音频数据格式问题")
    print("   测试音是简单的sin波，TTS是复杂的语音")
    print("   可能TTS音频数据有问题")
    
    print("\n2️⃣ 音频太小声")
    print("   TTS音频振幅可能太小")
    print("   会议软件阈值过滤了")
    
    print("\n3️⃣ 采样率转换问题")
    print("   24000Hz → 48000Hz 转换可能有问题")
    
    print("\n建议操作：")
    print("  1. 在程序中增加音量增益")
    print("  2. 检查重采样算法")
    print("  3. 对比测试音和TTS音频的波形")
    
else:
    print("❌ 测试音也听不到！\n")
    print("这说明：")
    print("  ❌ 设备[16] → CABLE Output → 会议软件 链路不通")
    print("  ❌ 不是程序的问题，是CABLE配置问题\n")
    
    print("=" * 70)
    print("问题定位：CABLE设备配对错误")
    print("=" * 70 + "\n")
    
    print("会议软件的 'CABLE Output (VB-Audio Virtual Cable)' 不对应设备[16]！\n")
    
    print("可能的情况：")
    print("\n1️⃣ 您的系统有多个VB-Cable实例")
    print("   程序用的设备[16]")
    print("   会议软件用的是另一个CABLE Output")
    
    print("\n2️⃣ VB-Cable驱动配置问题")
    print("   虚拟线缆没有正确连接Input和Output")
    
    print("\n3️⃣ 会议软件权限问题")
    print("   会议软件无法访问CABLE Output")
    
    print("\n=" * 70)
    print("解决方案")
    print("=" * 70 + "\n")
    
    print("方案1：找到正确的设备配对（推荐）\n")
    print("  运行以下测试：")
    print("  1. python test_device_6.py   # 测试设备[6]")
    print("  2. python test_device_14.py  # 测试设备[14]")
    print("  3. python test_device_16.py  # 测试设备[16]（当前）")
    print("  找到哪个设备能让会议听到，就用哪个\n")
    
    print("方案2：重置VB-Cable（彻底解决）\n")
    print("  1. 卸载所有VB-Cable和虚拟音频软件")
    print("  2. 重启电脑")
    print("  3. 只安装一个VB-Audio Virtual Cable")
    print("  4. 重启电脑")
    print("  5. 重新测试\n")
    
    print("方案3：检查Windows音频设置\n")
    print("  1. Windows声音设置 → 输入")
    print("  2. 找到 CABLE Output (VB-Audio Virtual Cable)")
    print("  3. 点击设备属性")
    print("  4. 确保未禁用且音量不为0")
    print("  5. 在高级选项卡中，尝试不同的默认格式\n")

print("\n" + "=" * 70)
print("下一步操作")
print("=" * 70 + "\n")

if result == 'y':
    print("测试音能听到，说明CABLE链路正常")
    print("问题在程序的TTS音频处理\n")
    print("我会帮您修改代码增加音量增益和改进重采样")
else:
    print("测试音听不到，说明CABLE配置有问题")
    print("需要找到正确的设备配对或重置VB-Cable\n")
    print("请告诉我您想尝试哪个方案")

print("\n" + "=" * 70 + "\n")
