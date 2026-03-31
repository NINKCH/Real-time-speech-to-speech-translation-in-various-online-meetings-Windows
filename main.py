"""
Realtime AST Translator - Main Entry
"""
import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import setup_logger
from utils.i18n import tr, get_language

logger = setup_logger(
    name="RealtimeAST",
    log_file="logs/translator.log",
    level="INFO"
)


def main():
    logger.info("=" * 60)
    logger.info(f"Realtime AST Translator starting (UI: {get_language()})")
    logger.info("=" * 60)
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName(tr("app_title"))
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
