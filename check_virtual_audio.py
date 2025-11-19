"""
虚拟音频配置快速检查
"""
import sounddevice as sd

def check_virtual_audio():
    print("\n" + "=" * 70)
    print("虚拟音频配置检查")
    print("=" * 70 + "\n")
    
    devices = sd.query_devices()
    cable_input = None
    cable_output = None
    issues = []
    
    # 检查 CABLE Input（程序输出设备）
    print("1️⃣ 检查 CABLE Input (程序音频输出)...")
    for i, device in enumerate(devices):
        if 'cable input' in device['name'].lower() and device['max_output_channels'] > 0:
            cable_input = (i, device)
            print(f"   ✅ 找到: [{i}] {device['name']}")
            print(f"      输出通道: {device['max_output_channels']}")
            print(f"      采样率: {device['default_samplerate']}Hz")
            break
    
    if not cable_input:
        print("   ❌ 未找到 CABLE Input 设备")
        issues.append("未安装 VB-Cable 或设备未启用")
    
    # 检查 CABLE Output（会议软件输入设备）
    print("\n2️⃣ 检查 CABLE Output (会议软件麦克风)...")
    for i, device in enumerate(devices):
        if 'cable output' in device['name'].lower() and device['max_input_channels'] > 0:
            cable_output = (i, device)
            print(f"   ✅ 找到: [{i}] {device['name']}")
            print(f"      输入通道: {device['max_input_channels']}")
            print(f"      采样率: {device['default_samplerate']}Hz")
            break
    
    if not cable_output:
        print("   ⚠️  未找到 CABLE Output 设备")
        print("      （会议软件可能无法使用虚拟麦克风）")
    
    # 检查程序配置
    print("\n3️⃣ 检查程序配置...")
    try:
        from modules.virtual_audio import VirtualAudioOutput
        print("   ✅ VirtualAudioOutput 模块可用")
        
        # 检查默认设备名
        import inspect
        init_signature = inspect.signature(VirtualAudioOutput.__init__)
        device_name_default = init_signature.parameters['device_name'].default
        print(f"   默认设备名: {device_name_default}")
        
        if cable_input and device_name_default.lower() in cable_input[1]['name'].lower():
            print("   ✅ 默认设备名匹配")
        else:
            print("   ⚠️  默认设备名可能不匹配")
            
    except Exception as e:
        print(f"   ❌ 模块导入失败: {e}")
        issues.append("程序模块有问题")
    
    # 总结
    print("\n" + "=" * 70)
    print("检查结果")
    print("=" * 70 + "\n")
    
    if cable_input and cable_output and len(issues) == 0:
        print("🎉 配置检查通过！\n")
        print("✅ VB-Cable 已正确安装")
        print("✅ CABLE Input 可用（程序输出）")
        print("✅ CABLE Output 可用（会议软件输入）")
        print("✅ 程序模块正常")
        
        print("\n" + "=" * 70)
        print("下一步操作")
        print("=" * 70 + "\n")
        print("1. 启动程序:")
        print("   python main.py")
        print("\n2. 在程序中:")
        print("   翻译模式: 选择【s2s (语音到语音)】")
        print("   点击【▶ 开始翻译】")
        print("\n3. 在会议软件中:")
        print("   麦克风: 选择【CABLE Output (VB-Audio Virtual Cable)】")
        print("\n4. 测试:")
        print("   说中文 → 程序翻译成英文 → 会议中听到英文")
        
        print("\n" + "=" * 70)
        print("音频流向")
        print("=" * 70)
        print(f"""
您的麦克风
    ↓ (采集)
程序 [RealtimeASTTranslator]
    ↓ (翻译)
豆包同传 API
    ↓ (TTS音频)
CABLE Input [{cable_input[0]}] {cable_input[1]['name']}
    ↓ (虚拟线缆)
CABLE Output [{cable_output[0]}] {cable_output[1]['name']}
    ↓ (作为麦克风)
会议软件 (Zoom/腾讯会议/Teams等)
    ↓
会议中的其他人
""")
        
    else:
        print("❌ 配置检查未通过！\n")
        
        for issue in issues:
            print(f"   ❌ {issue}")
        
        print("\n" + "=" * 70)
        print("解决方案")
        print("=" * 70 + "\n")
        
        if not cable_input or not cable_output:
            print("📥 安装 VB-Audio Virtual Cable:")
            print("   1. 访问: https://vb-audio.com/Cable/")
            print("   2. 下载 VB-CABLE Driver")
            print("   3. 解压后以管理员权限运行安装程序")
            print("   4. 重启电脑")
            print("   5. 重新运行此检查脚本")
            print("\n⚙️  启用设备（如果已安装）:")
            print("   1. Windows 设置 → 系统 → 声音")
            print("   2. 高级声音选项")
            print("   3. 找到 CABLE Input 和 CABLE Output")
            print("   4. 右键 → 启用")
        
        print("\n📖 详细指南:")
        print("   notepad VIRTUAL_AUDIO_SETUP_GUIDE.md")
        print("\n🚑 快速故障排除:")
        print("   notepad QUICK_FIX_VIRTUAL_AUDIO.md")
    
    print("\n" + "=" * 70 + "\n")
    
    return len(issues) == 0


if __name__ == "__main__":
    success = check_virtual_audio()
    
    if success:
        print("✅ 一切就绪！可以开始使用了。\n")
    else:
        print("❌ 需要先解决上述问题。\n")
        print("💡 提示: 如需帮助，运行完整诊断:")
        print("   python diagnose_audio.py\n")
