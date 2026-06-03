import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import time

# 1. 設定路徑與環境
client_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'client'))
sys.path.insert(0, client_path)

# 切換工作目錄到 client，確保 config.py 讀取檔案正確
os.chdir(client_path)

# Mock sys.argv
# 同時確保 MODEL 被正確設定
with patch.object(sys, 'argv', ['main.py', '--model', 'ocr', '--config', 'test.yaml']):
    import config
    from src.widgets import ResultWindow
    import src.api

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

class TestOCRMode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 建立 QApplication 實例 (單元測試全域只需一個)
        cls.app = QApplication.instance()
        if not cls.app:
            cls.app = QApplication(sys.argv)

    def setUp(self):
        # 建立一個測試用的虛假圖片檔案
        self.test_img = "test_snip_for_unittest.png"
        with open(self.test_img, "wb") as f:
            f.write(b"fake image content")

    def tearDown(self):
        # 清理測試檔案
        if os.path.exists(self.test_img):
            os.remove(self.test_img)

    @patch('src.api.ocr')
    def test_ocr_success_flow(self, mock_ocr):
        """
        測試 OCR 模式的完整流程：
        1. 啟動 ResultWindow
        2. Worker 執行模擬的 ocr 函數
        3. UI 接收信號並更新文本
        """
        # 設定 mock 的回傳值
        test_result_text = "This is a successful OCR test result."
        mock_ocr.return_value = test_result_text

        # 實例化 ResultWindow (這會自動開始 worker)
        win = ResultWindow(self.test_img)
        
        # 輪詢事件循環等待 Worker 完成
        # 使用 processEvents 讓 PyQt 的信號與槽機制運作
        timeout = 50  # 最多等 5 秒
        while win.worker.isRunning() and timeout > 0:
            self.app.processEvents()
            time.sleep(0.1)
            timeout -= 1
        
        # 強制最後處理一次事件確保 UI 更新
        self.app.processEvents()

        # 斷言 1: 文本框是否顯示了預期的結果
        self.assertEqual(win.text_edit.toPlainText(), test_result_text)
        
        # 斷言 2: StackedWidget 是否切換到了結果頁面 (Index 1)
        self.assertEqual(win.text_stack.currentIndex(), 1)
        
        # 斷言 3: API 是否被正確調用
        mock_ocr.assert_called_once()
        
        win.close()

    @patch('src.api.ocr')
    def test_ocr_error_flow(self, mock_ocr):
        """測試 OCR 發生錯誤時的流程"""
        # 模擬 API 拋出異常
        error_msg = "Network Error"
        mock_ocr.side_effect = Exception(error_msg)

        win = ResultWindow(self.test_img)
        
        timeout = 50
        while win.worker.isRunning() and timeout > 0:
            self.app.processEvents()
            time.sleep(0.1)
            timeout -= 1
        
        self.app.processEvents()

        # 斷言: 文本框應該顯示錯誤訊息
        self.assertIn(error_msg, win.text_edit.toPlainText())
        self.assertIn("⚠ Error", win.text_edit.toPlainText())
        win.close()

if __name__ == '__main__':
    unittest.main()
