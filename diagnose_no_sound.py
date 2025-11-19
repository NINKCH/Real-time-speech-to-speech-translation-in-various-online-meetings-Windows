"""
诊断"有音频日志但听不到声音"的问题
"""
import sounddevice as sd
import numpy as np

def main():
    print("\n" + "=" * 70)
    print("诊断：有音频输出日志但会议中听不到声音")
    print("=" * 70 + "\n")
    
    print("从您的日志中看到：")
    print("  🔊 输出TTS音频: XXX字节 → XXX样本 → 设备[5]")
    print("\n这说明程序正在输出音频到设备[5]")
    print("现在我们来检查设备[5]是什么...\n")
    
    devices = sd.query_devices()
    
    # 检查设备[5]
    if len(devices) <= 5:
        print(f"❌ 错误：系统只有 {len(devices)} 个设备，没有设备[5]")
        print("\n所有设备：")
        for i, device in enumerate(devices):
            print(f"  [{i}] {device['name']}")
        return
    
    device_5 = devices[5]
    print("=" * 70)
    print("设备[5]信息")
    print("=" * 70)
    print(f"名称: {device_5['name']}")
    print(f"输出通道: {device_5['max_output_channels']}")
    print(f"输入通道: {device_5['max_input_channels']}")
    
    # 检查是否是CABLE Input
    is_cable_input = 'cable input' in device_5['name'].lower()
    
    print("\n" + "=" * 70)
    print("问题诊断")
    print("=" * 70 + "\n")
    
    # 查找正确的CABLE Input
    cable_input_index = None
    for i, device in enumerate(devices):
        if 'cable input' in device['name'].lower() and device['max_output_channels'] > 0:
            cable_input_index = i
            break
    
    if not is_cable_input:
        print("❌ 问题找到了！")
        print(f"\n设备[5]不是 CABLE Input！")
        print(f"设备[5]是: {device_5['name']}")
        
        if cable_input_index is not None:
            print(f"\n正确的 CABLE Input 是设备[{cable_input_index}]:")
            print(f"  {devices[cable_input_index]['name']}")
            
            print("\n" + "=" * 70)
            print("❌ 根本原因")
            print("=" * 70)
            print("\n程序找错了设备！")
            print(f"程序应该输出到设备[{cable_input_index}]（CABLE Input）")
            print(f"但实际输出到了设备[5]（{device_5['name']}）")
            
            print("\n可能原因：")
            print("1. 音频设备列表发生了变化")
            print("2. 有其他音频设备插入/移除")
            print("3. 程序启动时的设备扫描结果不准确")
            
            print("\n" + "=" * 70)
            print("✅ 解决方案")
            print("=" * 70)
            print("\n方案1：重启程序（推荐）")
            print("  1. 关闭当前程序")
            print("  2. 重新运行: python main.py")
            print("  3. 程序会重新扫描设备，应该会找到正确的CABLE Input")
            
            print("\n方案2：手动指定设备")
            print(f"  在 modules/virtual_audio.py 中手动指定设备索引 {cable_input_index}")
            
        else:
            print("\n❌ 更严重的问题：系统中没有找到 CABLE Input 设备！")
            print("\n解决方案：")
            print("1. 安装 VB-Audio Virtual Cable")
            print("   https://vb-audio.com/Cable/")
            print("2. 确保 CABLE Input 设备已启用")
            print("   Windows 设置 → 系统 → 声音 → 高级声音选项")
        
    else:
        print("✅ 设备[5]是 CABLE Input - 设备配置正确")
        print(f"   {device_5['name']}")
        
        print("\n音频正在输出到正确的设备")
        print("问题不在程序端，而在会议软件或系统设置")
        
        # 查找CABLE Output
        cable_output_index = None
        for i, device in enumerate(devices):
            if 'cable output' in device['name'].lower() and device['max_input_channels'] > 0:
                cable_output_index = i
                break
        
        print("\n" + "=" * 70)
        print("检查会议软件配置")
        print("=" * 70 + "\n")
        
        if cable_output_index is not None:
            print(f"✅ 系统中有 CABLE Output 设备:")
            print(f"   [{cable_output_index}] {devices[cable_output_index]['name']}")
            
            print("\n请检查会议软件设置：")
            print("1. 打开会议软件音频设置")
            print("2. 麦克风应该选择:")
            print(f"   ✅ CABLE Output (VB-Audio Virtual Cable)")
            print("   ❌ 不要选择 CABLE Input")
            print("   ❌ 不要选择其他麦克风")
            print("\n3. 确认麦克风未静音")
            print("4. 测试麦克风（应该有音量指示）")
            
        else:
            print("⚠️  未找到 CABLE Output 设备")
            print("   会议软件可能无法使用虚拟麦克风")
        
        print("\n" + "=" * 70)
        print("测试CABLE音频")
        print("=" * 70 + "\n")
        
        test = input("要播放测试音到CABLE Input吗？(会议中应该能听到) (y/n): ").strip().lower()
        
        if test == 'y':
            print("\n播放测试音...")
            print("如果配置正确，会议中应该能听到3秒的'beep'声")
            
            sample_rate = 24000
            duration = 3
            t = np.linspace(0, duration, int(sample_rate * duration))
            frequency = 440
            audio = (0.3 * np.sin(2 * np.pi * frequency * t)).astype(np.float32)
            
            try:
                sd.play(audio, samplerate=sample_rate, device=5)
                sd.wait()
                print("✅ 测试音播放完成")
                
                heard = input("\n会议中能听到测试音吗？(y/n): ").strip().lower()
                
                if heard == 'y':
                    print("\n🎉 太好了！说明：")
                    print("  ✅ CABLE Input/Output 工作正常")
                    print("  ✅ 会议软件配置正确")
                    print("\n那么原问题可能是：")
                    print("  ⚠️  程序的TTS音频数据有问题")
                    print("  ⚠️  或者音频格式转换有问题")
                    print("\n建议：检查 translator_app.py 中的 _on_tts_audio 方法")
                else:
                    print("\n❌ 听不到测试音")
                    print("\n问题在会议软件配置或系统设置")
                    print("请检查：")
                    print("1. 会议软件麦克风是否选择了 CABLE Output")
                    print("2. 会议软件麦克风是否被静音")
                    print("3. Windows 声音设置中 CABLE Output 是否启用")
                    print("4. CABLE Output 音量是否正常")
                    
            except Exception as e:
                print(f"❌ 播放失败: {e}")
    
    # 显示所有输出设备
    print("\n" + "=" * 70)
    print("所有音频输出设备")
    print("=" * 70 + "\n")
    
    for i, device in enumerate(devices):
        if device['max_output_channels'] > 0:
            marker = " ← 程序当前使用" if i == 5 else ""
            cable = " 🎯" if 'cable input' in device['name'].lower() else ""
            print(f"[{i}] {device['name']}{marker}{cable}")
    
    print("\n" + "=" * 70)
    print("总结和建议")
    print("=" * 70 + "\n")
    
    if is_cable_input:
        print("设备配置：✅ 正确")
        print("问题可能在：会议软件配置 或 系统音量设置")
        print("\n建议操作：")
        print("1. 检查会议软件麦克风设置（选择 CABLE Output）")
        print("2. 检查会议软件麦克风是否静音")
        print("3. 检查 Windows 音量设置")
        print("4. 运行测试: python test_cable_audio.py")
    else:
        print("设备配置：❌ 错误")
        print(f"程序输出到了错误的设备[5]: {device_5['name']}")
        print("\n建议操作：")
        print("1. 重启程序: python main.py")
        print("2. 让程序重新扫描设备")
        print("3. 再次测试")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
