"""
组件测试脚本
用于测试各个模块是否正常工作
"""
import sys
import time


def test_imports():
    """测试导入"""
    print("=" * 60)
    print("测试1: 检查依赖导入")
    print("=" * 60)
    
    try:
        import numpy as np
        print("✅ numpy")
        
        import websockets
        print("✅ websockets")
        
        import sounddevice as sd
        print("✅ sounddevice")
        
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6")
        
        from dotenv import load_dotenv
        print("✅ python-dotenv")
        
        print("\n✅ 所有依赖导入成功！\n")
        return True
        
    except ImportError as e:
        print(f"\n❌ 依赖导入失败: {e}")
        print("请运行: pip install -r requirements.txt\n")
        return False


def test_audio_devices():
    """测试音频设备"""
    print("=" * 60)
    print("测试2: 检查音频设备")
    print("=" * 60)
    
    try:
        import sounddevice as sd
        
        devices = sd.query_devices()
        
        print("\n输入设备 (麦克风):")
        print("-" * 60)
        input_found = False
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"[{i}] {device['name']}")
                input_found = True
        
        if not input_found:
            print("❌ 未找到输入设备")
            return False
        
        print("\n输出设备 (扬声器):")
        print("-" * 60)
        output_found = False
        cable_found = False
        for i, device in enumerate(devices):
            if device['max_output_channels'] > 0:
                print(f"[{i}] {device['name']}")
                output_found = True
                if "CABLE" in device['name'].upper() or "VIRTUAL" in device['name'].upper():
                    cable_found = True
                    print(f"     ✅ 找到虚拟设备!")
        
        if not output_found:
            print("❌ 未找到输出设备")
            return False
        
        if not cable_found:
            print("\n⚠️ 警告: 未找到VB-Cable虚拟设备")
            print("请安装: https://vb-audio.com/Cable/")
            print("虚拟设备对于会议使用是必需的\n")
        else:
            print("\n✅ VB-Cable虚拟设备已安装\n")
        
        return True
        
    except Exception as e:
        print(f"❌ 音频设备检测失败: {e}\n")
        return False


def test_config():
    """测试配置"""
    print("=" * 60)
    print("测试3: 检查配置")
    print("=" * 60)
    
    try:
        import os
        from pathlib import Path
        from dotenv import load_dotenv
        
        env_file = Path(".env")
        
        if not env_file.exists():
            print("⚠️ .env 文件不存在")
            print("请复制 .env.example 为 .env 并填入API密钥\n")
            return False
        
        load_dotenv()
        
        app_key = os.getenv("DOUBAO_APP_KEY", "")
        access_key = os.getenv("DOUBAO_ACCESS_KEY", "")
        
        if not app_key or not access_key:
            print("⚠️ API密钥未配置")
            print("请在 .env 文件中设置:")
            print("  DOUBAO_APP_KEY=你的App_Key")
            print("  DOUBAO_ACCESS_KEY=你的Access_Key\n")
            return False
        
        print(f"✅ App Key: {app_key[:10]}...")
        print(f"✅ Access Key: {access_key[:10]}...")
        print("\n✅ 配置检查通过\n")
        return True
        
    except Exception as e:
        print(f"❌ 配置检查失败: {e}\n")
        return False


def test_modules():
    """测试模块"""
    print("=" * 60)
    print("测试4: 检查模块")
    print("=" * 60)
    
    try:
        from modules.audio_capture import AudioCapture
        print("✅ AudioCapture")
        
        from modules.virtual_audio import VirtualAudioOutput
        print("✅ VirtualAudioOutput")
        
        from modules.ast_client import ASTClient
        print("✅ ASTClient")
        
        from translator_app import RealtimeTranslatorApp
        print("✅ RealtimeTranslatorApp")
        
        from gui.main_window import MainWindow
        print("✅ MainWindow")
        
        print("\n✅ 所有模块加载成功\n")
        return True
        
    except Exception as e:
        print(f"❌ 模块加载失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "      豆包实时同声传译器 - 组件测试".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print("\n")
    
    results = []
    
    # 运行所有测试
    results.append(("依赖导入", test_imports()))
    results.append(("音频设备", test_audio_devices()))
    results.append(("配置检查", test_config()))
    results.append(("模块加载", test_modules()))
    
    # 汇总结果
    print("=" * 60)
    print("测试汇总")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 所有测试通过！你可以运行: python main.py\n")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请根据上述提示修复问题\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
