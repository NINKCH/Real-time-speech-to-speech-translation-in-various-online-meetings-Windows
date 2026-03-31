from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QProgressBar, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from pathlib import Path
import wave
import numpy as np
from datetime import datetime
import os

from utils.i18n import tr


class VoiceCloneTestThread(QThread):

    progress_signal = pyqtSignal(str)
    audio_signal = pyqtSignal(np.ndarray, int)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, app_key, access_key, test_text):
        super().__init__()
        self.app_key = app_key
        self.access_key = access_key
        self.test_text = test_text
        self.is_running = True
        self.collected_audio = []
    
    def run(self):
        try:
            import asyncio
            from modules.ast_client_protobuf import ASTClientProtobuf
            from modules.audio_capture import AudioCapture
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(self._test_voice_clone())
            finally:
                loop.close()
                
        except Exception as e:
            self.error_signal.emit(f"测试失败: {str(e)}")
        finally:
            self.finished_signal.emit()
    
    async def _test_voice_clone(self):
        from modules.ast_client_protobuf import ASTClientProtobuf
        from modules.audio_capture import AudioCapture
        
        self.progress_signal.emit("🎤 初始化音频采集...")
        
        client = ASTClientProtobuf(self.app_key, self.access_key)
        client.set_config(
            mode="s2s",
            source_language="zh",
            target_language="en",
            source_audio_rate=16000,
            target_audio_rate=24000
        )
        
        def on_audio(audio_data):
            self.collected_audio.append(audio_data)
            self.progress_signal.emit(f"📊 已收集音频片段: {len(self.collected_audio)}")
        
        client.on_tts_audio = on_audio
        
        self.progress_signal.emit("🔌 连接服务器并启动会话...")
        if not await client.connect():
            self.error_signal.emit("连接失败")
            return
        
        self.progress_signal.emit("📡 启动接收循环...")
        receive_task = asyncio.create_task(client.receive_loop())
        
        audio_capture = AudioCapture()
        
        def on_audio_captured(audio_chunk):
            if self.is_running:
                import asyncio
                asyncio.create_task(client.send_audio(audio_chunk))
        
        audio_capture.on_audio_callback = on_audio_captured
        
        self.progress_signal.emit(f"🎤 开始录音，请朗读:\n\n【{self.test_text}】\n")
        audio_capture.start()
        
        import asyncio
        for i in range(10):
            if not self.is_running:
                break
            await asyncio.sleep(1)
            self.progress_signal.emit(f"⏱️ 录音中... {i+1}/10秒")
        
        audio_capture.stop()
        self.progress_signal.emit("⏹️ 录音结束")
        
        self.progress_signal.emit("⏳ 等待音频生成...")
        await asyncio.sleep(3)
        
        await client.close()
        
        if self.collected_audio:
            self.progress_signal.emit(f"✅ 克隆成功！收到 {len(self.collected_audio)} 个音频片段")
            combined_audio = np.concatenate(self.collected_audio)
            self.audio_signal.emit(combined_audio, 24000)
        else:
            self.error_signal.emit("未收到克隆的音频")
    
    def stop(self):
        self.is_running = False


class VoiceCloneTestDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_thread = None
        self.cloned_audio = None
        self.cloned_sample_rate = 24000
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(tr("voice_clone_tool_title"))
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        info_group = QGroupBox(tr("feature_desc_group"))
        info_layout = QVBoxLayout()
        info_text = QLabel(tr("feature_desc_text"))
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        text_group = QGroupBox(tr("clone_text_group"))
        text_layout = QVBoxLayout()
        self.test_text_label = QLabel(tr("clone_test_text"))
        self.test_text_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 15px; "
            "background-color: #f0f0f0; border-radius: 5px;"
        )
        self.test_text_label.setWordWrap(True)
        text_layout.addWidget(self.test_text_label)
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)
        
        progress_group = QGroupBox(tr("clone_progress_group"))
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        self.status_text.setStyleSheet("font-family: 'Consolas', monospace;")
        progress_layout.addWidget(self.status_text)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        result_group = QGroupBox(tr("clone_result_group"))
        result_layout = QVBoxLayout()
        
        self.result_label = QLabel(tr("waiting_clone"))
        self.result_label.setStyleSheet("color: gray; font-size: 14px;")
        result_layout.addWidget(self.result_label)
        
        audio_btn_layout = QHBoxLayout()
        
        self.play_btn = QPushButton(tr("btn_play_clone"))
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self.play_cloned_audio)
        self.play_btn.setStyleSheet("padding: 10px; font-size: 13px;")
        audio_btn_layout.addWidget(self.play_btn)
        
        self.save_btn = QPushButton(tr("btn_save_sample"))
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_cloned_audio)
        self.save_btn.setStyleSheet("padding: 10px; font-size: 13px;")
        audio_btn_layout.addWidget(self.save_btn)
        
        result_layout.addLayout(audio_btn_layout)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        button_layout = QHBoxLayout()
        
        self.test_btn = QPushButton(tr("btn_start_clone"))
        self.test_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; "
            "padding: 15px; font-size: 15px; font-weight: bold; }"
        )
        self.test_btn.clicked.connect(self.start_test)
        button_layout.addWidget(self.test_btn)
        
        self.stop_btn = QPushButton(tr("btn_stop_clone"))
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_test)
        button_layout.addWidget(self.stop_btn)
        
        self.close_btn = QPushButton(tr("btn_close_dialog"))
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def start_test(self):
        from dotenv import load_dotenv
        load_dotenv()
        
        app_key = os.getenv("DOUBAO_APP_KEY", "")
        access_key = os.getenv("DOUBAO_ACCESS_KEY", "")
        
        if not app_key or not access_key:
            QMessageBox.warning(
                self,
                tr("config_error"),
                tr("config_error_msg")
            )
            return
        
        self.cloned_audio = None
        self.result_label.setText(tr("cloning"))
        self.result_label.setStyleSheet("color: orange; font-size: 14px;")
        self.play_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.status_text.clear()
        
        self.test_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.show()
        
        test_text = self.test_text_label.text().replace('\n', ' ')
        
        self.test_thread = VoiceCloneTestThread(app_key, access_key, test_text)
        self.test_thread.progress_signal.connect(self.on_progress)
        self.test_thread.audio_signal.connect(self.on_audio_received)
        self.test_thread.error_signal.connect(self.on_error)
        self.test_thread.finished_signal.connect(self.on_finished)
        
        self.test_thread.start()
        self.status_text.append("🚀 克隆启动...\n")
    
    def stop_test(self):
        if self.test_thread:
            self.test_thread.stop()
            self.status_text.append("\n⏹️ 用户停止克隆")
    
    def on_progress(self, message):
        self.status_text.append(message)
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )
    
    def on_audio_received(self, audio_data, sample_rate):
        self.cloned_audio = audio_data
        self.cloned_sample_rate = sample_rate
        
        duration = len(audio_data) / sample_rate
        self.result_label.setText(
            tr("clone_success", duration=duration, rate=sample_rate)
        )
        self.result_label.setStyleSheet("color: green; font-size: 14px; font-weight: bold;")
        
        self.play_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
    
    def on_error(self, error_msg):
        self.status_text.append(f"\n❌ 错误: {error_msg}")
        self.result_label.setText(f"❌ {tr('clone_failed')}: {error_msg}")
        self.result_label.setStyleSheet("color: red; font-size: 14px;")
        QMessageBox.critical(self, tr("clone_failed"), error_msg)
    
    def on_finished(self):
        self.test_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.hide()
        self.status_text.append(f"\n{tr('clone_complete')}")
    
    def play_cloned_audio(self):
        if self.cloned_audio is None:
            QMessageBox.warning(self, tr("hint"), tr("no_audio_to_play"))
            return
        
        try:
            import sounddevice as sd
            
            self.status_text.append(f"\n{tr('playing')}")
            self.play_btn.setEnabled(False)
            
            sd.play(self.cloned_audio, self.cloned_sample_rate)
            
            duration = len(self.cloned_audio) / self.cloned_sample_rate
            QTimer.singleShot(int(duration * 1000) + 500, self.on_playback_finished)
            
        except Exception as e:
            QMessageBox.critical(self, tr("play_failed"), tr("play_failed_msg", e=e))
            self.play_btn.setEnabled(True)
    
    def on_playback_finished(self):
        self.status_text.append(tr("playback_finished"))
        self.play_btn.setEnabled(True)
    
    def save_cloned_audio(self):
        if self.cloned_audio is None:
            QMessageBox.warning(self, tr("hint"), tr("no_audio_to_save"))
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"voice_clone_{timestamp}.wav"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("save_audio_title"),
            default_filename,
            "WAV Files (*.wav)"
        )
        
        if not file_path:
            return
        
        try:
            audio_int16 = (self.cloned_audio * 32767).astype(np.int16)
            
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.cloned_sample_rate)
                wf.writeframes(audio_int16.tobytes())
            
            self.status_text.append(f"\n💾 音频已保存: {file_path}")
            QMessageBox.information(
                self,
                tr("save_success_title"),
                tr("save_success_msg", path=file_path)
            )
            
        except Exception as e:
            QMessageBox.critical(self, tr("save_failed_title"), tr("save_failed_msg", e=e))
    
    def closeEvent(self, event):
        if self.test_thread and self.test_thread.isRunning():
            reply = QMessageBox.question(
                self,
                tr("confirm_close_title"),
                tr("confirm_close_msg"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.test_thread.stop()
                self.test_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = VoiceCloneTestDialog()
    dialog.exec()
    sys.exit(0)
