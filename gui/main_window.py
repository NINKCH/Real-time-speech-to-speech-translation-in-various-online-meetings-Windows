from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QGroupBox,
    QComboBox, QMessageBox, QStatusBar, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor
import json
from pathlib import Path
from utils.i18n import tr, get_language, set_language, get_translated_languages


class MainWindow(QMainWindow):
    source_text_signal = pyqtSignal(str, bool)
    translation_text_signal = pyqtSignal(str, bool)
    status_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.translator_app = None
        self.settings = self.load_settings()
        self.init_ui()
        
        self.source_text_signal.connect(self._update_source_text)
        self.translation_text_signal.connect(self._update_translation_text)
        self.status_signal.connect(self._update_status)
        self.error_signal.connect(self._show_error)
    
    def init_ui(self):
        self.setWindowTitle(f"{tr('app_title')} - Realtime AST Translator")
        self.setGeometry(100, 100, 900, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        config_group = self.create_config_section()
        main_layout.addWidget(config_group)
        
        control_layout = self.create_control_section()
        main_layout.addLayout(control_layout)
        
        text_layout = self.create_text_section()
        main_layout.addLayout(text_layout)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(tr("status_ready"))
    
    def create_config_section(self) -> QGroupBox:
        group = QGroupBox(tr("translation_config"))
        layout = QHBoxLayout()
        
        layout.addWidget(QLabel(tr("source_language")))
        self.source_lang_combo = QComboBox()
        languages = get_translated_languages()
        self.source_lang_combo.addItems(languages)
        self.source_lang_combo.setCurrentText(self.settings.get("source_language", "中文(zh)"))
        layout.addWidget(self.source_lang_combo)
        
        layout.addWidget(QLabel("→"))
        
        layout.addWidget(QLabel(tr("target_language")))
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems(languages)
        self.target_lang_combo.setCurrentText(self.settings.get("target_language", "英语(en)"))
        layout.addWidget(self.target_lang_combo)
        
        layout.addWidget(QLabel(tr("mode")))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([tr("mode_s2s"), tr("mode_s2t")])
        self.mode_combo.setCurrentIndex(0 if self.settings.get("mode", "s2s") == "s2s" else 1)
        layout.addWidget(self.mode_combo)
        
        self.debug_checkbox = QCheckBox(tr("debug_mode"))
        self.debug_checkbox.setChecked(self.settings.get("debug_mode", False))
        self.debug_checkbox.setToolTip(tr("debug_mode_tooltip"))
        layout.addWidget(self.debug_checkbox)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def create_control_section(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        
        self.start_btn = QPushButton(tr("btn_start"))
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-size: 14px; }")
        self.start_btn.clicked.connect(self.start_translation)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton(tr("btn_stop"))
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 10px; font-size: 14px; }")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_translation)
        layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton(tr("btn_clear"))
        self.clear_btn.clicked.connect(self.clear_text)
        layout.addWidget(self.clear_btn)
        
        self.settings_btn = QPushButton(tr("btn_settings"))
        self.settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(self.settings_btn)
        
        self.voice_info_btn = QPushButton(tr("btn_info"))
        self.voice_info_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 10px; font-size: 14px; }")
        self.voice_info_btn.clicked.connect(self.show_voice_info)
        self.voice_info_btn.setToolTip(tr("btn_info_tooltip"))
        layout.addWidget(self.voice_info_btn)
        
        self.voice_test_btn = QPushButton(tr("btn_voice_clone"))
        self.voice_test_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 10px; font-size: 14px; }")
        self.voice_test_btn.clicked.connect(self.show_voice_test)
        self.voice_test_btn.setToolTip(tr("btn_voice_clone_tooltip"))
        layout.addWidget(self.voice_test_btn)
        
        lang_btn = QPushButton(tr("btn_language"))
        lang_btn.clicked.connect(self.toggle_language)
        layout.addWidget(lang_btn)
        
        return layout
    
    def create_text_section(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        
        source_group = QGroupBox(tr("original_text"))
        source_layout = QVBoxLayout()
        self.source_text = QTextEdit()
        self.source_text.setReadOnly(True)
        self.source_text.setFont(QFont("Segoe UI", 11))
        source_layout.addWidget(self.source_text)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        translation_group = QGroupBox(tr("translated_text"))
        translation_layout = QVBoxLayout()
        self.translation_text = QTextEdit()
        self.translation_text.setReadOnly(True)
        self.translation_text.setFont(QFont("Segoe UI", 11))
        translation_layout.addWidget(self.translation_text)
        translation_group.setLayout(translation_layout)
        layout.addWidget(translation_group)
        
        return layout
    
    def start_translation(self):
        try:
            source_lang = self.source_lang_combo.currentText().split("(")[1].rstrip(")")
            target_lang = self.target_lang_combo.currentText().split("(")[1].rstrip(")")
            mode = "s2s" if self.mode_combo.currentIndex() == 0 else "s2t"
            
            self.settings["source_language"] = self.source_lang_combo.currentText()
            self.settings["target_language"] = self.target_lang_combo.currentText()
            self.settings["mode"] = mode
            self.settings["debug_mode"] = self.debug_checkbox.isChecked()
            self.save_settings()
            
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            app_key = os.getenv("DOUBAO_APP_KEY", "")
            access_key = os.getenv("DOUBAO_ACCESS_KEY", "")
            
            if not app_key or not access_key:
                QMessageBox.warning(
                    self,
                    tr("error_config"),
                    tr("error_config_msg")
                )
                return
            
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
            
            self.translator_app.on_source_text_callback = lambda text, is_final: self.source_text_signal.emit(text, is_final)
            self.translator_app.on_translation_text_callback = lambda text, is_final: self.translation_text_signal.emit(text, is_final)
            self.translator_app.on_status_callback = lambda status: self.status_signal.emit(status)
            self.translator_app.on_error_callback = lambda error: self.error_signal.emit(error)
            
            if self.translator_app.start():
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.source_lang_combo.setEnabled(False)
                self.target_lang_combo.setEnabled(False)
                self.mode_combo.setEnabled(False)
                self.debug_checkbox.setEnabled(False)
            else:
                QMessageBox.critical(self, tr("error_start"), tr("error_start_msg"))
                
        except Exception as e:
            QMessageBox.critical(self, tr("error"), f"{tr('error_start')}: {str(e)}")
    
    def stop_translation(self):
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
        self.source_text.clear()
        self.translation_text.clear()
    
    def show_settings(self):
        from gui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def _update_source_text(self, text: str, is_final: bool):
        if is_final:
            self.source_text.append(f"<b>{text}</b>")
        else:
            cursor = self.source_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(f"{text} ")
    
    def _update_translation_text(self, text: str, is_final: bool):
        if is_final:
            self.translation_text.append(f"<b>{text}</b>")
        else:
            cursor = self.translation_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(f"{text} ")
    
    def _update_status(self, status: str):
        self.status_bar.showMessage(status)
    
    def _show_error(self, error: str):
        self.status_bar.showMessage(f"{tr('error')}: {error}")
        QMessageBox.warning(self, tr("error"), error)
    
    def load_settings(self) -> dict:
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
        settings_file = Path("user_settings.json")
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Save settings failed: {e}")
    
    def show_voice_info(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(tr("voice_clone_title"))
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(tr("voice_clone_info"))
        
        view_doc_btn = msg.addButton(tr("btn_view_doc"), QMessageBox.ButtonRole.ActionRole)
        test_btn = msg.addButton(tr("btn_test_clone"), QMessageBox.ButtonRole.ActionRole)
        msg.addButton(tr("btn_close"), QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        clicked = msg.clickedButton()
        if clicked == view_doc_btn:
            import webbrowser
            doc_path = Path("ZERO_SHOT_VOICE_CLONING.md").absolute()
            if doc_path.exists():
                webbrowser.open(str(doc_path))
            else:
                QMessageBox.warning(self, tr("hint"), tr("doc_not_found"))
        elif clicked == test_btn:
            self.show_voice_test()
    
    def show_voice_test(self):
        from gui.voice_clone_test_dialog import VoiceCloneTestDialog
        dialog = VoiceCloneTestDialog(self)
        dialog.exec()
    
    def toggle_language(self):
        new_lang = "zh" if get_language() == "en" else "en"
        set_language(new_lang)
        self._refresh_ui()
    
    def _refresh_ui(self):
        self.setWindowTitle(f"{tr('app_title')} - Realtime AST Translator")
        self.status_bar.showMessage(tr("status_ready"))
        
        self.source_lang_combo.clear()
        self.source_lang_combo.addItems(get_translated_languages())
        self.target_lang_combo.clear()
        self.target_lang_combo.addItems(get_translated_languages())
        
        self.mode_combo.clear()
        self.mode_combo.addItems([tr("mode_s2s"), tr("mode_s2t")])
        self.mode_combo.setCurrentIndex(0 if self.settings.get("mode", "s2s") == "s2s" else 1)
        
        self.debug_checkbox.setText(tr("debug_mode"))
        self.debug_checkbox.setToolTip(tr("debug_mode_tooltip"))
        
        self.start_btn.setText(tr("btn_start"))
        self.stop_btn.setText(tr("btn_stop"))
        self.clear_btn.setText(tr("btn_clear"))
        self.settings_btn.setText(tr("btn_settings"))
        self.voice_info_btn.setText(tr("btn_info"))
        self.voice_info_btn.setToolTip(tr("btn_info_tooltip"))
        self.voice_test_btn.setText(tr("btn_voice_clone"))
        self.voice_test_btn.setToolTip(tr("btn_voice_clone_tooltip"))
    
    def closeEvent(self, event):
        if self.translator_app:
            self.stop_translation()
        event.accept()
