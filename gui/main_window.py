"""
GUI主窗口
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QGroupBox,
    QComboBox, QMessageBox, QStatusBar, QCheckBox
)
# 声音复刻相关导入已移除，因为同传2.0内置零样本声音复刻，无需额外配置
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor
import json
from pathlib import Path


class MainWindow(QMainWindow):
    """主窗口"""
    
    # 信号
    source_text_signal = pyqtSignal(str, bool)
    translation_text_signal = pyqtSignal(str, bool)
    status_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.translator_app = None
        self.settings = self.load_settings()
        self.init_ui()
        
        # 连接信号
        self.source_text_signal.connect(self._update_source_text)
        self.translation_text_signal.connect(self._update_translation_text)
        self.status_signal.connect(self._update_status)
        self.error_signal.connect(self._show_error)
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("豆包实时同声传译 - Realtime AST Translator")
        self.setGeometry(100, 100, 900, 700)
        
        # 中心widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 配置区域
        config_group = self.create_config_section()
        main_layout.addWidget(config_group)
        
        # 控制按钮
        control_layout = self.create_control_section()
        main_layout.addLayout(control_layout)
        
        # 文本显示区域
        text_layout = self.create_text_section()
        main_layout.addLayout(text_layout)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def create_config_section(self) -> QGroupBox:
        """创建配置区域"""
        group = QGroupBox("翻译配置")
        layout = QHBoxLayout()
        
        # 源语言
        layout.addWidget(QLabel("源语言:"))
        self.source_lang_combo = QComboBox()
        languages = [
            "中文(zh)", "英语(en)", "日语(ja)", "韩语(ko)",
            "西班牙语(es)", "法语(fr)", "德语(de)", "俄语(ru)",
            "阿拉伯语(ar)", "葡萄牙语(pt)", "意大利语(it)"
        ]
        self.source_lang_combo.addItems(languages)
        self.source_lang_combo.setCurrentText(self.settings.get("source_language", "中文(zh)"))
        layout.addWidget(self.source_lang_combo)
        
        # 箭头
        layout.addWidget(QLabel("→"))
        
        # 目标语言
        layout.addWidget(QLabel("目标语言:"))
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems(languages)
        self.target_lang_combo.setCurrentText(self.settings.get("target_language", "英语(en)"))
        layout.addWidget(self.target_lang_combo)
        
        # 模式
        layout.addWidget(QLabel("模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["s2s (语音到语音)", "s2t (语音到文本)"])
        self.mode_combo.setCurrentIndex(0 if self.settings.get("mode", "s2s") == "s2s" else 1)
        layout.addWidget(self.mode_combo)
        
        # 调试模式复选框
        self.debug_checkbox = QCheckBox("调试模式")
        self.debug_checkbox.setChecked(self.settings.get("debug_mode", False))
        self.debug_checkbox.setToolTip("启用后将保存音频文件到audio_debug目录用于调试")
        layout.addWidget(self.debug_checkbox)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def create_control_section(self) -> QHBoxLayout:
        """创建控制按钮区域"""
        layout = QHBoxLayout()
        
        # 开始按钮
        self.start_btn = QPushButton("▶ 开始翻译")
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-size: 14px; }")
        self.start_btn.clicked.connect(self.start_translation)
        layout.addWidget(self.start_btn)
        
        # 停止按钮
        self.stop_btn = QPushButton("■ 停止")
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 10px; font-size: 14px; }")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_translation)
        layout.addWidget(self.stop_btn)
        
        # 清空按钮
        clear_btn = QPushButton("🗑 清空")
        clear_btn.clicked.connect(self.clear_text)
        layout.addWidget(clear_btn)
        
        # 设置按钮
        settings_btn = QPushButton("⚙ 设置")
        settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(settings_btn)
        
        # 声音复刻说明按钮
        voice_info_btn = QPushButton("ℹ️ 功能说明")
        voice_info_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 10px; font-size: 14px; }")
        voice_info_btn.clicked.connect(self.show_voice_info)
        voice_info_btn.setToolTip("了解零样本声音复刻功能")
        layout.addWidget(voice_info_btn)
        
        # 声音克隆按钮
        voice_test_btn = QPushButton("🔬 声音克隆")
        voice_test_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 10px; font-size: 14px; }")
        voice_test_btn.clicked.connect(self.show_voice_test)
        voice_test_btn.setToolTip("测试零样本声音克隆功能")
        layout.addWidget(voice_test_btn)
        
        return layout
    
    def create_text_section(self) -> QHBoxLayout:
        """创建文本显示区域"""
        layout = QHBoxLayout()
        
        # 原文区域
        source_group = QGroupBox("原文")
        source_layout = QVBoxLayout()
        self.source_text = QTextEdit()
        self.source_text.setReadOnly(True)
        self.source_text.setFont(QFont("Microsoft YaHei UI", 11))
        source_layout.addWidget(self.source_text)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # 译文区域
        translation_group = QGroupBox("译文")
        translation_layout = QVBoxLayout()
        self.translation_text = QTextEdit()
        self.translation_text.setReadOnly(True)
        self.translation_text.setFont(QFont("Microsoft YaHei UI", 11))
        translation_layout.addWidget(self.translation_text)
        translation_group.setLayout(translation_layout)
        layout.addWidget(translation_group)
        
        return layout
    
    def start_translation(self):
        """开始翻译"""
        try:
            # 获取配置
            source_lang = self.source_lang_combo.currentText().split("(")[1].rstrip(")")
            target_lang = self.target_lang_combo.currentText().split("(")[1].rstrip(")")
            mode = "s2s" if self.mode_combo.currentIndex() == 0 else "s2t"
            
            # 保存设置
            self.settings["source_language"] = self.source_lang_combo.currentText()
            self.settings["target_language"] = self.target_lang_combo.currentText()
            self.settings["mode"] = mode
            self.settings["debug_mode"] = self.debug_checkbox.isChecked()
            self.save_settings()
            
            # 检查API密钥
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            app_key = os.getenv("DOUBAO_APP_KEY", "")
            access_key = os.getenv("DOUBAO_ACCESS_KEY", "")
            
            if not app_key or not access_key:
                QMessageBox.warning(
                    self,
                    "配置错误",
                    "请先在.env文件中配置 DOUBAO_APP_KEY 和 DOUBAO_ACCESS_KEY\n\n"
                    "获取地址：https://console.volcengine.com/"
                )
                return
            
            # 创建翻译应用
            from translator_app import RealtimeTranslatorApp
            debug_mode = self.debug_checkbox.isChecked()
            self.translator_app = RealtimeTranslatorApp(
                app_key, 
                access_key,
                mode=mode,
                source_language=source_lang,
                target_language=target_lang,
                debug_mode=debug_mode
            )
            
            # 设置回调
            self.translator_app.on_source_text_callback = lambda text, is_final: self.source_text_signal.emit(text, is_final)
            self.translator_app.on_translation_text_callback = lambda text, is_final: self.translation_text_signal.emit(text, is_final)
            self.translator_app.on_status_callback = lambda status: self.status_signal.emit(status)
            self.translator_app.on_error_callback = lambda error: self.error_signal.emit(error)
            
            # 启动
            if self.translator_app.start():
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.source_lang_combo.setEnabled(False)
                self.target_lang_combo.setEnabled(False)
                self.mode_combo.setEnabled(False)
                self.debug_checkbox.setEnabled(False)
            else:
                QMessageBox.critical(self, "启动失败", "无法启动翻译服务，请检查网络连接和API配置")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动失败：{str(e)}")
    
    def stop_translation(self):
        """停止翻译"""
        if self.translator_app:
            self.translator_app.stop()
            self.translator_app = None
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.source_lang_combo.setEnabled(True)
        self.target_lang_combo.setEnabled(True)
        self.mode_combo.setEnabled(True)
        self.debug_checkbox.setEnabled(True)
    
    def clear_text(self):
        """清空文本"""
        self.source_text.clear()
        self.translation_text.clear()
    
    def show_settings(self):
        """显示设置对话框"""
        from gui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def _update_source_text(self, text: str, is_final: bool):
        """更新原文"""
        if is_final:
            self.source_text.append(f"<b>{text}</b>")
        else:
            # 临时显示
            cursor = self.source_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(f"{text} ")
    
    def _update_translation_text(self, text: str, is_final: bool):
        """更新译文"""
        if is_final:
            self.translation_text.append(f"<b>{text}</b>")
        else:
            cursor = self.translation_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(f"{text} ")
    
    def _update_status(self, status: str):
        """更新状态"""
        self.status_bar.showMessage(status)
    
    def _show_error(self, error: str):
        """显示错误"""
        self.status_bar.showMessage(f"错误: {error}")
        QMessageBox.warning(self, "错误", error)
    
    def load_settings(self) -> dict:
        """加载设置"""
        settings_file = Path("user_settings.json")
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "source_language": "中文(zh)",
            "target_language": "英语(en)",
            "mode": "s2s"
        }
    
    def save_settings(self):
        """保存设置"""
        settings_file = Path("user_settings.json")
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def show_voice_info(self):
        """显示声音复刻说明"""
        msg = QMessageBox(self)
        msg.setWindowTitle("🎤 零样本声音复刻")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(
            "豆包同声传译2.0 内置零样本声音复刻功能！\n\n"
            "✨ 自动启用，无需配置\n"
            "✨ 边说话边学习您的音色\n"
            "✨ 翻译时自动使用您的声音\n\n"
            "只需：\n"
            "1. 确保模式选择【s2s (语音到语音)】\n"
            "2. 点击【▶ 开始翻译】\n"
            "3. 对着麦克风说话\n"
            "4. 听您自己的声音说英文！\n\n"
            "💡 想测试克隆效果？\n"
            "点击【🔬 声音克隆】按钮进行测试！"
        )
        
        # 添加按钮
        view_doc_btn = msg.addButton("查看文档", QMessageBox.ButtonRole.ActionRole)
        test_btn = msg.addButton("测试克隆", QMessageBox.ButtonRole.ActionRole)
        msg.addButton("关闭", QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        # 处理按钮点击
        clicked = msg.clickedButton()
        if clicked == view_doc_btn:
            import webbrowser
            doc_path = Path("ZERO_SHOT_VOICE_CLONING.md").absolute()
            if doc_path.exists():
                webbrowser.open(str(doc_path))
            else:
                QMessageBox.warning(self, "提示", "文档文件不存在")
        elif clicked == test_btn:
            self.show_voice_test()
    
    def show_voice_test(self):
        """显示声音克隆测试对话框"""
        from gui.voice_clone_test_dialog import VoiceCloneTestDialog
        dialog = VoiceCloneTestDialog(self)
        dialog.exec()
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.translator_app:
            self.stop_translation()
        event.accept()
