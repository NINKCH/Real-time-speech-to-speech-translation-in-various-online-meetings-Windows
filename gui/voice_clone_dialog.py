"""
声音克隆管理对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QGroupBox, QFileDialog, QMessageBox,
    QComboBox, QCheckBox, QProgressBar, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
import json
import os


class VoiceCloneDialog(QDialog):
    """声音克隆管理对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.speaker_id = ""
        self.init_ui()
        self.load_saved_speaker_id()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("声音克隆管理")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # 说明区域
        info_group = QGroupBox("📖 功能说明")
        info_layout = QVBoxLayout()
        info_text = QLabel(
            "声音克隆功能可以让翻译后的语音使用您自己的声音。\n\n"
            "使用步骤：\n"
            "1. 访问豆包控制台：https://console.volcengine.com/speech/service\n"
            "2. 进入【语音合成】服务\n"
            "3. 创建或选择【音色定制】功能\n"
            "4. 录制您的声音样本（通常需要20-30分钟的录音）\n"
            "5. 训练完成后获取 Speaker ID\n"
            "6. 将 Speaker ID 粘贴到下方输入框\n\n"
            "注意：声音克隆功能需要额外的配置和费用，请先在控制台开通。"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Speaker ID输入区域
        speaker_group = QGroupBox("🎤 Speaker ID 配置")
        speaker_layout = QVBoxLayout()
        
        # 输入框
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Speaker ID:"))
        self.speaker_id_input = QLineEdit()
        self.speaker_id_input.setPlaceholderText("例如: voice_12345678")
        self.speaker_id_input.textChanged.connect(self.on_speaker_id_changed)
        input_layout.addWidget(self.speaker_id_input)
        speaker_layout.addLayout(input_layout)
        
        # 状态提示
        self.status_label = QLabel("未配置声音克隆")
        self.status_label.setStyleSheet("color: gray;")
        speaker_layout.addWidget(self.status_label)
        
        speaker_group.setLayout(speaker_layout)
        layout.addWidget(speaker_group)
        
        # 测试区域（预留）
        test_group = QGroupBox("🧪 测试（暂未实现）")
        test_layout = QVBoxLayout()
        test_info = QLabel(
            "完整的声音克隆测试功能需要:\n"
            "1. 上传声音样本文件\n"
            "2. 训练声音模型\n"
            "3. 测试生成效果\n\n"
            "目前建议直接在豆包控制台完成声音克隆，然后将获得的 Speaker ID 填入上方。"
        )
        test_info.setWordWrap(True)
        test_info.setStyleSheet("color: gray;")
        test_layout.addWidget(test_info)
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.open_console_btn = QPushButton("🌐 打开控制台")
        self.open_console_btn.clicked.connect(self.open_console)
        button_layout.addWidget(self.open_console_btn)
        
        button_layout.addStretch()
        
        self.clear_btn = QPushButton("清除")
        self.clear_btn.clicked.connect(self.clear_speaker_id)
        button_layout.addWidget(self.clear_btn)
        
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_speaker_id)
        button_layout.addWidget(self.save_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_speaker_id_changed(self, text):
        """Speaker ID输入变化"""
        if text.strip():
            self.status_label.setText(f"✅ 已配置: {text}")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("未配置声音克隆")
            self.status_label.setStyleSheet("color: gray;")
    
    def open_console(self):
        """打开控制台"""
        import webbrowser
        webbrowser.open("https://console.volcengine.com/speech/service")
    
    def clear_speaker_id(self):
        """清除Speaker ID"""
        reply = QMessageBox.question(
            self,
            "确认清除",
            "确定要清除已保存的 Speaker ID 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.speaker_id_input.clear()
    
    def save_speaker_id(self):
        """保存Speaker ID"""
        speaker_id = self.speaker_id_input.text().strip()
        
        if not speaker_id:
            QMessageBox.warning(self, "警告", "请先输入 Speaker ID")
            return
        
        self.speaker_id = speaker_id
        
        # 保存到配置文件
        config_file = Path("voice_clone_config.json")
        try:
            config = {"speaker_id": speaker_id}
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            
            QMessageBox.information(
                self,
                "保存成功",
                f"Speaker ID 已保存！\n\n"
                f"ID: {speaker_id}\n\n"
                f"在主界面点击【开始翻译】时，将使用此声音进行翻译。"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")
    
    def load_saved_speaker_id(self):
        """加载已保存的Speaker ID"""
        config_file = Path("voice_clone_config.json")
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    speaker_id = config.get("speaker_id", "")
                    if speaker_id:
                        self.speaker_id_input.setText(speaker_id)
                        self.speaker_id = speaker_id
            except Exception as e:
                print(f"加载声音克隆配置失败: {e}")
    
    def get_speaker_id(self) -> str:
        """获取Speaker ID"""
        return self.speaker_id


# 测试代码
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = VoiceCloneDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        print(f"设置的 Speaker ID: {dialog.get_speaker_id()}")
    sys.exit(0)
