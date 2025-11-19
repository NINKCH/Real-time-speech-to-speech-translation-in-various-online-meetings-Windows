"""
完整的声音克隆功能测试
包括配置和训练功能
"""
import sys
from pathlib import Path

def test_all():
    """测试所有声音克隆相关功能"""
    print("\n" + "=" * 70)
    print("声音克隆功能完整测试")
    print("=" * 70 + "\n")
    
    results = []
    
    # 测试1: 导入模块
    print("测试1: 导入所有模块")
    print("-" * 70)
    try:
        from modules.voice_clone_trainer import VoiceCloneTrainer
        print("✅ VoiceCloneTrainer 模块导入成功")
        results.append(("训练模块", True))
    except Exception as e:
        print(f"❌ VoiceCloneTrainer 导入失败: {e}")
        results.append(("训练模块", False))
    
    try:
        from gui.voice_clone_dialog import VoiceCloneDialog
        print("✅ VoiceCloneDialog 导入成功")
        results.append(("配置对话框", True))
    except Exception as e:
        print(f"❌ VoiceCloneDialog 导入失败: {e}")
        results.append(("配置对话框", False))
    
    try:
        from gui.voice_clone_train_dialog import VoiceCloneTrainDialog
        print("✅ VoiceCloneTrainDialog 导入成功")
        results.append(("训练对话框", True))
    except Exception as e:
        print(f"❌ VoiceCloneTrainDialog 导入失败: {e}")
        results.append(("训练对话框", False))
    
    try:
        from gui.main_window import MainWindow
        print("✅ MainWindow 导入成功")
        results.append(("主窗口", True))
    except Exception as e:
        print(f"❌ MainWindow 导入失败: {e}")
        results.append(("主窗口", False))
    
    # 测试2: VoiceCloneTrainer功能
    print("\n测试2: VoiceCloneTrainer 功能")
    print("-" * 70)
    try:
        from modules.voice_clone_trainer import VoiceCloneTrainer
        
        trainer = VoiceCloneTrainer("test_key", "test_token")
        
        # 测试属性
        assert hasattr(trainer, 'upload_and_train'), "缺少 upload_and_train 方法"
        assert hasattr(trainer, 'check_status'), "缺少 check_status 方法"
        assert hasattr(trainer, 'MODEL_TYPE_ICL_2_0'), "缺少模型类型常量"
        assert hasattr(trainer, 'LANGUAGE_CN'), "缺少语言常量"
        
        # 测试模型类型
        assert trainer.MODEL_TYPE_ICL_2_0 == 4, "ICL 2.0 模型类型错误"
        assert trainer.MODEL_TYPE_ICL_1_0 == 1, "ICL 1.0 模型类型错误"
        
        # 测试语言
        assert trainer.LANGUAGE_CN == 0, "中文语言代码错误"
        assert trainer.LANGUAGE_EN == 1, "英文语言代码错误"
        
        print("✅ VoiceCloneTrainer 功能测试通过")
        print(f"   - 支持模型类型: MEGA(0), ICL1.0(1), DiT标准(2), DiT还原(3), ICL2.0(4)")
        print(f"   - 支持语言: CN(0), EN(1), JA(2), ES(3), ID(4), PT(5), DE(6), FR(7)")
        results.append(("训练器功能", True))
    except Exception as e:
        print(f"❌ VoiceCloneTrainer 功能测试失败: {e}")
        results.append(("训练器功能", False))
    
    # 测试3: 文件完整性
    print("\n测试3: 文件完整性检查")
    print("-" * 70)
    files_to_check = [
        ("训练模块", "modules/voice_clone_trainer.py"),
        ("配置对话框", "gui/voice_clone_dialog.py"),
        ("训练对话框", "gui/voice_clone_train_dialog.py"),
        ("主窗口", "gui/main_window.py"),
        ("使用指南", "VOICE_CLONE_GUIDE.md"),
        ("更新说明", "VOICE_CLONE_TRAIN_UPDATE.md"),
        ("功能更新", "FEATURE_UPDATE.md"),
    ]
    
    for name, file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size / 1024  # KB
            print(f"✅ {name:15s} - {file_path:40s} ({size:.1f}KB)")
            results.append((f"文件-{name}", True))
        else:
            print(f"❌ {name:15s} - {file_path:40s} (不存在)")
            results.append((f"文件-{name}", False))
    
    # 测试4: GUI组件
    print("\n测试4: GUI组件功能")
    print("-" * 70)
    try:
        from PyQt6.QtWidgets import QApplication
        from gui.voice_clone_train_dialog import VoiceCloneTrainDialog
        
        # 创建应用（测试环境）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建对话框
        dialog = VoiceCloneTrainDialog()
        
        # 检查组件
        assert hasattr(dialog, 'speaker_id_input'), "缺少 speaker_id_input"
        assert hasattr(dialog, 'audio_file_label'), "缺少 audio_file_label"
        assert hasattr(dialog, 'model_type_combo'), "缺少 model_type_combo"
        assert hasattr(dialog, 'language_combo'), "缺少 language_combo"
        assert hasattr(dialog, 'train_btn'), "缺少 train_btn"
        assert hasattr(dialog, 'progress_bar'), "缺少 progress_bar"
        
        # 检查下拉框选项
        assert dialog.model_type_combo.count() == 4, "模型类型数量不对"
        assert dialog.language_combo.count() == 8, "语言数量不对"
        
        print("✅ GUI组件测试通过")
        print(f"   - Speaker ID输入框: ✓")
        print(f"   - 音频文件选择: ✓")
        print(f"   - 模型类型选择: 4种")
        print(f"   - 语言选择: 8种")
        print(f"   - 训练按钮: ✓")
        print(f"   - 进度条: ✓")
        results.append(("GUI组件", True))
        
        # 清理
        dialog.close()
        
    except Exception as e:
        print(f"❌ GUI组件测试失败: {e}")
        results.append(("GUI组件", False))
    
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
        print("🎉 所有测试通过！声音克隆完整功能已准备就绪。")
        print("\n📖 功能说明：")
        print("1. 🎤 配置声音 - 快速配置已有的 Speaker ID")
        print("2. 🔬 训练工具 - 上传音频训练新的声音复刻模型")
        print("\n🚀 启动应用：")
        print("   python main.py")
        print("\n📚 查看文档：")
        print("   - VOICE_CLONE_GUIDE.md (使用指南)")
        print("   - VOICE_CLONE_TRAIN_UPDATE.md (训练功能说明)")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(test_all())
