"""
完整音频链路诊断工具
从程序输出到会议软件接收的完整链路测试
"""
import sounddevice as sd
import numpy as np
import time
import threading

def test_section(title):
    print("\n" + "=" * 70)
    print(f"📋 {title}")
    print("=" * 70 + "\n")

def find_cable_devices():
    """查找CABLE设备"""
    devices = sd.query_devices()
    cable_input = None
    cable_output = None
    
    for i, device in enumerate(devices):
        if 'cable input' in device['name'].lower() and device['max_output_channels'] > 0:
            cable_input = (i, device)
        if 'cable output' in device['name'].lower() and device['max_input_channels'] > 0:
            cable_output = (i, device)
    
    return cable_input, cable_output, devices

def test_playback_to_cable_input(device_index, duration=3):
    """测试播放到CABLE Input"""
    sample_rate = 24000
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 生成容易识别的测试音：440Hz基音 + 880Hz泛音
    audio = 0.3 * np.sin(2 * np.pi * 440 * t)
    audio += 0.2 * np.sin(2 * np.pi * 880 * t)
    audio = audio.astype(np.float32)
    
    print(f"🔊 播放 {duration} 秒测试音到 CABLE Input...")
    print(f"   设备索引: [{device_index}]")
    print(f"   音频长度: {len(audio)} 样本")
    print(f"   采样率: {sample_rate}Hz")
    
    try:
        sd.play(audio, samplerate=sample_rate, device=device_index)
        print("   播放中...", end='', flush=True)
        sd.wait()
        print(" ✅ 完成")
        return True
    except Exception as e:
        print(f" ❌ 失败: {e}")
        return False

def test_record_from_cable_output(device_index, duration=3):
    """测试从CABLE Output录音"""
    sample_rate = 24000
    
    print(f"🎤 从 CABLE Output 录音 {duration} 秒...")
    print(f"   设备索引: [{device_index}]")
    
    try:
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            device=device_index,
            dtype=np.float32
        )
        print("   录音中...", end='', flush=True)
        sd.wait()
        print(" ✅ 完成")
        
        # 分析录音
        max_amplitude = np.max(np.abs(recording))
        rms = np.sqrt(np.mean(recording**2))
        
        print(f"\n   录音分析:")
        print(f"   - 最大振幅: {max_amplitude:.4f}")
        print(f"   - RMS能量: {rms:.4f}")
        
        if max_amplitude > 0.01:
            print(f"   ✅ 录到音频了！振幅: {max_amplitude:.4f}")
            return True, recording
        else:
            print(f"   ❌ 几乎没有音频！振幅: {max_amplitude:.4f}")
            return False, recording
            
    except Exception as e:
        print(f" ❌ 失败: {e}")
        return False, None

def test_loopback():
    """完整回环测试"""
    test_section("完整音频链路测试")
    
    cable_input, cable_output, devices = find_cable_devices()
    
    if not cable_input:
        print("❌ 未找到 CABLE Input 设备")
        return False
    
    if not cable_output:
        print("❌ 未找到 CABLE Output 设备")
        return False
    
    print(f"✅ CABLE Input:  [{cable_input[0]}] {cable_input[1]['name']}")
    print(f"✅ CABLE Output: [{cable_output[0]}] {cable_output[1]['name']}")
    
    # 测试1：先单独播放
    test_section("测试1: 播放音频到 CABLE Input")
    input("准备好后按 Enter 开始播放测试音...")
    
    success = test_playback_to_cable_input(cable_input[0], duration=3)
    
    if not success:
        print("\n❌ 播放失败！问题在程序输出端")
        return False
    
    # 测试2：先单独录音
    test_section("测试2: 从 CABLE Output 录音（静默测试）")
    print("这个测试会录音3秒，测试CABLE Output是否能录音")
    input("按 Enter 开始...")
    
    success, _ = test_record_from_cable_output(cable_output[0], duration=3)
    
    if not success:
        print("\n⚠️ 录音功能可能有问题，但继续下一步测试")
    
    # 测试3：回环测试（同时播放和录音）
    test_section("测试3: 完整回环测试（同时播放和录音）")
    print("这个测试会：")
    print("  1. 播放测试音到 CABLE Input")
    print("  2. 同时从 CABLE Output 录音")
    print("  3. 检查录音中是否有测试音")
    
    input("\n准备好后按 Enter 开始...")
    
    print("\n🔄 开始回环测试...")
    
    # 准备录音
    sample_rate = 24000
    duration = 5
    
    # 在后台开始录音
    print("1️⃣ 启动录音...")
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        device=cable_output[0],
        dtype=np.float32
    )
    
    # 等待一小段时间确保录音开始
    time.sleep(0.5)
    
    # 播放测试音
    print("2️⃣ 播放测试音...")
    t = np.linspace(0, 3, int(sample_rate * 3))
    audio = 0.3 * np.sin(2 * np.pi * 440 * t)
    audio += 0.2 * np.sin(2 * np.pi * 880 * t)
    audio = audio.astype(np.float32)
    
    sd.play(audio, samplerate=sample_rate, device=cable_input[0])
    
    # 等待完成
    print("3️⃣ 等待完成...")
    sd.wait()
    
    print("4️⃣ 分析结果...")
    
    # 分析录音
    max_amplitude = np.max(np.abs(recording))
    rms = np.sqrt(np.mean(recording**2))
    
    print(f"\n录音分析:")
    print(f"  最大振幅: {max_amplitude:.4f}")
    print(f"  RMS能量: {rms:.4f}")
    
    print("\n" + "=" * 70)
    print("回环测试结果")
    print("=" * 70 + "\n")
    
    if max_amplitude > 0.01:
        print("🎉 成功！CABLE 音频链路正常工作！")
        print(f"\n✅ CABLE Input → CABLE Output 传输正常")
        print(f"✅ 最大振幅: {max_amplitude:.4f}")
        print(f"✅ 这证明虚拟线缆工作正常")
        
        print("\n" + "=" * 70)
        print("❓ 那为什么会议软件听不到？")
        print("=" * 70)
        
        print("\n可能的原因：")
        print("\n1️⃣ 会议软件配置问题")
        print("   □ 会议软件真的选择了 CABLE Output 吗？")
        print("   □ 麦克风是否被静音？")
        print("   □ 会议软件是否有麦克风权限？")
        
        print("\n2️⃣ 程序的TTS音频问题")
        print("   □ 程序是否真的在输出TTS音频？")
        print("   □ 检查日志是否有 '🔊 输出TTS音频'")
        print("   □ 音频数据是否正确？")
        
        print("\n建议操作：")
        print("  1. 在会议软件中测试麦克风")
        print("  2. 同时运行: python test_cable_audio.py")
        print("  3. 看会议软件的麦克风音量指示是否跳动")
        
        return True
        
    else:
        print("❌ 失败！CABLE 音频链路不工作！")
        print(f"\n录音振幅太小: {max_amplitude:.4f}")
        print(f"这说明 CABLE Input → CABLE Output 没有传输音频")
        
        print("\n" + "=" * 70)
        print("问题定位")
        print("=" * 70)
        
        print("\n可能的原因：")
        print("\n1️⃣ VB-Cable 驱动问题")
        print("   解决：重启电脑")
        
        print("\n2️⃣ CABLE Output 被禁用或音量为0")
        print("   检查：")
        print("   - Windows 声音设置 → 输入")
        print("   - 找到 CABLE Output")
        print("   - 确保已启用且音量不为0")
        
        print("\n3️⃣ CABLE Input 被禁用或音量为0")
        print("   检查：")
        print("   - Windows 声音设置 → 输出")
        print("   - 找到 CABLE Input")
        print("   - 确保已启用且音量不为0")
        
        print("\n4️⃣ Windows音频服务问题")
        print("   解决：")
        print("   - 按 Win+R")
        print("   - 输入 services.msc")
        print("   - 找到 'Windows Audio'")
        print("   - 重启服务")
        
        return False

