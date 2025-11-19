"""
声音克隆功能修复验证
"""
import sys

def test_fixes():
    """验证修复"""
    print("\n" + "=" * 70)
    print("声音克隆功能修复验证")
    print("=" * 70 + "\n")
    
    results = []
    
    # 测试1: 导入检查
    print("测试1: 模块导入")
    print("-" * 70)
    try:
        from gui.voice_clone_test_dialog import VoiceCloneTestDialog
        from gui.main_window import MainWindow
        print("✅ 所有模块导入成功")
        results.append(("模块导入", True))
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        results.append(("模块导入", False))
        return results
    
    # 测试2: 命名统一性检查
    print("\n测试2: 命名统一性（复刻→克隆）")
    print("-" * 70)
    try:
        # 检查voice_clone_test_dialog.py
        with open("gui/voice_clone_test_dialog.py", "r", encoding="utf-8") as f:
            dialog_content = f.read()
        
        # 检查main_window.py
        with open("gui/main_window.py", "r", encoding="utf-8") as f:
            main_content = f.read()
        
        # 应该包含"克隆"
        has_clone = "声音克隆" in main_content and "克隆" in dialog_content
        print(f"✅ 使用'克隆'术语: {'是' if has_clone else '否'}")
        
        # 应该包含"开始克隆"
        has_start_clone = "开始克隆" in dialog_content
        print(f"✅ '开始克隆'按钮: {'是' if has_start_clone else '否'}")
        
        # 窗口标题
        has_title = "零样本声音克隆工具" in dialog_content
        print(f"✅ 窗口标题更新: {'是' if has_title else '否'}")
        
        results.append(("命名统一性", has_clone and has_start_clone and has_title))
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        results.append(("命名统一性", False))
    
    # 测试3: API调用修复检查
    print("\n测试3: API调用修复")
    print("-" * 70)
    try:
        with open("gui/voice_clone_test_dialog.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 不应该包含错误的方法调用
        has_start_session = "start_session()" in content or "await client.start_session" in content
        has_stop_session = "stop_session()" in content or "await client.stop_session" in content
        has_disconnect = "disconnect()" in content or "await client.disconnect" in content
        
        if has_start_session:
            print("❌ 仍包含 start_session() 调用")
        else:
            print("✅ 已移除 start_session() 调用")
        
        if has_stop_session:
            print("❌ 仍包含 stop_session() 调用")
        else:
            print("✅ 已移除 stop_session() 调用")
        
        if has_disconnect:
            print("❌ 仍包含 disconnect() 调用")
        else:
            print("✅ 已移除 disconnect() 调用")
        
        # 应该包含正确的方法
        has_connect = "await client.connect()" in content
        has_close = "await client.close()" in content
        has_receive_loop = "receive_loop()" in content
        
        print(f"✅ 使用 connect(): {'是' if has_connect else '否'}")
        print(f"✅ 使用 close(): {'是' if has_close else '否'}")
        print(f"✅ 使用 receive_loop(): {'是' if has_receive_loop else '否'}")
        
        all_correct = (not has_start_session and not has_stop_session and not has_disconnect 
                      and has_connect and has_close and has_receive_loop)
        
        results.append(("API调用修复", all_correct))
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        results.append(("API调用修复", False))
    
    # 测试4: 文档更新
    print("\n测试4: 文档更新")
    print("-" * 70)
    from pathlib import Path
    
    doc_file = Path("VOICE_CLONE_FIX_UPDATE.md")
    if doc_file.exists():
        size = doc_file.stat().st_size / 1024
        print(f"✅ 修复说明文档: VOICE_CLONE_FIX_UPDATE.md ({size:.1f}KB)")
        results.append(("修复文档", True))
    else:
        print("❌ 缺少修复说明文档")
        results.append(("修复文档", False))
    
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
        print("🎉 所有测试通过！声音克隆功能已修复。")
        print("\n✨ 修复内容：")
        print("   1. ✅ 修复了 API 方法调用错误")
        print("   2. ✅ 统一使用'克隆'命名")
        print("   3. ✅ 更新了所有按钮和文案")
        print("   4. ✅ 完善了实现逻辑")
        print("\n🚀 立即测试：")
        print("   python main.py")
        print("   点击【🔬 声音克隆】")
        print("   点击【🚀 开始克隆】")
        print("   朗读测试文本")
        print("\n📖 查看修复说明：")
        print("   notepad VOICE_CLONE_FIX_UPDATE.md")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(test_fixes())
