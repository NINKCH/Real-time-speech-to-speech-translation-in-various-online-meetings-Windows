"""
声音复刻训练对话框
用于上传音频训练声音复刻模型
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QGroupBox, QFileDialog, QMessageBox,
    QComboBox, QCheckBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
import os


class TrainingThread(QThread):
    """训练线程"""
    progress_signal = pyqtSignal(str)
    success_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, app_key, access_token, speaker_id, audio_file, model_type, language, enable_denoise):
        super().__init__()
        self.app_key = app_key
        self.access_token = access_token
        self.speaker_id = speaker_id
        self.audio_file = audio_file
        self.model_type = model_type
        self.language = language
        self.enable_denoise = enable_denoise
    
    def run(self):
        try:
            from modules.voice_clone_trainer import VoiceCloneTrainer
            
            trainer = VoiceCloneTrainer(self.app_key, self.access_token)
            trainer.on_progress = lambda msg: self.progress_signal.emit(msg)
            trainer.on_success = lambda msg: self.success_signal.emit(msg)
            trainer.on_error = lambda msg: self.error_signal.emit(msg)
            
            # 确定resource_id
            resource_id = "seed-icl-2.0" if self.model_type == 4 else "seed-icl-1.0"
            
            result = trainer.upload_and_train(
                speaker_id=self.speaker_id,
                audio_file_path=self.audio_file,
                model_type=self.model_type,
                language=self.language,
                enable_denoise=self.enable_denoise,
                resource_id=resource_id
            )
            
            self.success_signal.emit(f"训练请求已提交！Speaker ID: {self.speaker_id}")
            
        except Exception as e:
            self.error_signal.emit(f"训练失败: {str(e)}")
        finally:
            self.finished_signal.emit()


class VoiceCloneTrainDialog(QDialog):
    """声音复刻训练对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_file_path = ""
        self.training_thread = None
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("声音复刻训练工具")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # 说明区域
        info_group = QGroupBox("📖 功能说明")
        info_layout = QVBoxLayout()
        info_text = QLabel(
            "此工具用于训练声音复刻模型，将您的声音训练成可用的 Speaker ID。\n\n"
            "训练步骤：\n"
            "1. 从控制台获取 Speaker ID (需要先购买音色，格式：S_xxxx)\n"
            "2. 录制或选择音频文件（建议20秒以上，清晰无噪音）\n"
            "3. 选择模型类型和语种\n"
            "4. 点击【开始训练】\n"
            "5. 等待训练完成（通常几分钟）\n"
            "6. 训练成功后，即可在主界面使用该 Speaker ID\n\n"
            "注意：训练需要消耗训练次数配额。"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Speaker ID配置
        speaker_group = QGroupBox("🎤 Speaker ID 配置")
        speaker_layout = QVBoxLayout()
        
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Speaker ID:"))
        self.speaker_id_input = QLineEdit()
        self.speaker_id_input.setPlaceholderText("例如: S_VYBmqB0A （从控制台获取）")
        id_layout.addWidget(self.speaker_id_input)
        speaker_layout.addLayout(id_layout)
        
        speaker_group.setLayout(speaker_layout)
        layout.addWidget(speaker_group)
        
        # 音频文件选择
        audio_group = QGroupBox("🎵 音频文件")
        audio_layout = QVBoxLayout()
        
        file_layout = QHBoxLayout()
        self.audio_file_label = QLabel("未选择文件")
        self.audio_file_label.setStyleSheet("color: gray;")
        file_layout.addWidget(self.audio_file_label)
        
        select_btn = QPushButton("选择音频")
        select_btn.clicked.connect(self.select_audio_file)
        file_layout.addWidget(select_btn)
        audio_layout.addLayout(file_layout)
        
        audio_tip = QLabel(
            "支持格式：WAV, MP3, OGG, M4A, AAC, PCM\n"
            "建议：20秒以上，清晰无噪音，单通道，16kHz或24kHz"
        )
        audio_tip.setStyleSheet("color: gray; font-size: 10px;")
        audio_layout.addWidget(audio_tip)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # 训练参数
        param_group = QGroupBox("⚙️ 训练参数")
        param_layout = QVBoxLayout()
        
        # 模型类型
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("模型类型:"))
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems([
            "ICL 2.0 (推荐，最新)",
            "ICL 1.0",
            "DiT 标准版",
            "DiT 还原版"
        ])
        self.model_type_combo.setCurrentIndex(0)
        model_layout.addWidget(self.model_type_combo)
        param_layout.addLayout(model_layout)
        
        # 语种
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("音频语种:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "中文",
            "英语",
            "日语",
            "西班牙语",
            "印尼语",
            "葡萄牙语",
            "德语",
            "法语"
        ])
        lang_layout.addWidget(self.language_combo)
        param_layout.addLayout(lang_layout)
        
        # 降噪选项
        self.denoise_checkbox = QCheckBox("开启音频降噪（样本噪声大时启用）")
        self.denoise_checkbox.setChecked(False)
        param_layout.addWidget(self.denoise_checkbox)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # 进度显示
        progress_group = QGroupBox("📊 训练进度")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_bar.hide()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        progress_layout.addWidget(self.status_text)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.console_btn = QPushButton("🌐 打开控制台")
        self.console_btn.clicked.connect(self.open_console)
        button_layout.addWidget(self.console_btn)
        
        self.doc_btn = QPushButton("📖 查看文档")
        self.doc_btn.clicked.connect(self.open_doc)
        button_layout.addWidget(self.doc_btn)
        
        button_layout.addStretch()
        
        self.train_btn = QPushButton("🚀 开始训练")
        self.train_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; }")
        self.train_btn.clicked.connect(self.start_training)
        button_layout.addWidget(self.train_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def select_audio_file(self):
        """选择音频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择音频文件",
            "",
            "音频文件 (*.wav *.mp3 *.ogg *.m4a *.aac *.pcm);;所有文件 (*.*)"
        )
        
        if file_path:
            self.audio_file_path = file_path
            file_name = Path(file_path).name
            file_size = Path(file_path).stat().st_size / 1024 / 1024  # MB
            
            if file_size > 10:
                QMessageBox.warning(
                    self,
                    "文件过大",
                    f"文件大小: {file_size:.2f}MB\n最大支持: 10MB\n\n请选择更小的文件。"
                )
                return
            
            self.audio_file_label.setText(f"✅ {file_name} ({file_size:.2f}MB)")
            self.audio_file_label.setStyleSheet("color: green;")
    
    def start_training(self):
        """开始训练"""
        # 验证输入
        speaker_id = self.speaker_id_input.text().strip()
        if not speaker_id:
            QMessageBox.warning(self, "错误", "请输入 Speaker ID")
            return
        
        if not speaker_id.startswith("S_"):
            QMessageBox.warning(self, "错误", "Speaker ID 格式错误，应以 S_ 开头")
            return
        
        if not self.audio_file_path:
            QMessageBox.warning(self, "错误", "请选择音频文件")
            return
        
        # 获取API配置
        from dotenv import load_dotenv
        load_dotenv()
        
        app_key = os.getenv("DOUBAO_APP_KEY", "")
        access_token = os.getenv("DOUBAO_ACCESS_KEY", "")
        
        if not app_key or not access_token:
            QMessageBox.warning(
                self,
                "配置错误",
                "请先在.env文件中配置 DOUBAO_APP_KEY 和 DOUBAO_ACCESS_KEY"
            )
            return
        
        # 获取参数
        model_type_map = [4, 1, 2, 3]  # ICL2.0, ICL1.0, DiT标准, DiT还原
        model_type = model_type_map[self.model_type_combo.currentIndex()]
        language = self.language_combo.currentIndex()
        enable_denoise = self.denoise_checkbox.isChecked()
        
        # 确认训练
        reply = QMessageBox.question(
            self,
            "确认训练",
            f"确认以下配置并开始训练？\n\n"
            f"Speaker ID: {speaker_id}\n"
            f"音频文件: {Path(self.audio_file_path).name}\n"
            f"模型类型: {self.model_type_combo.currentText()}\n"
            f"语种: {self.language_combo.currentText()}\n"
            f"降噪: {'开启' if enable_denoise else '关闭'}\n\n"
            f"注意：训练将消耗训练次数配额。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # 禁用按钮
        self.train_btn.setEnabled(False)
        self.progress_bar.show()
        self.status_text.append("🚀 开始训练...\n")
        
        # 创建训练线程
        self.training_thread = TrainingThread(
            app_key, access_token, speaker_id,
            self.audio_file_path, model_type, language, enable_denoise
        )
        
        # 连接信号
        self.training_thread.progress_signal.connect(self.on_progress)
        self.training_thread.success_signal.connect(self.on_success)
        self.training_thread.error_signal.connect(self.on_error)
        self.training_thread.finished_signal.connect(self.on_finished)
        
        # 启动线程
        self.training_thread.start()
    
    def on_progress(self, message):
        """进度更新"""
        self.status_text.append(f"📝 {message}")
    
    def on_success(self, message):
        """成功"""
        self.status_text.append(f"\n✅ {message}\n")
        QMessageBox.information(
            self,
            "训练成功",
            f"{message}\n\n"
            "训练已开始，通常需要几分钟完成。\n"
            "您可以：\n"
            "1. 在控制台查看训练状态\n"
            "2. 训练完成后在主界面配置此 Speaker ID"
        )
    
    def on_error(self, message):
        """错误"""
        self.status_text.append(f"\n❌ {message}\n")
        QMessageBox.critical(self, "训练失败", message)
    
    def on_finished(self):
        """完成"""
        self.train_btn.setEnabled(True)
        self.progress_bar.hide()
    
    def open_console(self):
        """打开控制台"""
        import webbrowser
        webbrowser.open("https://console.volcengine.com/speech/service")
    
    def open_doc(self):
        """打开文档"""
        import webbrowser
        doc_path = Path("VOICE_CLONE_GUIDE.md").absolute()
        if doc_path.exists():
            webbrowser.open(str(doc_path))
        else:
            webbrowser.open("https://www.volcengine.com/docs/6561/")


# 测试代码
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = VoiceCloneTrainDialog()
    dialog.exec()
    sys.exit(0)
