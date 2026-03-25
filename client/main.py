import sys
from PyQt6.QtWidgets import QApplication

from src.widgets import SnippingTool, ResultWindow

def main():
    app = QApplication(sys.argv)

    # 1. 初始化截圖工具
    snipper = SnippingTool()
    
    # 用來存放 ResultWindow 的變數（防止被垃圾回收）
    # 使用 list 或一個全域/類別變數來保存引用
    windows = []

    def handle_snip_finished(img_path):
        """當截圖完成時觸發的邏輯"""
        # 2. 建立結果視窗，並傳入路徑
        res_win = ResultWindow(img_path)
        windows.append(res_win) # 保持引用，防止視窗閃退
        res_win.show()

    snipper.img_captured.connect(handle_snip_finished)

    snipper.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()