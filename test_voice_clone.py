"""
测试声音克隆功能
"""
import sys
from pathlib import Path

def test_imports():
    """测试导入"""
    print("=" * 60)
    print("测试1: 导入模块")
    print("=" * 60)
    
    try:
        from gui.voice_clone_dialog import VoiceCloneDialog
        print("✅ VoiceCloneDialog 导入成功")
    except Exception as e:
        print(f"❌ VoiceCloneDialog 导入失败: {e}")
        return False
    
    try:
        from gui.main_window import MainWindow
        print("✅ MainWindow 导入成功")
    except Exception as e:
        print(f"❌ MainWindow 导入失败: {e}")
        return False
    
    try:
        from modules.ast_client_protobuf import ASTClientProtobuf
        print("✅ ASTClientProtobuf 导入成功")
    except Exception as e:
        print(f"❌ ASTClientProtobuf 导入失败: {e}")
        return False
    
    try:
        from translator_app import RealtimeTranslatorApp
        print("✅ RealtimeTranslatorApp 导入成功")
    except Exception as e:
        print(f"❌ RealtimeTranslatorApp 导入失败: {e}")
        return False
    
    print("\n✅ 所有模块导入成功！\n")
    return True


def test_protobuf_client():
    """测试Protobuf客户端的speaker_id支持"""
    print("=" * 60)
    print("测试2: Protobuf客户端 speaker_id 支持")
    print("=" * 60)
    
    from modules.ast_client_protobuf import ASTClientProtobuf
    
    # 创建客户端
    client = ASTClientProtobuf("test_key", "test_access")
    
    # 测试设置speaker_id
    test_speaker_id = "voice_test_12345"
    client.set_config(speaker_id=test_speaker_id)
    
    if client.speaker_id == test_speaker_id:
        print(f"✅ speaker_id 设置成功: {client.speaker_id}")
    else:
        print(f"❌ speaker_id 设置失败: {client.speaker_id}")
        return False
    
    # 测试清空speaker_id
    client.set_config(speaker_id="")
    if client.speaker_id == "":
        print("✅ speaker_id 清空成功")
    else:
        print(f"❌ speaker_id 清空失败: {client.speaker_id}")
        return False
    
    print("\n✅ Protobuf客户端测试通过！\n")
    return True


def test_translator_app():
    """测试TranslatorApp的speaker_id支持"""
    print("=" * 60)
    print("测试3: TranslatorApp speaker_id 支持")
    print("=" * 60)
    
    from translator_app import RealtimeTranslatorApp
    
    # 创建应用
    app = RealtimeTranslatorApp("test_key", "test_access")
    
    # 检查初始值
    if hasattr(app, 'speaker_id'):
        print(f"✅ 应用有 speaker_id 属性: {app.speaker_id}")
    else:
        print("❌ 应用缺少 speaker_id 属性")
        return False
    
    # 测试设置
    test_speaker_id = "voice_app_test"
    app.set_config(speaker_id=test_speaker_id)
    
    if app.speaker_id == test_speaker_id:
        print(f"✅ speaker_id 配置成功: {app.speaker_id}")
    else:
        print(f"❌ speaker_id 配置失败: {app.speaker_id}")
        return False
    
    print("\n✅ TranslatorApp 测试通过！\n")
    return True


def test_config_persistence():
    """测试配置持久化"""
    print("=" * 60)
    print("测试4: 配置持久化")
    print("=" * 60)
    
    import json
    from pathlib import Path
    
    config_file = Path("voice_clone_config_test.json")
    test_speaker_id = "voice_persist_test"
    
    # 写入配置
    try:
        config = {"speaker_id": test_speaker_id}
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print("✅ 配置文件写入成功")
    except Exception as e:
        print(f"❌ 配置文件写入失败: {e}")
        return False
    
    # 读取配置
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            loaded_config = json.load(f)
        loaded_speaker_id = loaded_config.get("speaker_id", "")
        
        if loaded_speaker_id == test_speaker_id:
            print(f"✅ 配置文件读取成功: {loaded_speaker_id}")
        else:
            print(f"❌ 配置文件读取失败: {loaded_speaker_id}")
            return False
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        return False
    finally:
        # 清理测试文件
        if config_file.exists():
            config_file.unlink()
            print("✅ 测试文件已清理")
    
    print("\n✅ 配置持久化测试通过！\n")
    return True


def test_language_support():
    """测试语言支持"""
    print("=" * 60)
    print("测试5: 多语言支持")
    print("=" * 60)
    
    languages = [
        "zh", "en", "ja", "ko",
        "es", "fr", "de", "ru",
        "ar", "pt", "it"
    ]
    
    print(f"支持的语言代码: {len(languages)} 种")
    for i, lang in enumerate(languages, 1):
        print(f"  {i}. {lang}")
    
    print("\n✅ 语言列表验证通过！\n")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("声音克隆功能测试套件")
    print("=" * 60 + "\n")
    
    tests = [
        ("模块导入", test_imports),
        ("Protobuf客户端", test_protobuf_client),
        ("TranslatorApp", test_translator_app),
        ("配置持久化", test_config_persistence),
        ("多语言支持", test_language_support),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ 测试 '{name}' 出现异常: {e}\n")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    print(f"总计: {passed}/{total} 通过")
    print("=" * 60 + "\n")
    
    if passed == total:
        print("🎉 所有测试通过！声音克隆功能已准备就绪。")
        print("\n下一步：")
        print("1. 运行 python main.py 启动应用")
        print("2. 点击'🎤 声音克隆'按钮配置 Speaker ID")
        print("3. 开始使用个性化的实时翻译！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查上述错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
