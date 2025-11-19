"""
零样本声音复刻验证对话框
用于测试和验证声音复刻效果
"""
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


class VoiceCloneTestThread(QThread):
    """声音复刻测试线程"""
    progress_signal = pyqtSignal(str)
    audio_signal = pyqtSignal(np.ndarray, int)  # 音频数据, 采样率
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
        """运行测试"""
        try:
            import asyncio
            from modules.ast_client_protobuf import ASTClientProtobuf
            from modules.audio_capture import AudioCapture
            
            # 创建新的事件循环
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
        """异步测试声音复刻"""
        from modules.ast_client_protobuf import ASTClientProtobuf
        from modules.audio_capture import AudioCapture
        
        self.progress_signal.emit("🎤 初始化音频采集...")
        
        # 创建AST客户端
        client = ASTClientProtobuf(self.app_key, self.access_key)
        client.set_config(
            mode="s2s",
            source_language="zh",
            target_language="en",
            source_audio_rate=16000,
            target_audio_rate=24000
        )
        
        # 设置回调收集音频
        def on_audio(audio_data):
            self.collected_audio.append(audio_data)
            self.progress_signal.emit(f"📊 已收集音频片段: {len(self.collected_audio)}")
        
        client.on_tts_audio = on_audio
        
        # 连接（connect方法已包含启动会话的逻辑）
        self.progress_signal.emit("🔌 连接服务器并启动会话...")
        if not await client.connect():
            self.error_signal.emit("连接失败")
            return
        
        # 启动接收循环（在后台运行）
        self.progress_signal.emit("📡 启动接收循环...")
        receive_task = asyncio.create_task(client.receive_loop())
        
        # 创建音频采集
        audio_capture = AudioCapture()
        
        def on_audio_captured(audio_chunk):
            if self.is_running:
                # 发送音频（异步）
                import asyncio
                asyncio.create_task(client.send_audio(audio_chunk))
        
        audio_capture.on_audio_callback = on_audio_captured
        
        # 开始采集
        self.progress_signal.emit(f"🎤 开始录音，请朗读:\n\n【{self.test_text}】\n")
        audio_capture.start()
        
        # 录音10秒
        import asyncio
        for i in range(10):
            if not self.is_running:
                break
            await asyncio.sleep(1)
            self.progress_signal.emit(f"⏱️ 录音中... {i+1}/10秒")
        
        # 停止采集
        audio_capture.stop()
        self.progress_signal.emit("⏹️ 录音结束")
        
        # 等待音频生成
        self.progress_signal.emit("⏳ 等待音频生成...")
        await asyncio.sleep(3)
        
        # 关闭连接
        await client.close()
        
        # 合并音频
        if self.collected_audio:
            self.progress_signal.emit(f"✅ 克隆成功！收到 {len(self.collected_audio)} 个音频片段")
            combined_audio = np.concatenate(self.collected_audio)
            self.audio_signal.emit(combined_audio, 24000)
        else:
            self.error_signal.emit("未收到克隆的音频")
    
    def stop(self):
        """停止测试"""
        self.is_running = False


