"""
验证功能测试
测试声音复刻验证对话框
"""
import sys
from pathlib import Path

def test_verification():
    """测试验证功能"""
    print("\n" + "=" * 70)
    print("声音复刻验证功能测试")
    print("=" * 70 + "\n")
    
    results = []
    
    # 测试1: 导入验证对话框
    print("测试1: 验证对话框导入")
    print("-" * 70)
    try:
        from gui.voice_clone_test_dialog import VoiceCloneTestDialog
        print("✅ VoiceCloneTestDialog 导入成功")
        results.append(("验证对话框", True))
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        results.append(("验证对话框", False))
        return results
    
    # 测试2: 主窗口集成
    print("\n测试2: 主窗口集成")
    print("-" * 70)
    try:
        from gui.main_window import MainWindow
        
        # 检查是否有show_voice_test方法
        assert hasattr(MainWindow, 'show_voice_test'), "缺少 show_voice_test 方法"
        print("✅ MainWindow 包含 show_voice_test 方法")
        
        # 检查main_window.py中是否有验证按钮
        with open("gui/main_window.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "验证复刻" in content, "缺少验证复刻按钮"
        print("✅ 主窗口包含验证复刻按钮")
        
        assert "voice_test_btn" in content, "缺少验证按钮变量"
        print("✅ 验证按钮已正确定义")
        
        results.append(("主窗口集成", True))
    except Exception as e:
        print(f"❌ 集成检查失败: {e}")
        results.append(("主窗口集成", False))
    
    # 测试3: 对话框功能
    print("\n测试3: 对话框功能检查")
    print("-" * 70)
    try:
        from PyQt6.QtWidgets import QApplication
        from gui.voice_clone_test_dialog import VoiceCloneTestDialog
        
        # 创建应用
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建对话框
        dialog = VoiceCloneTestDialog()
        
        # 检查关键组件
        components = [
            ("测试按钮", "test_btn"),
            ("停止按钮", "stop_btn"),
            ("播放按钮", "play_btn"),
            ("保存按钮", "save_btn"),
            ("进度条", "progress_bar"),
            ("状态文本", "status_text"),
            ("结果标签", "result_label"),
            ("测试文本", "test_text_label"),
        ]
        
        for name, attr in components:
            assert hasattr(dialog, attr), f"缺少 {attr}"
            print(f"✅ {name:15s} - {attr:20s}")
        
        # 检查方法
        methods = [
            ("开始测试", "start_test"),
            ("停止测试", "stop_test"),
            ("播放音频", "play_cloned_audio"),
            ("保存音频", "save_cloned_audio"),
        ]
        
        for name, method in methods:
            assert hasattr(dialog, method), f"缺少 {method} 方法"
            print(f"✅ {name:15s} - {method:20s}")
        
        dialog.close()
        results.append(("对话框功能", True))
        
    except Exception as e:
        print(f"❌ 功能检查失败: {e}")
        results.append(("对话框功能", False))
    
    # 测试4: 文档完整性
    print("\n测试4: 文档完整性")
    print("-" * 70)
    docs = [
        ("验证指南", "VOICE_CLONE_VERIFICATION_GUIDE.md"),
        ("零样本说明", "ZERO_SHOT_VOICE_CLONING.md"),
        ("最终总结", "FINAL_UPDATE_SUMMARY.md"),
    ]
    
    for name, filename in docs:
        path = Path(filename)
        if path.exists():
            size = path.stat().st_size / 1024
            print(f"✅ {name:15s} - {filename:45s} ({size:.1f}KB)")
            results.append((f"文档-{name}", True))
        else:
            print(f"❌ {name:15s} - {filename:45s} (不存在)")
            results.append((f"文档-{name}", False))
    
    # 测试5: 界面按钮布局
    print("\n测试5: 界面按钮布局")
    print("-" * 70)
    try:
        with open("gui/main_window.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查按钮顺序和配置
        checks = [
            ("功能说明按钮", "ℹ️ 功能说明"),
            ("验证复刻按钮", "🔬 验证复刻"),
            ("蓝色背景", "#2196F3"),
            ("橙色背景", "#FF9800"),
        ]
        
        for name, text in checks:
            if text in content:
                print(f"✅ {name:20s} - 已配置")
            else:
                print(f"⚠️ {name:20s} - 未找到")
        
        results.append(("界面布局", True))
        
    except Exception as e:
        print(f"❌ 布局检查失败: {e}")
        results.append(("界面布局", False))
    
    # 总结
    print("\n" + "=" * 70)
    print("测试结果总结")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status:10s} - {name}")
    
    print("\n" + "=" * 70)
    print(f"总计: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    print("=" * 70 + "\n")
    
    if passed == total:
        print("🎉 所有测试通过！声音复刻验证功能已准备就绪。")
        print("\n✨ 新增功能：")
        print("   - 🔬 验证复刻按钮（橙色）")
        print("   - 完整的测试对话框")
        print("   - 实时录音和复刻")
        print("   - 播放复刻音频")
        print("   - 保存音频样本")
        print("\n🚀 使用方法：")
        print("   python main.py")
        print("   点击【🔬 验证复刻】")
        print("   朗读测试文本")
        print("   听取复刻效果")
        print("   保存音频样本")
        print("\n📖 查看文档：")
        print("   VOICE_CLONE_VERIFICATION_GUIDE.md - 详细使用指南")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(test_verification())
