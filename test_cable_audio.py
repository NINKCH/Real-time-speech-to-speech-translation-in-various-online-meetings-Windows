"""
测试CABLE音频输出
直接向CABLE Input播放测试音，检查会议软件是否能听到
"""
import sounddevice as sd
import numpy as np
import time

def find_cable_input():
    """查找CABLE Input设备"""
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if 'cable input' in device['name'].lower() and device['max_output_channels'] > 0:
            return i, device
    return None, None

def play_test_tone(device_index, duration=3, frequency=440):
    """播放测试音到指定设备"""
    sample_rate = 24000
    t = np.linspace(0, duration, int(sample_rate * duration))
    # 生成测试音（440Hz + 880Hz混合，更容易辨认）
    audio = 0.3 * np.sin(2 * np.pi * frequency * t)  # 主音
    audio += 0.2 * np.sin(2 * np.pi * frequency * 2 * t)  # 泛音
    audio = audio.astype(np.float32)
    
    print(f"播放测试音到设备 [{device_index}]...")
    print(f"  频率: {frequency}Hz")
    print(f"  时长: {duration}秒")
    print(f"  采样率: {sample_rate}Hz")
    
    sd.play(audio, samplerate=sample_rate, device=device_index)
    sd.wait()
    
    print("✅ 测试音播放完成")

def main():
    print("\n" + "=" * 70)
    print("CABLE 音频输出测试")
    print("=" * 70 + "\n")
    
    print("步骤1: 查找 CABLE Input 设备...")
    device_index, device_info = find_cable_input()
    
    if device_index is None:
        print("❌ 未找到 CABLE Input 设备")
        print("\n请确保：")
        print("1. 已安装 VB-Audio Virtual Cable")
        print("2. CABLE Input 设备已启用")
        return
    
    print(f"✅ 找到设备: [{device_index}] {device_info['name']}")
    
    print("\n" + "=" * 70)
    print("步骤2: 准备测试")
    print("=" * 70 + "\n")
    
    print("⚠️  重要提示：")
    print("1. 请确保会议软件已打开")
    print("2. 会议软件麦克风选择了 'CABLE Output'")
    print("3. 会议软件麦克风未静音")
    print("4. 如果在会议中，告诉其他人您要测试麦克风")
    
    input("\n按 Enter 开始播放测试音...")
    
    print("\n" + "=" * 70)
    print("步骤3: 播放测试音")
    print("=" * 70 + "\n")
    
    print("🔊 即将播放3秒测试音...")
    print("   如果会议软件配置正确，您（或会议中的其他人）应该能听到")
    print("   一个清晰的 'beep' 声音\n")
    
    time.sleep(1)
    
    # 播放测试音
    play_test_tone(device_index, duration=3, frequency=440)
    
    print("\n" + "=" * 70)
    print("步骤4: 验证结果")
    print("=" * 70 + "\n")
    
    result = input("您（或会议中的其他人）能听到测试音吗？(y/n): ").strip().lower()
    
    if result == 'y':
        print("\n🎉 太好了！CABLE 音频输出工作正常！")
        print("\n这意味着：")
        print("  ✅ CABLE Input 设备工作正常")
        print("  ✅ CABLE Output 设备工作正常")
        print("  ✅ 会议软件配置正确")
        print("\n问题可能在于：")
        print("  ⚠️  程序没有正确输出音频到 CABLE Input")
        print("  ⚠️  或者设备索引不匹配")
        print("\n检查程序日志中的设备索引：")
        print(f"  应该输出到设备 [{device_index}]")
        print(f"  但日志显示输出到设备 [?]")
        
    else:
        print("\n❌ 无法听到测试音")
        print("\n可能的问题：")
        print("1. 会议软件没有选择 CABLE Output 作为麦克风")
        print("   → 打开会议软件音频设置，选择 'CABLE Output'")
        print("\n2. 会议软件麦克风被静音")
        print("   → 取消静音")
        print("\n3. Windows 音量设置问题")
        print("   → Windows 设置 → 系统 → 声音")
        print("   → 输入设备 → CABLE Output")
        print("   → 检查音量和是否启用")
        print("\n4. 会议软件没有麦克风权限")
        print("   → Windows 设置 → 隐私 → 麦克风")
        print("   → 确保会议软件有权限")
    
    print("\n" + "=" * 70)
    print("额外测试：播放语音提示")
    print("=" * 70 + "\n")
    
    test_voice = input("要播放一段'说话'的测试音吗？(y/n): ").strip().lower()
    
    if test_voice == 'y':
        print("\n🔊 播放模拟语音测试音...")
        print("   （多个频率混合，模拟语音）\n")
        
        # 生成模拟语音的测试音
        sample_rate = 24000
        duration = 2
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # 混合多个频率模拟语音
        audio = 0.2 * np.sin(2 * np.pi * 200 * t)  # 基频
        audio += 0.15 * np.sin(2 * np.pi * 400 * t)  # 泛音1
        audio += 0.1 * np.sin(2 * np.pi * 600 * t)  # 泛音2
        audio += 0.05 * np.sin(2 * np.pi * 800 * t)  # 泛音3
        
        # 添加包络（模拟语音的起伏）
        envelope = np.abs(np.sin(2 * np.pi * 3 * t))
        audio = audio * envelope
        audio = audio.astype(np.float32)
        
        sd.play(audio, samplerate=sample_rate, device=device_index)
        sd.wait()
        
        print("✅ 测试完成")
    
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70 + "\n")
    
    print(f"CABLE Input 设备: [{device_index}] {device_info['name']}")
    print(f"程序应该输出到: 设备 [{device_index}]")
    print(f"\n下一步：")
    print(f"1. 检查程序日志中的设备索引")
    print(f"2. 运行: python check_device_5.py")
    print(f"3. 如果设备索引不匹配，重启程序")
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
