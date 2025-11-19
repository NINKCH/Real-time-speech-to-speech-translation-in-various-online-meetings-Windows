"""
测试所有CABLE Input设备
找出哪个能让会议软件听到
"""
import sounddevice as sd
import numpy as np
import time

print("\n" + "=" * 70)
print("测试所有CABLE设备")
print("=" * 70 + "\n")

print("这个工具会逐个测试所有CABLE Input设备")
print("帮您找出会议软件实际使用的是哪一个\n")

devices = sd.query_devices()

# 找出所有CABLE Input
cable_inputs = []
for i, device in enumerate(devices):
    if 'cable input' in device['name'].lower() and device['max_output_channels'] > 0:
        cable_inputs.append((i, device))

if not cable_inputs:
    print("❌ 未找到任何CABLE Input设备")
    exit(1)

print(f"找到 {len(cable_inputs)} 个CABLE Input设备：\n")
for i, (idx, device) in enumerate(cable_inputs, 1):
    print(f"{i}. 设备[{idx}] {device['name']}")
    print(f"   采样率: {device['default_samplerate']}Hz")
    print()

print("=" * 70)
print("测试准备")
print("=" * 70 + "\n")

print("⚠️  请确保：")
print("  1. 会议软件已打开")
print("  2. 会议软件麦克风选择了: CABLE Output (VB-Audio Virtual Cable)")
print("  3. 麦克风未静音")
print("  4. 告诉会议对方准备听测试音")
print("  5. 每次播放后，让对方告诉您能否听到\n")

input("准备好后按 Enter 开始...\n")

# 逐个测试
working_devices = []

for i, (idx, device) in enumerate(cable_inputs, 1):
    print("=" * 70)
    print(f"测试 {i}/{len(cable_inputs)}: 设备[{idx}] {device['name']}")
    print("=" * 70 + "\n")
    
    sample_rate = int(device['default_samplerate'])
    duration = 3
    
    print(f"设备信息：")
    print(f"  索引: [{idx}]")
    print(f"  名称: {device['name']}")
    print(f"  采样率: {sample_rate}Hz\n")
    
    input(f"按 Enter 播放测试音到设备[{idx}]...")
    
    # 生成测试音
    t = np.linspace(0, duration, int(sample_rate * duration))
    # 每个设备用不同频率，方便区分
    frequency = 440 + (i - 1) * 110  # 440, 550, 660...
    audio = 0.3 * np.sin(2 * np.pi * frequency * t)
    audio = audio.astype(np.float32)
    
    try:
        print(f"🔊 播放测试音（频率: {frequency}Hz）...")
        sd.play(audio, samplerate=sample_rate, device=idx)
        sd.wait()
        print("✅ 播放完成\n")
        
        result = input("会议对方能听到吗？(y/n): ").strip().lower()
        
        if result == 'y':
            print(f"✅ 成功！设备[{idx}]能工作！\n")
            working_devices.append((idx, device))
        else:
            print(f"❌ 听不到\n")
            
    except Exception as e:
        print(f"❌ 播放失败: {e}\n")
    
    if i < len(cable_inputs):
        print("继续测试下一个设备...\n")
        time.sleep(1)

# 总结
print("\n" + "=" * 70)
print("测试总结")
print("=" * 70 + "\n")

if working_devices:
    print(f"🎉 找到 {len(working_devices)} 个能工作的设备：\n")
    
    for idx, device in working_devices:
        print(f"✅ 设备[{idx}] {device['name']}")
        print(f"   采样率: {device['default_samplerate']}Hz\n")
    
    if len(working_devices) == 1:
        idx, device = working_devices[0]
        print("=" * 70)
        print("修改程序配置")
        print("=" * 70 + "\n")
        
        print(f"在 translator_app.py 第107行，修改为：\n")
        print(f"    device_index={idx}  # 使用设备[{idx}]\n")
        
        print("或者运行以下命令自动修改：\n")
        print(f"    python -c \"import re; f=open('translator_app.py','r',encoding='utf-8'); s=f.read(); f.close(); s=re.sub(r'device_index=\\d+', 'device_index={idx}', s); f=open('translator_app.py','w',encoding='utf-8'); f.write(s); f.close(); print('✅ 已修改')\"")
        
    else:
        print("⚠️  找到多个能工作的设备")
        print("   建议使用第一个找到的")
        idx, device = working_devices[0]
        print(f"   → 设备[{idx}]\n")
        
else:
    print("❌ 所有设备都听不到测试音\n")
    
    print("这说明：")
    print("  1. 会议软件选择的CABLE Output不对应这些CABLE Input")
    print("  2. 或者CABLE虚拟线缆驱动有问题\n")
    
    print("=" * 70)
    print("故障排除")
    print("=" * 70 + "\n")
    
    print("方案1：检查会议软件麦克风设置")
    print("  → 确认真的选择了 CABLE Output")
    print("  → 尝试重新选择一次")
    print("  → 重启会议软件\n")
    
    print("方案2：检查Windows声音设置")
    print("  → Windows设置 → 声音 → 输入")
    print("  → 找到 CABLE Output")
    print("  → 确保已启用且音量不为0\n")
    
    print("方案3：重启VB-Cable驱动")
    print("  → 重启电脑（最简单有效）\n")
    
    print("方案4：重新安装VB-Cable")
    print("  → 卸载所有虚拟音频软件")
    print("  → 重启")
    print("  → 重新安装VB-Audio Virtual Cable")
    print("  → 重启\n")

print("=" * 70 + "\n")
