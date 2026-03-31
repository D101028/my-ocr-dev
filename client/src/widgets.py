from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QPlainTextEdit, QScrollArea, 
                             QApplication, QFrame, QStackedWidget, QComboBox)
from PyQt6.QtCore import Qt, QRect, QPoint , QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QMovie
from PIL import ImageGrab

from config import Config, MODEL
from src.api import ocr
from src.sound import play_sound 
from src.tex_compile import compile_to_png 

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
        
        self.tmp_img_path = f"{Config.WORKING_DIR}/snip_output.png"
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
    compile_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    compile_error_occurred = pyqtSignal(str)

    def __init__(self, img_path):
        super().__init__()
        self.img_path = img_path

    def run(self):
        try:
            if MODEL == "latex":
                api = Config.LATEX_OCR_SERVER_API
            else:
                api = Config.OCR_SERVER_API
            
            text = ocr(self.img_path, api)
            self.ocr_finished.emit(text)
            
            if MODEL == "latex" and text.strip():
                try:
                    res_img_path = compile_to_png(text, thread=self)
                    self.compile_finished.emit(res_img_path)
                except Exception as e:
                    self.compile_error_occurred.emit(str(e))
        except Exception as e:
            self.error_occurred.emit(str(e))

class ResultWindow(QWidget):
    def __init__(self, img_path):
        super().__init__()
        self.img_path = img_path
        self.setWindowTitle(f"Recognition Results ({MODEL.upper()})")
        self.resize(700, 500 if MODEL == "ocr" else 650) 
        self.init_ui()
        self.apply_styles()
        self.start_processing()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # --- 1. 文本顯示區 (兩模式共有) ---
        self.text_stack = QStackedWidget()
        
        # Loading 頁面
        self.text_loading_container = QWidget()
        text_loading_layout = QVBoxLayout(self.text_loading_container)
        self.text_loading_label = QLabel()
        self.text_loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_loading_layout.addWidget(self.text_loading_label)
        
        # 編輯頁面
        self.text_edit = QPlainTextEdit()
        self.text_edit.setFont(QFont("JetBrains Mono", 12))
        
        self.text_stack.addWidget(self.text_loading_container) # Index 0
        self.text_stack.addWidget(self.text_edit)              # Index 1
        layout.addWidget(self.text_stack, 1)

        # --- 2. 功能按鈕列 (Copy) ---
        action_layout = QHBoxLayout()
        self.copy_btn = QPushButton(" Copy")
        self.copy_btn.setFixedHeight(35)
        self.copy_btn.setMinimumWidth(100)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        
        action_layout.addStretch()
        action_layout.addWidget(self.copy_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        # --- 3. 底部動態分流區 ---
        if MODEL == "ocr":
            self.init_ocr_bottom(layout)
        else:
            self.init_latex_bottom(layout)

        # Loading 動畫
        self.loading_movie_text = QMovie(Config.LOADING_GIF)
        self.loading_movie_text.setScaledSize(QSize(64, 64))

    def init_ocr_bottom(self, parent_layout):
        """OCR 模式：語言選單與語音播放"""
        bottom_frame = QFrame()
        bottom_frame.setObjectName("bottom_frame")
        bottom_layout = QHBoxLayout(bottom_frame)
        
        # 語言下拉選單
        self.lang_combo = QComboBox()
        self.lang_map = {
            "Japanese (ja)": "ja",
            "English (en)": "en",
            "Tr. Chinese (zh-TW)": "zh-TW",
            "Si. Chinese (zh-CN)": "zh-CN"
        }
        self.code_lang_map = dict((value, key) for key, value in self.lang_map.items())
        self.lang_combo.addItems(self.lang_map.keys())
        self.lang_combo.setCurrentText(self.code_lang_map[Config.GTTS_DEFAULT_LANG])
        self.lang_combo.setFixedHeight(35)
        
        # 播放鍵
        self.play_btn = QPushButton(" ▶ Play Audio")
        self.play_btn.setFixedHeight(35)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.clicked.connect(self.play_audio)
        
        bottom_layout.addStretch()
        label = QLabel("Voice Lang:")
        label.setObjectName("voiceLangLabel")
        bottom_layout.addWidget(label)
        bottom_layout.addWidget(self.lang_combo)
        bottom_layout.addSpacing(10)
        bottom_layout.addWidget(self.play_btn)
        bottom_layout.addStretch()
        
        parent_layout.addWidget(bottom_frame)

    def init_latex_bottom(self, parent_layout):
        """Latex 模式：圖片編譯預覽"""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.display_label)
        
        self.loading_movie_img = QMovie(Config.LOADING_GIF)
        self.loading_movie_img.setScaledSize(QSize(80, 80))
        
        parent_layout.addWidget(self.scroll_area, 2)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #2b2b2b; color: #ffffff; }
            QPlainTextEdit {
                border: 1px solid #555555; border-radius: 8px;
                background-color: #1e1e1e; padding: 10px;
            }
            #text_loading_container {
                border: 1px solid #444444; border-radius: 8px;
                background-color: #1e1e1e;
            }
            #bottom_frame {
                background-color: #333333; border-radius: 8px; padding: 5px;
            }
            QPushButton {
                background-color: #4a4a4a; border-radius: 4px; padding: 5px 15px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #666666; }
            QComboBox {
                background-color: #444444; border: 1px solid #555555;
                border-radius: 4px; padding: 2px 10px; min-width: 120px;
            }
            QComboBox::drop-down { border: 0px; }
            QScrollArea { border-top: 1px solid #555555; }
            QLabel#voiceLangLabel { background-color: #333333 }
        """)
        self.text_loading_container.setObjectName("text_loading_container")

    def start_processing(self):
        self.text_stack.setCurrentIndex(0)
        self.text_loading_label.setMovie(self.loading_movie_text)
        self.loading_movie_text.start()

        if MODEL == "latex":
            self.display_label.setMovie(self.loading_movie_img)
            self.loading_movie_img.start()
        
        self.worker = OCRWorker(self.img_path)
        self.worker.ocr_finished.connect(self.on_ocr_success)
        if MODEL == "latex":
            self.worker.compile_finished.connect(self.on_compile_success)
            self.worker.compile_error_occurred.connect(self.on_error_compile)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def on_ocr_success(self, text):
        self.loading_movie_text.stop()
        self.text_edit.setPlainText(text)
        self.text_stack.setCurrentIndex(1)

    def on_compile_success(self, img_path):
        if MODEL == "latex":
            self.loading_movie_img.stop()
            pixmap = QPixmap(img_path)
            self.display_label.setMovie(None)
            self.display_label.setPixmap(pixmap)

    def play_audio(self):
        text = self.text_edit.toPlainText().strip()
        if not text: return
        
        # 取得選擇的語言代碼
        display_name = self.lang_combo.currentText()
        lang_code = self.lang_map.get(display_name, "ja")
        
        # 執行語音播放
        play_sound(text, lang=lang_code)

    def on_error(self, err):
        self.loading_movie_text.stop()
        if MODEL == "latex": self.loading_movie_img.stop()
        self.text_stack.setCurrentIndex(1)
        self.text_edit.setPlainText(f"⚠ Error: {err}")
    
    def on_error_compile(self, err):
        self.loading_movie_text.stop()
        if MODEL == "latex": self.loading_movie_img.stop()
        error_widget = QPlainTextEdit()
        error_widget.setPlainText(err)
        self.scroll_area.setWidget(error_widget)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.text_edit.toPlainText())
            self.copy_btn.setText("✓ Copied")
            self.copy_btn.setEnabled(False)
            QTimer.singleShot(1500, lambda: (self.copy_btn.setText(" Copy"), self.copy_btn.setEnabled(True)))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def closeEvent(self, event):
        event.accept()
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.requestInterruption()
            self.worker.wait()