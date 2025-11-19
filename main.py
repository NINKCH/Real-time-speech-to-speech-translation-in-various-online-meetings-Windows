"""
豆包实时同声传译器 - 主程序入口
Realtime AST Translator - Main Entry
"""
import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import setup_logger

# 设置日志
logger = setup_logger(
    name="RealtimeAST",
    log_file="logs/translator.log",
    level="INFO"
)


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("豆包实时同声传译器启动")
    logger.info("=" * 60)
    
    try:
        # 创建应用
        app = QApplication(sys.argv)
        app.setApplicationName("豆包实时同声传译")
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        # 运行应用
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"应用错误: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