def main():
    print("\n" + "=" * 70)
    print("🔬 完整音频链路诊断工具")
    print("=" * 70)
    print("\n这个工具会测试从 CABLE Input 到 CABLE Output 的完整链路")
    print("帮助您找出为什么会议软件听不到翻译的英文语音\n")
    
    input("按 Enter 开始诊断...")
    
    # 步骤1：检查设备
    test_section("步骤1: 检查 CABLE 设备")
    
    cable_input, cable_output, devices = find_cable_devices()
    
    if not cable_input:
        print("❌ 未找到 CABLE Input 设备")
        print("   请安装 VB-Audio Virtual Cable")
        return
    
    if not cable_output:
        print("❌ 未找到 CABLE Output 设备")
        print("   请安装 VB-Audio Virtual Cable")
        return
    
    print(f"✅ 找到 CABLE Input:  [{cable_input[0]}] {cable_input[1]['name']}")
    print(f"   输出通道: {cable_input[1]['max_output_channels']}")
    print(f"   采样率: {cable_input[1]['default_samplerate']}Hz")
    
    print(f"\n✅ 找到 CABLE Output: [{cable_output[0]}] {cable_output[1]['name']}")
    print(f"   输入通道: {cable_output[1]['max_input_channels']}")
    print(f"   采样率: {cable_output[1]['default_samplerate']}Hz")
    
    # 步骤2：检查程序输出
    test_section("步骤2: 检查程序输出的设备索引")
    
    print("根据您的日志，程序输出到设备[5]")
    print(f"我们找到的 CABLE Input 是设备[{cable_input[0]}]")
    
    if cable_input[0] == 5:
        print("\n✅ 设备索引匹配！程序输出到正确的设备")
    else:
        print(f"\n❌ 设备索引不匹配！")
        print(f"   程序输出到: 设备[5]")
        print(f"   CABLE Input 是: 设备[{cable_input[0]}]")
        print(f"\n   设备[5]是: {devices[5]['name']}")
        print(f"\n⚠️  这可能是问题所在！")
        print(f"   建议：重启程序让它重新扫描设备")
    
    # 步骤3：完整回环测试
    input("\n按 Enter 继续完整回环测试...")
    success = test_loopback()
    
    # 最终总结
    test_section("诊断总结")
    
    if success:
        print("✅ CABLE 音频链路正常工作")
        print("\n问题可能在：")
        print("  1. 会议软件配置（最可能）")
        print("  2. 程序的TTS音频输出")
        print("  3. 会议软件麦克风权限")
        
        print("\n下一步操作：")
        print("  1. 检查会议软件麦克风设置")
        print("  2. 在会议软件中测试麦克风")
        print("  3. 检查程序日志中的 🔊 输出")
    else:
        print("❌ CABLE 音频链路不工作")
        print("\n最可能的解决方案：")
        print("  1. 重启电脑（90%的情况能解决）")
        print("  2. 检查Windows音量设置")
        print("  3. 重新安装 VB-Cable")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
