"""
设置对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QLabel, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
import os
from pathlib import Path


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(600, 400)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # API配置
        api_group = QGroupBox("豆包同声传译 API 配置")
        api_layout = QFormLayout()
        
        # App Key
        self.app_key_input = QLineEdit()
        self.app_key_input.setPlaceholderText("请输入 App Key")
        api_layout.addRow("App Key:", self.app_key_input)
        
        # Access Key
        self.access_key_input = QLineEdit()
        self.access_key_input.setPlaceholderText("请输入 Access Key")
        self.access_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("Access Key:", self.access_key_input)
        
        # Resource ID
        self.resource_id_input = QLineEdit()
        self.resource_id_input.setPlaceholderText("volc.service_type.10053")
        self.resource_id_input.setText("volc.service_type.10053")
        api_layout.addRow("Resource ID:", self.resource_id_input)
        
        # 帮助信息
        help_label = QLabel(
            "💡 <a href='https://console.volcengine.com/'>点击获取豆包API密钥</a><br>"
            "1. 访问火山引擎控制台<br>"
            "2. 开通"同声传译"服务<br>"
            "3. 创建并复制 App Key 和 Access Key"
        )
        help_label.setOpenExternalLinks(True)
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; padding: 10px; background: #f0f0f0; border-radius: 5px;")
        api_layout.addRow(help_label)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # 虚拟音频配置
        audio_group = QGroupBox("虚拟音频配置")
        audio_layout = QFormLayout()
        
        device_label = QLabel(
            "请确保已安装 <a href='https://vb-audio.com/Cable/'>VB-Audio Virtual Cable</a><br>"
            "安装后在会议软件中选择 'CABLE Output' 作为麦克风"
        )
        device_label.setOpenExternalLinks(True)
        device_label.setWordWrap(True)
        audio_layout.addRow(device_label)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        test_btn = QPushButton("🔧 测试连接")
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # 加载当前配置
        self.load_current_config()
    
    def load_current_config(self):
        """加载当前配置"""
        from dotenv import load_dotenv
        load_dotenv()
        
        app_key = os.getenv("DOUBAO_APP_KEY", "")
        access_key = os.getenv("DOUBAO_ACCESS_KEY", "")
        resource_id = os.getenv("DOUBAO_RESOURCE_ID", "volc.service_type.10053")
        
        if app_key:
            self.app_key_input.setText(app_key)
        if access_key:
            self.access_key_input.setText(access_key)
        if resource_id:
            self.resource_id_input.setText(resource_id)
    
    def save_settings(self):
        """保存设置到.env文件"""
        app_key = self.app_key_input.text().strip()
        access_key = self.access_key_input.text().strip()
        resource_id = self.resource_id_input.text().strip() or "volc.service_type.10053"
        
        if not app_key or not access_key:
            QMessageBox.warning(self, "警告", "请填写 App Key 和 Access Key")
            return
        
        # 写入.env文件
        env_file = Path(".env")
        env_content = f"""# 豆包同声传译 2.0 API 配置
DOUBAO_APP_KEY={app_key}
DOUBAO_ACCESS_KEY={access_key}
DOUBAO_RESOURCE_ID={resource_id}
"""
        
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            QMessageBox.information(self, "成功", "设置已保存！\n请重启应用使配置生效")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败：{str(e)}")
    
    def test_connection(self):
        """测试API连接"""
        app_key = self.app_key_input.text().strip()
        access_key = self.access_key_input.text().strip()
        
        if not app_key or not access_key:
            QMessageBox.warning(self, "警告", "请先填写 App Key 和 Access Key")
            return
        
        QMessageBox.information(
            self,
            "测试连接",
            "连接测试功能开发中...\n\n"
            "请先保存配置，然后启动翻译测试连接"
        )
