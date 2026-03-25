from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QPlainTextEdit, QScrollArea, 
                             QApplication, QFrame, QStackedWidget)
from PyQt6.QtCore import Qt, QRect, QPoint , QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QMovie, QIcon
from PIL import ImageGrab

from config import Config, MODEL
from src.api import ocr

# 截圖 widget
class SnippingTool(QWidget):
    # 傳遞截圖後的圖片路徑 (str)
    img_captured = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        # 1. 設定視窗屬性：無邊框、全螢幕、始終最上層
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        # 2. 設定半透明背景 (讓螢幕變暗的遮罩感)
        self.setWindowOpacity(0.3) 
        self.setCursor(Qt.CursorShape.CrossCursor) # 十字游標
        
        self.tmp_img_path = f"{Config.TMP_SAVING_PATH}/snip_output.png"
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_selecting = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancel_capture()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_selecting = False
            self.capture_screen()
            
            # 發送信號 & 關閉截圖視窗
            self.img_captured.emit(self.tmp_img_path)
            self.close()

    def paintEvent(self, event):
        if not self.is_selecting:
            return

        painter = QPainter(self)
        # 設定畫筆：紅色邊框，寬度 2
        pen = QPen(QColor(255, 255, 0), 2)
        painter.setPen(pen)
        
        # 計算矩形範圍 (normalized 確保從右下往左上拉也能運作)
        rect = QRect(self.start_point, self.end_point).normalized()
        painter.fillRect(rect, QColor(255, 255, 0, 50))
        painter.drawRect(rect)

    def capture_screen(self):
        # 取得最終矩形座標
        rect = QRect(self.start_point, self.end_point).normalized()
        
        # 轉換為 Pillow 需要的元組 (left, top, right, bottom)
        # 注意：在高解析度螢幕 (DPI Scaling) 下，可能需要處理縮放倍率
        bbox = (
            rect.left(),
            rect.top(),
            rect.right(),
            rect.bottom()
        )

        if rect.width() > 5 and rect.height() > 5:
            # 隱藏視窗以免截到半透明的遮罩
            self.hide()
            # 使用 Pillow 擷取座標範圍
            screenshot = ImageGrab.grab(bbox=bbox, all_screens=True)
            screenshot.save(self.tmp_img_path)
            print(f"截圖已儲存：{bbox}")
        else:
            print("範圍太小，取消截圖")

    def cancel_capture(self):
        self.close()
        QApplication.quit()

class OCRWorker(QThread):
    ocr_finished = pyqtSignal(str)
    compile_finished = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, img_path):
        super().__init__()
        self.img_path = img_path

    def run(self):
        try:
            api = Config.LATEX_OCR_SERVER_API if MODEL == "latex" else Config.OCR_SERVER_API
            out = ocr(self.img_path, api)
            self.ocr_finished.emit(out)
            
            raise Exception("Not Ready")
            self.compile_finished.emit(result_img)
        except Exception as e:
            self.error_occurred.emit(str(e))

class ResultWindow(QWidget):
    def __init__(self, img_path):
        super().__init__()
        self.img_path = img_path
        self.setWindowTitle("Recognition Results")
        self.resize(700, 600) # 稍微調高一點點
        self.init_ui()
        self.apply_styles()
        self.start_processing()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # --- 1. 文本區堆疊 (關鍵修改) ---
        self.text_stack = QStackedWidget()
        
        # 頁面 0: 文字區的 Loading 狀態
        self.text_loading_container = QWidget()
        text_loading_layout = QVBoxLayout(self.text_loading_container)
        self.text_loading_label = QLabel()
        self.text_loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_loading_layout.addWidget(self.text_loading_label)
        
        # 頁面 1: 實際的文字框
        self.text_edit = QPlainTextEdit()
        self.text_edit.setFont(QFont("JetBrains Mono", 12))
        
        self.text_stack.addWidget(self.text_loading_container) # Index 0
        self.text_stack.addWidget(self.text_edit)              # Index 1

        # --- 2. 功能列 ---
        action_layout = QHBoxLayout()
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setFixedHeight(40)
        self.copy_btn.setMinimumWidth(100)
        
        action_layout.addStretch()
        action_layout.addWidget(self.copy_btn)
        action_layout.addStretch()

        # --- 3. 預覽區 (圖片) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.display_label)

        # 設定 Loading 動畫 (共用或獨立皆可)
        self.loading_movie_text = QMovie(Config.LOADING_GIF)
        self.loading_movie_img = QMovie(Config.LOADING_GIF)
        self.loading_movie_text.setScaledSize(QSize(64, 64)) # 文字區的小一點
        self.loading_movie_img.setScaledSize(QSize(96, 96))

        # 組合總佈局
        layout.addWidget(self.text_stack, 1) # 權重 1
        layout.addLayout(action_layout)
        layout.addSpacing(5)
        layout.addWidget(self.scroll_area, 2) # 權重 2

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPlainTextEdit {
                border: 1px solid #555555;
                border-radius: 8px;
                background-color: #1e1e1e;
                padding: 10px;
                color: #ffffff;
            }
            /* Loading 容器的邊框，讓它看起來像文字框的佔位符 */
            QWidget#text_loading_container {
                border: 1px solid #444444;
                border-radius: 8px;
                background-color: #1e1e1e;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: 500;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QScrollArea {
                background-color: #2b2b2b;
                border-top: 1px solid #555555;
            }
        """)
        self.text_loading_container.setObjectName("text_loading_container")

    def start_processing(self):
        # 切換到 Loading 頁面並播放動畫
        self.text_stack.setCurrentIndex(0)
        self.text_loading_label.setMovie(self.loading_movie_text)
        self.loading_movie_text.start()

        self.display_label.setMovie(self.loading_movie_img)
        self.loading_movie_img.start()
        
        # 初始化 Worker
        self.worker = OCRWorker(self.img_path)
        self.worker.ocr_finished.connect(self.on_ocr_success) # 改用專門的 function 處理
        self.worker.compile_finished.connect(self.on_compile_success)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def on_ocr_success(self, text):
        """當文字辨識完成時調用"""
        self.loading_movie_text.stop()
        self.text_edit.setPlainText(text)
        self.text_stack.setCurrentIndex(1) # 切換回文字顯示頁面

    def on_compile_success(self, result):
        self.loading_movie_img.stop()
        pixmap = QPixmap(result) if isinstance(result, str) else result
        self.display_label.setMovie(None)
        self.display_label.setPixmap(pixmap)

    def on_error(self, err):
        self.loading_movie_text.stop()
        self.loading_movie_img.stop()
        self.text_stack.setCurrentIndex(1) # 切換回文字框以顯示錯誤
        # self.text_edit.setPlainText(f"⚠ Error: {err}")
        self.display_label.setText(f"⚠ Error: {err}")

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.text_edit.toPlainText())
            self.copy_btn.setText("✓")
            self.copy_btn.setEnabled(False)
            def inner():
                self.copy_btn.setText("Copy")
                self.copy_btn.setEnabled(True)
            QTimer.singleShot(1500, inner)

    def keyPressEvent(self, event):
        # 如果按下的是 Esc 鍵
        if event.key() == Qt.Key.Key_Escape:
            self.close()  # 呼叫關閉視窗

    def closeEvent(self, event):
        # 如果 worker 還在執行，強制終止它
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate() # 強制停止執行緒
            self.worker.wait()      # 等待執行緒完全清理退出
        event.accept()             # 接受關閉事件
