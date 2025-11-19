"""
音频设备诊断工具
检查VB-Cable虚拟音频设备的配置
"""
import sounddevice as sd
import numpy as np
import time

def diagnose_audio_devices():
    """诊断音频设备"""
    print("\n" + "=" * 70)
    print("音频设备诊断工具")
    print("=" * 70 + "\n")
    
    print("1️⃣ 所有音频设备列表：")
    print("-" * 70)
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        marker = ""
        if device['max_input_channels'] > 0:
            marker += " [输入]"
        if device['max_output_channels'] > 0:
            marker += " [输出]"
        
        print(f"[{i:2d}] {device['name']}{marker}")
        print(f"     输入通道: {device['max_input_channels']}, "
              f"输出通道: {device['max_output_channels']}, "
              f"采样率: {device['default_samplerate']}Hz")
    
    print("\n2️⃣ VB-Cable 虚拟音频设备检测：")
    print("-" * 70)
    
    cable_input = None
    cable_output = None
    
    for i, device in enumerate(devices):
        name_lower = device['name'].lower()
        
        # 查找 CABLE Input（程序应该输出到这里）
        if 'cable input' in name_lower and device['max_output_channels'] > 0:
            cable_input = {'index': i, 'device': device}
            print(f"✅ 找到 CABLE Input (输出设备): [{i}] {device['name']}")
            print(f"   → 程序应该向这里输出音频")
        
        # 查找 CABLE Output（会议软件应该从这里读取）
        if 'cable output' in name_lower and device['max_input_channels'] > 0:
            cable_output = {'index': i, 'device': device}
            print(f"✅ 找到 CABLE Output (输入设备): [{i}] {device['name']}")
            print(f"   → 会议软件应该选择这个作为麦克风")
    
    if not cable_input:
        print("❌ 未找到 CABLE Input 输出设备")
        print("   请安装 VB-Audio Virtual Cable")
        print("   下载地址: https://vb-audio.com/Cable/")
        return False
    
    if not cable_output:
        print("⚠️  未找到 CABLE Output 输入设备")
    
    print("\n3️⃣ 测试音频输出到 CABLE Input：")
    print("-" * 70)
    
    try:
        print(f"正在测试输出到设备 [{cable_input['index']}] {cable_input['device']['name']}...")
        
        # 生成测试音（440Hz正弦波，2秒）
        sample_rate = 24000
        duration = 2.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440
        test_audio = (np.sin(2 * np.pi * frequency * t) * 0.3).astype(np.float32)
        
        # 播放到 CABLE Input
        sd.play(test_audio, samplerate=sample_rate, device=cable_input['index'])
        print(f"✅ 正在播放测试音（440Hz，{duration}秒）...")
        print(f"   如果会议软件选择了 CABLE Output 作为麦克风，")
        print(f"   应该能听到这个测试音。")
        
        sd.wait()
        print("✅ 测试音播放完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    finally:
        print("\n" + "=" * 70)
        print("诊断完成")
        print("=" * 70)


def test_virtual_audio_module():
    """测试 VirtualAudioOutput 模块"""
    print("\n" + "=" * 70)
    print("测试 VirtualAudioOutput 模块")
    print("=" * 70 + "\n")
    
    try:
        from modules.virtual_audio import VirtualAudioOutput
        
        # 创建虚拟音频输出
        print("初始化 VirtualAudioOutput...")
        output = VirtualAudioOutput(device_name="CABLE Input", sample_rate=24000)
        
        print(f"设备索引: {output.device_index}")
        
        if output.device_index is None:
            print("❌ 未找到虚拟音频设备")
            return False
        
        # 打印可用设备
        output.print_devices()
        
        # 启动输出
        print("\n启动虚拟音频输出...")
        output.start()
        
        # 生成测试音
        print("播放测试音...")
        duration = 2.0
        sample_rate = 24000
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440
        test_audio = (np.sin(2 * np.pi * frequency * t) * 0.3).astype(np.float32)
        
        # 播放测试音
        output.play(test_audio)
        print(f"✅ 测试音已加入队列，队列大小: {output.get_queue_size()}")
        
        # 等待播放完成
        time.sleep(duration + 0.5)
        
        # 停止输出
        output.stop()
        
        print("✅ VirtualAudioOutput 模块测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🔍 开始音频设备诊断...\n")
    
    # 诊断音频设备
    device_ok = diagnose_audio_devices()
    
    if device_ok:
        # 测试 VirtualAudioOutput 模块
        print("\n" + "=" * 70)
        input("按 Enter 继续测试 VirtualAudioOutput 模块...")
        test_virtual_audio_module()
    
    print("\n" + "=" * 70)
    print("💡 使用说明：")
    print("=" * 70)
    print("1. 确保安装了 VB-Audio Virtual Cable")
    print("2. 程序应该输出音频到 'CABLE Input'")
    print("3. 会议软件应该选择 'CABLE Output' 作为麦克风输入")
    print("4. 音频流向：程序 → CABLE Input → [虚拟线缆] → CABLE Output → 会议")
    print("=" * 70 + "\n")
