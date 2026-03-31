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
from utils.i18n import tr


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("settings_title"))
        self.setModal(True)
        self.resize(600, 400)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # API配置
        api_group = QGroupBox(tr("api_config_group"))
        api_layout = QFormLayout()
        
        # App Key
        self.app_key_input = QLineEdit()
        self.app_key_input.setPlaceholderText(tr("app_key_placeholder"))
        api_layout.addRow("App Key:", self.app_key_input)
        
        # Access Key
        self.access_key_input = QLineEdit()
        self.access_key_input.setPlaceholderText(tr("access_key_placeholder"))
        self.access_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("Access Key:", self.access_key_input)
        
        # Resource ID
        self.resource_id_input = QLineEdit()
        self.resource_id_input.setPlaceholderText("volc.service_type.10053")
        self.resource_id_input.setText("volc.service_type.10053")
        api_layout.addRow("Resource ID:", self.resource_id_input)
        
        # 帮助信息
        help_label = QLabel(tr("api_help"))
        help_label.setOpenExternalLinks(True)
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; padding: 10px; background: #f0f0f0; border-radius: 5px;")
        api_layout.addRow(help_label)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # 虚拟音频配置
        audio_group = QGroupBox(tr("virtual_audio_group"))
        audio_layout = QFormLayout()
        
        device_label = QLabel(tr("virtual_audio_help"))
        device_label.setOpenExternalLinks(True)
        device_label.setWordWrap(True)
        audio_layout.addRow(device_label)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton(tr("btn_save"))
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        test_btn = QPushButton(tr("btn_test_connection"))
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)
        
        cancel_btn = QPushButton(tr("btn_cancel"))
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
            QMessageBox.warning(self, "Warning", tr("warning_fill_keys"))
            return
        
        # 写入.env文件
        env_file = Path(".env")
        env_content = f"""# Doubao AST API Config
DOUBAO_APP_KEY={app_key}
DOUBAO_ACCESS_KEY={access_key}
DOUBAO_RESOURCE_ID={resource_id}
"""
        
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            QMessageBox.information(self, "Success", tr("settings_saved"))
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", tr("save_failed", e=str(e)))
    
    def test_connection(self):
        """测试API连接"""
        app_key = self.app_key_input.text().strip()
        access_key = self.access_key_input.text().strip()
        
        if not app_key or not access_key:
            QMessageBox.warning(self, "Warning", tr("warning_fill_keys"))
            return
        
        QMessageBox.information(
            self,
            tr("test_connection_title"),
            tr("test_connection_msg")
        )
