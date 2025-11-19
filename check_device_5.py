"""
检查设备[5]是什么设备
"""
import sounddevice as sd

print("\n" + "=" * 70)
print("检查音频输出设备 [5]")
print("=" * 70 + "\n")

devices = sd.query_devices()

# 显示设备[5]的详细信息
if len(devices) > 5:
    device_5 = devices[5]
    print(f"设备 [5] 的详细信息：")
    print(f"  名称: {device_5['name']}")
    print(f"  输入通道: {device_5['max_input_channels']}")
    print(f"  输出通道: {device_5['max_output_channels']}")
    print(f"  默认采样率: {device_5['default_samplerate']}Hz")
    print(f"  设备类型: {'输出设备' if device_5['max_output_channels'] > 0 else '输入设备'}")
    
    print("\n" + "=" * 70)
    print("问题分析")
    print("=" * 70 + "\n")
    
    # 检查是否是CABLE Input
    is_cable_input = 'cable input' in device_5['name'].lower()
    
    if is_cable_input:
        print("✅ 设备[5]是 CABLE Input - 配置正确！")
        print("\n可能的问题：")
        print("1. 会议软件是否选择了 CABLE Output？")
        print("2. 会议软件麦克风是否被静音？")
        print("3. Windows音量设置是否正常？")
        print("4. 会议软件是否有麦克风权限？")
        
        print("\n✅ 音频正在输出到正确的设备")
        print("   问题在会议软件端或系统音量设置")
        
    else:
        print(f"❌ 设备[5]不是 CABLE Input - 配置错误！")
        print(f"   当前输出到: {device_5['name']}")
        print(f"\n这是问题所在！程序正在输出到错误的设备。")
    
    print("\n" + "=" * 70)
    print("所有输出设备列表")
    print("=" * 70 + "\n")
    
    cable_input_index = None
    for i, device in enumerate(devices):
        if device['max_output_channels'] > 0:
            marker = " ← 当前使用" if i == 5 else ""
            is_cable = "🎯 CABLE Input" if 'cable input' in device['name'].lower() else ""
            print(f"[{i}] {device['name']}{marker} {is_cable}")
            
            if 'cable input' in device['name'].lower():
                cable_input_index = i
    
    if cable_input_index is not None and cable_input_index != 5:
        print("\n" + "=" * 70)
        print("⚠️ 发现问题！")
        print("=" * 70)
        print(f"\n正确的 CABLE Input 设备索引是 [{cable_input_index}]")
        print(f"但程序正在使用设备 [5]: {device_5['name']}")
        print(f"\n可能原因：")
        print(f"1. 音频设备列表发生了变化")
        print(f"2. 程序启动时找到了错误的设备")
        print(f"3. 有其他音频设备插入/移除")
        
        print(f"\n解决方案：")
        print(f"1. 重启程序（让它重新扫描设备）")
        print(f"2. 或者修改代码，指定设备索引为 [{cable_input_index}]")
    
else:
    print(f"❌ 系统只有 {len(devices)} 个音频设备，没有设备[5]")
    print("\n所有设备：")
    for i, device in enumerate(devices):
        print(f"[{i}] {device['name']}")

print("\n" + "=" * 70)
print("测试建议")
print("=" * 70 + "\n")

print("方案1: 重启程序")
print("  关闭当前程序，重新运行:")
print("  python main.py")
print("\n方案2: 测试CABLE Input")
print("  运行测试脚本验证CABLE Input是否工作:")
print("  python diagnose_audio.py")
print("\n方案3: 检查会议软件")
print("  确认会议软件选择了 CABLE Output 作为麦克风")
print("\n" + "=" * 70 + "\n")
