"""
日誌設定模組
"""
import os
import logging
import sys
from pathlib import Path

def setup_logging():
    """
    設定應用程式日誌
    """
    # 建立 logs 目錄（如果不存在）
    logs_dir = Path('/app/logs')
    logs_dir.mkdir(exist_ok=True)
    
    # 設定日誌格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format, date_format)
    
    # 建立根記錄器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除任何現有的處理程序
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加控制台處理程序
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 添加檔案處理程序
    file_handler = logging.FileHandler('/app/logs/invoice_agent.log')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 為特定模組設定日誌級別
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.WARNING)
    
    return root_logger

logger = setup_logging()