class VoiceCloneTestDialog(QDialog):
    """零样本声音克隆对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_thread = None
        self.cloned_audio = None
        self.cloned_sample_rate = 24000
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("🔬 零样本声音克隆工具")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # 说明区域
        info_group = QGroupBox("📖 功能说明")
        info_layout = QVBoxLayout()
        info_text = QLabel(
            "此工具用于测试豆包同传2.0的零样本声音克隆功能。\n\n"
            "克隆流程：\n"
            "1. 点击【开始克隆】\n"
            "2. 对着麦克风朗读显示的文本（约10秒）\n"
            "3. 系统会自动翻译成英文，并使用您的声音合成\n"
            "4. 播放克隆的音频，听是否是您的声音\n"
            "5. 可以保存克隆的音频样本\n\n"
            "注意：这是实时克隆，边说边学习您的音色。"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 测试文本
        text_group = QGroupBox("📝 克隆文本")
        text_layout = QVBoxLayout()
        self.test_text_label = QLabel(
            "你好，我正在测试豆包同传的零样本声音克隆功能。\n"
            "这个技术可以实时学习我的声音，并用我的音色说英文。\n"
            "让我们看看效果如何。"
        )
        self.test_text_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 15px; "
            "background-color: #f0f0f0; border-radius: 5px;"
        )
        self.test_text_label.setWordWrap(True)
        text_layout.addWidget(self.test_text_label)
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)
        
        # 进度显示
        progress_group = QGroupBox("📊 克隆进度")
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
        
        # 结果显示
        result_group = QGroupBox("🎵 克隆结果")
        result_layout = QVBoxLayout()
        
        self.result_label = QLabel("等待克隆...")
        self.result_label.setStyleSheet("color: gray; font-size: 14px;")
        result_layout.addWidget(self.result_label)
        
        # 播放和保存按钮
        audio_btn_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("▶️ 播放克隆音频")
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self.play_cloned_audio)
        self.play_btn.setStyleSheet("padding: 10px; font-size: 13px;")
        audio_btn_layout.addWidget(self.play_btn)
        
        self.save_btn = QPushButton("💾 保存样本")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_cloned_audio)
        self.save_btn.setStyleSheet("padding: 10px; font-size: 13px;")
        audio_btn_layout.addWidget(self.save_btn)
        
        result_layout.addLayout(audio_btn_layout)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("🚀 开始克隆")
        self.test_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; "
            "padding: 15px; font-size: 15px; font-weight: bold; }"
        )
        self.test_btn.clicked.connect(self.start_test)
        button_layout.addWidget(self.test_btn)
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_test)
        button_layout.addWidget(self.stop_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def start_test(self):
        """开始克隆"""
        # 检查配置
        from dotenv import load_dotenv
        load_dotenv()
        
        app_key = os.getenv("DOUBAO_APP_KEY", "")
        access_key = os.getenv("DOUBAO_ACCESS_KEY", "")
        
        if not app_key or not access_key:
            QMessageBox.warning(
                self,
                "配置错误",
                "请先在.env文件中配置 DOUBAO_APP_KEY 和 DOUBAO_ACCESS_KEY"
            )
            return
        
        # 重置状态
        self.cloned_audio = None
        self.result_label.setText("克隆中...")
        self.result_label.setStyleSheet("color: orange; font-size: 14px;")
        self.play_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.status_text.clear()
        
        # 禁用开始按钮
        self.test_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.show()
        
        # 获取测试文本
        test_text = self.test_text_label.text().replace('\n', ' ')
        
        # 创建测试线程
        self.test_thread = VoiceCloneTestThread(app_key, access_key, test_text)
        self.test_thread.progress_signal.connect(self.on_progress)
        self.test_thread.audio_signal.connect(self.on_audio_received)
        self.test_thread.error_signal.connect(self.on_error)
        self.test_thread.finished_signal.connect(self.on_finished)
        
        # 启动
        self.test_thread.start()
        self.status_text.append("🚀 克隆启动...\n")
    
    def stop_test(self):
        """停止克隆"""
        if self.test_thread:
            self.test_thread.stop()
            self.status_text.append("\n⏹️ 用户停止克隆")
    
    def on_progress(self, message):
        """进度更新"""
        self.status_text.append(message)
        # 自动滚动到底部
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )
    
    def on_audio_received(self, audio_data, sample_rate):
        """收到克隆的音频"""
        self.cloned_audio = audio_data
        self.cloned_sample_rate = sample_rate
        
        duration = len(audio_data) / sample_rate
        self.result_label.setText(
            f"✅ 克隆成功！\n"
            f"音频长度: {duration:.2f}秒\n"
            f"采样率: {sample_rate}Hz\n"
            f"点击播放按钮试听效果"
        )
        self.result_label.setStyleSheet("color: green; font-size: 14px; font-weight: bold;")
        
        self.play_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
    
    def on_error(self, error_msg):
        """错误"""
        self.status_text.append(f"\n❌ 错误: {error_msg}")
        self.result_label.setText(f"❌ 克隆失败: {error_msg}")
        self.result_label.setStyleSheet("color: red; font-size: 14px;")
        QMessageBox.critical(self, "克隆失败", error_msg)
    
    def on_finished(self):
        """完成"""
        self.test_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.hide()
        self.status_text.append("\n✅ 克隆完成")
    
    def play_cloned_audio(self):
        """播放克隆的音频"""
        if self.cloned_audio is None:
            QMessageBox.warning(self, "提示", "没有可播放的音频")
            return
        
        try:
            import sounddevice as sd
            
            self.status_text.append("\n▶️ 正在播放克隆音频...")
            self.play_btn.setEnabled(False)
            
            # 播放
            sd.play(self.cloned_audio, self.cloned_sample_rate)
            
            # 等待播放完成
            duration = len(self.cloned_audio) / self.cloned_sample_rate
            QTimer.singleShot(int(duration * 1000) + 500, self.on_playback_finished)
            
        except Exception as e:
            QMessageBox.critical(self, "播放失败", f"无法播放音频: {e}")
            self.play_btn.setEnabled(True)
    
    def on_playback_finished(self):
        """播放完成"""
        self.status_text.append("⏹️ 播放完成")
        self.play_btn.setEnabled(True)
    
    def save_cloned_audio(self):
        """保存克隆的音频"""
        if self.cloned_audio is None:
            QMessageBox.warning(self, "提示", "没有可保存的音频")
            return
        
        # 生成默认文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"voice_clone_{timestamp}.wav"
        
        # 选择保存位置
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存克隆音频",
            default_filename,
            "WAV 文件 (*.wav)"
        )
        
        if not file_path:
            return
        
        try:
            # 转换为16位整数
            audio_int16 = (self.cloned_audio * 32767).astype(np.int16)
            
            # 保存WAV文件
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(1)  # 单声道
                wf.setsampwidth(2)  # 16位
                wf.setframerate(self.cloned_sample_rate)
                wf.writeframes(audio_int16.tobytes())
            
            self.status_text.append(f"\n💾 音频已保存: {file_path}")
            QMessageBox.information(
                self,
                "保存成功",
                f"克隆音频已保存到:\n{file_path}\n\n"
                f"您可以使用任何音频播放器打开此文件，\n"
                f"验证是否克隆出了您的声音。"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"无法保存音频: {e}")
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.test_thread and self.test_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "确认关闭",
                "克隆正在进行，确定要关闭吗？",
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


# 测试代码
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = VoiceCloneTestDialog()
    dialog.exec()
    sys.exit(0)
