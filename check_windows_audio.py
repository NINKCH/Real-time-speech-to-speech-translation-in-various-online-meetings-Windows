"""
检查Windows音量设置
"""
import sounddevice as sd
import numpy as np
import time

print("\n" + "=" * 70)
print("Windows音量设置检查和测试")
print("=" * 70 + "\n")

# 查找CABLE Output
cable_output_index = None
devices = sd.query_devices()

for i, device in enumerate(devices):
    if 'cable output' in device['name'].lower() and device['max_input_channels'] > 0:
        cable_output_index = i
        print(f"✅ 找到 CABLE Output: [{i}] {device['name']}")
        print(f"   最大输入通道: {device['max_input_channels']}")
        print(f"   默认采样率: {device['default_samplerate']}Hz")
        break

if cable_output_index is None:
    print("❌ 未找到 CABLE Output 设备")
    exit(1)

print("\n" + "=" * 70)
print("步骤1: 检查Windows声音设置")
print("=" * 70 + "\n")

print("请按照以下步骤操作：\n")
print("1. 右键点击任务栏的音量图标 🔊")
print("2. 点击'声音设置'")
print("3. 向下滚动到'输入'部分")
print("4. 在下拉菜单中选择: CABLE Output (VB-Audio Virtual Cable)")
print("\n5. 查看音量滑块和音量条")
print("   ❌ 如果音量是 0 → 调高到 50-100")
print("   ❌ 如果看不到音量条 → 设备可能被禁用")

input("\n完成上述检查后，按 Enter 继续...\n")

print("=" * 70)
print("步骤2: 测试音频输出并观察Windows音量条")
print("=" * 70 + "\n")

print("现在我将播放一系列测试音到 CABLE Input")
print("请同时观察Windows声音设置中的音量条\n")
print("⚠️  重要：保持Windows声音设置窗口打开！")
print("   观察 CABLE Output 的音量条是否有波动\n")

input("准备好后按 Enter 开始...")

# 查找CABLE Input
cable_input_index = None
for i, device in enumerate(devices):
    if 'cable input' in device['name'].lower() and device['max_output_channels'] > 0:
        cable_input_index = i
        break

if cable_input_index is None:
    print("❌ 未找到 CABLE Input")
    exit(1)

print(f"\n播放到设备 [{cable_input_index}] CABLE Input...")
print("观察Windows中 CABLE Output 的音量条！\n")

# 播放5次短促的beep
for i in range(5):
    print(f"播放第 {i+1}/5 次 'beep'... ", end='', flush=True)
    
    # 生成短促的beep
    sample_rate = 24000
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 880  # 更高的频率，更容易听到
    audio = (0.5 * np.sin(2 * np.pi * frequency * t)).astype(np.float32)
    
    sd.play(audio, samplerate=sample_rate, device=cable_input_index)
    sd.wait()
    print("✓")
    time.sleep(0.5)

print("\n" + "=" * 70)
result = input("Windows中的音量条有波动吗？(y/n): ").strip().lower()
print("=" * 70 + "\n")

if result == 'y':
    print("✅ 太好了！CABLE链路正常工作！\n")
    print("音频流向正常：")
    print("  程序 → CABLE Input → [虚拟线缆] → CABLE Output → 音量条波动 ✅\n")
    
    print("既然音量条有波动，那么问题可能在：\n")
    print("1️⃣ 会议软件配置")
    print("   → 会议软件真的选择了 CABLE Output 吗？")
    print("   → 截图会议软件的音频设置给我看看")
    print("   → 或者描述一下麦克风选项")
    
    print("\n2️⃣ 会议软件麦克风权限")
    print("   → Windows 设置 → 隐私 → 麦克风")
    print("   → 确保会议软件（腾讯会议/Zoom等）有权限")
    
    print("\n3️⃣ 会议软件测试麦克风")
    print("   → 在会议软件中点击'测试麦克风'")
    print("   → 运行 python test_cable_audio.py")
    print("   → 看会议软件的麦克风测试是否有音量指示")
    
else:
    print("❌ 音量条没有波动！\n")
    print("这说明Windows没有从 CABLE Output 接收到音频\n")
    
    print("可能的原因：\n")
    
    print("1️⃣ CABLE Output 被禁用")
    print("   解决：")
    print("   → Windows 声音设置")
    print("   → 输入设备列表")
    print("   → 找到 CABLE Output")
    print("   → 确保'已启用'")
    
    print("\n2️⃣ CABLE Output 没有选为当前输入设备")
    print("   解决：")
    print("   → 在'输入'下拉菜单中")
    print("   → 选择 CABLE Output")
    
    print("\n3️⃣ VB-Cable 驱动问题")
    print("   解决：")
    print("   → 重启电脑（最简单）")
    print("   → 或重新安装 VB-Cable")
    
    print("\n4️⃣ CABLE Input → CABLE Output 链路断开")
    print("   这是VB-Cable内部的问题")
    print("   解决：重启电脑")

print("\n" + "=" * 70)
print("步骤3: 详细排查")
print("=" * 70 + "\n")

print("现在请打开：Windows 设置 → 系统 → 声音 → 输入\n")
print("找到 CABLE Output，点击后查看：\n")

check_list = [
    "设备是否启用（不是禁用）",
    "音量是否大于0（建议50-100）",
    "播放测试音时，音量条是否跳动",
    "设备属性中是否有错误提示"
]

for i, item in enumerate(check_list, 1):
    status = input(f"{i}. {item}？(y/n): ").strip().lower()
    if status != 'y':
        print(f"   ❌ 这里有问题！需要修复")
    else:
        print(f"   ✅ 正常")

print("\n" + "=" * 70)
print("诊断总结")
print("=" * 70 + "\n")

print("如果上面的检查都是'y'，但还是听不到，那么：")
print("1. 重启电脑（最有效）")
print("2. 重新安装 VB-Cable")
print("3. 检查会议软件的具体配置")
print("\n" + "=" * 70 + "\n")
