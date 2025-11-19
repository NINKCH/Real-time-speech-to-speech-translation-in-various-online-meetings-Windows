"""
检查设备[6]是什么
"""
import sounddevice as sd

print("\n" + "=" * 70)
print("检查程序输出的设备[6]")
print("=" * 70 + "\n")

devices = sd.query_devices()

if len(devices) <= 6:
    print(f"❌ 错误：系统只有 {len(devices)} 个设备，没有设备[6]")
    exit(1)

device_6 = devices[6]

print(f"设备[6]详细信息：")
print(f"  名称: {device_6['name']}")
print(f"  输入通道: {device_6['max_input_channels']}")
print(f"  输出通道: {device_6['max_output_channels']}")
print(f"  默认采样率: {device_6['default_samplerate']}Hz")
print(f"  是否输出设备: {'是' if device_6['max_output_channels'] > 0 else '否'}")

print("\n" + "-" * 70)

# 检查是否是CABLE相关设备
is_cable = 'cable' in device_6['name'].lower()
print(f"是否包含'CABLE': {'是' if is_cable else '否'}")

if is_cable:
    print("\n✅ 设备[6]是CABLE相关设备！")
    print("   但可能不是正确的CABLE Input")
else:
    print("\n❌ 设备[6]不是CABLE设备！")
    print("   程序没有找到正确的虚拟音频设备")

print("\n" + "=" * 70)
print("查找真正的CABLE Input")
print("=" * 70 + "\n")

cable_input = None
for i, device in enumerate(devices):
    if device['max_output_channels'] > 0:
        if 'cable input' in device['name'].lower():
            cable_input = (i, device)
            print(f"✅ 找到 CABLE Input: [{i}] {device['name']}")
            print(f"   输出通道: {device['max_output_channels']}")
            print(f"   采样率: {device['default_samplerate']}Hz")
            break

if cable_input:
    print(f"\n" + "=" * 70)
    print("对比")
    print("=" * 70 + "\n")
    
    print(f"程序当前使用: 设备[6] {device_6['name']}")
    print(f"应该使用:     设备[{cable_input[0]}] {cable_input[1]['name']}")
    
    if cable_input[0] == 6:
        print("\n✅ 索引相同！但可能名称匹配有问题")
    else:
        print(f"\n❌ 索引不同！程序找错了设备")
        print(f"\n可能原因：")
        print(f"  1. 设备[6]的名称中也包含'CABLE'或'Virtual'")
        print(f"  2. 但它不是真正的CABLE Input")
        print(f"  3. 程序的查找逻辑误匹配了")
else:
    print("\n❌ 未找到CABLE Input设备！")
    print("   请确保已安装VB-Audio Virtual Cable")

print("\n" + "=" * 70)
print("所有输出设备列表")
print("=" * 70 + "\n")

for i, device in enumerate(devices):
    if device['max_output_channels'] > 0:
        marker = " ← 程序使用" if i == 6 else ""
        marker += " ← CABLE Input" if 'cable input' in device['name'].lower() else ""
        print(f"[{i:2d}] {device['name']:60} {marker}")
        print(f"     采样率: {device['default_samplerate']}Hz")

print("\n" + "=" * 70 + "\n")
