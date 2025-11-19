"""
列出所有CABLE设备对
"""
import sounddevice as sd

print("\n" + "=" * 70)
print("CABLE 设备配对分析")
print("=" * 70 + "\n")

devices = sd.query_devices()

# 找出所有CABLE Input（输出设备）
cable_inputs = []
for i, device in enumerate(devices):
    if 'cable input' in device['name'].lower() and device['max_output_channels'] > 0:
        cable_inputs.append((i, device))

# 找出所有CABLE Output（输入设备）
cable_outputs = []
for i, device in enumerate(devices):
    if 'cable output' in device['name'].lower() and device['max_input_channels'] > 0:
        cable_outputs.append((i, device))

print("📤 CABLE Input 设备（程序输出目标）：")
print("-" * 70)
for i, (idx, device) in enumerate(cable_inputs, 1):
    marker = " ← 程序当前使用" if idx == 6 else ""
    print(f"{i}. 设备[{idx:2d}] {device['name']}")
    print(f"   采样率: {device['default_samplerate']}Hz")
    print(f"   输出通道: {device['max_output_channels']}{marker}")
    print()

print("=" * 70)
print("📥 CABLE Output 设备（会议软件麦克风选择）：")
print("-" * 70)
for i, (idx, device) in enumerate(cable_outputs, 1):
    print(f"{i}. 设备[{idx:2d}] {device['name']}")
    print(f"   采样率: {device['default_samplerate']}Hz")
    print(f"   输入通道: {device['max_input_channels']}")
    print()

print("=" * 70)
print("🔗 设备配对说明")
print("=" * 70 + "\n")

print("VB-Audio Virtual Cable 通常有以下配对：\n")

# 尝试匹配配对
print("推测的配对关系：\n")

for input_idx, input_device in cable_inputs:
    input_name = input_device['name']
    input_rate = input_device['default_samplerate']
    
    # 移除 "Input" 并尝试匹配 "Output"
    base_name = input_name.replace('Input', '').replace('input', '').strip()
    
    print(f"📤 设备[{input_idx}] {input_name} ({input_rate}Hz)")
    
    # 查找可能的Output配对
    possible_outputs = []
    for output_idx, output_device in cable_outputs:
        output_name = output_device['name']
        output_rate = output_device['default_samplerate']
        
        # 简单匹配：名称相似或采样率相同
        if base_name.lower() in output_name.lower():
            possible_outputs.append((output_idx, output_device, "名称匹配"))
        elif abs(input_rate - output_rate) < 100:
            possible_outputs.append((output_idx, output_device, "采样率匹配"))
    
    if possible_outputs:
        print("   可能的配对：")
        for output_idx, output_device, reason in possible_outputs:
            print(f"   → 设备[{output_idx}] {output_device['name']} ({output_device['default_samplerate']}Hz) - {reason}")
    else:
        print("   ⚠️  未找到明确的配对")
    print()

print("=" * 70)
print("💡 建议操作")
print("=" * 70 + "\n")

print("当前程序使用：设备[6] CABLE Input (VB-Audio Virtual C) - 44100Hz\n")

print("会议软件应该选择以下麦克风之一：")
for output_idx, output_device in cable_outputs:
    if '44100' in str(output_device['default_samplerate']):
        # 尝试判断是否是设备[6]的配对
        if 'virtual c' in output_device['name'].lower():
            print(f"  ✅ 推荐：{output_device['name']} （最可能是设备[6]的配对）")
        else:
            print(f"  ⚪ 可能：{output_device['name']}")

print("\n或者修改程序使用不同的CABLE Input：")
print("  编辑 modules/virtual_audio.py")
print("  修改 device_name 参数指定具体设备")

print("\n" + "=" * 70 + "\n")
