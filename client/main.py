import sys
from PyQt6.QtWidgets import QApplication

from config import Config
from src.widgets import SnippingTool, ResultWindow

def main():
    app = QApplication(sys.argv)
    snipper = SnippingTool()
    windows: list[ResultWindow] = [] # 存放 ResultWindow 引用

    def handle_snip_finished(img_path):
        res_win = ResultWindow(img_path)
        windows.append(res_win)
        res_win.show()

    try:
        snipper.img_captured.connect(handle_snip_finished)
        snipper.show()

        # 進入事件循環，直到所有視窗關閉
        exit_code = app.exec()
            
    finally:
        # --- 清理階段 ---
        print("Shutting down workers...")
        
        # 遍歷所有視窗，關閉裡面可能正在運行的 Worker
        for win in windows:
            if hasattr(win, 'worker') and win.worker.isRunning():
                win.worker.kill()
                win.worker.wait()
                # win.worker.wait(1000) # 給予 1 秒寬限期讓它噴異常退出
        
        print("Cleaning up temporary files...")
        Config.delete_tmp_files()
        sys.exit(exit_code)

if __name__ == "__main__":
    main()