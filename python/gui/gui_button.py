import sys
import threading
import os
import json
from datetime import datetime  # 追加

from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QTextEdit, QPushButton, QSpinBox, QDialog, QCheckBox
)
from PySide6.QtCore import QTime, Signal

from recording_module import record_twitch_to_mp4

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

log_font_size = 14
ui_font_size = 14
log_config = "true"

def load_config():
    global log_font_size, ui_font_size, recent_urls, log_config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                log_font_size = config.get("log_font_size", log_font_size)
                ui_font_size = config.get("ui_font_size", ui_font_size)
                recent_urls = config.get("recent_urls", [])
                log_config = config.get("log", [])
        except Exception as e:
            print(f"設定ファイルの読み込みに失敗しました: {e}")
    else:
        save_config()

def save_config():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "log_font_size": log_font_size,
                "ui_font_size": ui_font_size,
                "recent_urls": recent_urls,
                "log": log_config
            }, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"設定ファイルの保存に失敗しました: {e}")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定")
        self.setFixedSize(320, 240)
        self.parent = parent
        layout = QVBoxLayout()

        self.log_size_spin = QSpinBox()
        self.log_size_spin.setValue(log_font_size)
        layout.addWidget(QLabel("ログの文字サイズ"))
        layout.addWidget(self.log_size_spin)

        self.ui_size_spin = QSpinBox()
        self.ui_size_spin.setValue(ui_font_size)
        layout.addWidget(QLabel("UI文字サイズ（ボタンなど）"))
        layout.addWidget(self.ui_size_spin)

        self.log_checkbox = QCheckBox("ログを表示")
        self.log_checkbox.setChecked(log_config == "true")  # ← チェック状態を設定
        layout.addWidget(self.log_checkbox)

        apply_button = QPushButton("適用")
        apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(apply_button)

        close_button = QPushButton("閉じる")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)
        self.apply_font_sizes()

    def apply_settings(self):
        global log_font_size, ui_font_size, log_config
        log_font_size = self.log_size_spin.value()
        ui_font_size = self.ui_size_spin.value()
        log_config = "true" if self.log_checkbox.isChecked() else "false"

        if hasattr(self.parent, "log_signal"):
            self.parent.log_signal.emit("💾 設定とURLを保存中...")

        save_config()
        self.parent.apply_font_sizes()
        self.apply_font_sizes()
        self.parent.save_current_url()

        if hasattr(self.parent, "log_signal"):
            self.parent.log_signal.emit("✅ 設定とURLを保存しました。")

    def apply_font_sizes(self):
        font_style = f"font-size: {ui_font_size}px;"
        for widget in [self.log_size_spin, self.ui_size_spin, self.log_checkbox]:
            widget.setStyleSheet(font_style)
        for label in self.findChildren(QLabel):
            label.setStyleSheet(font_style)
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(font_style)

class MainWindow(QWidget):
    log_signal = Signal(str)

    def __init__(self):
        super().__init__()
        load_config()
        self.setWindowTitle("Twitch録画ツール")
        self.setMinimumSize(680, 400)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 上部入力欄
        top_layout = QHBoxLayout()
        self.record_button = QPushButton("録画開始")
        self.record_button.setFixedHeight(40)  # 40pxの高さに固定
        self.record_button.clicked.connect(self.on_record_button_clicked)
        top_layout.addWidget(self.record_button)

        # URLのラベルと入力欄を縦にまとめるレイアウト
        url_layout = QVBoxLayout()
        url_label = QLabel("TwitchのURL")
        url_layout.addWidget(url_label)

        self.url_entry = QComboBox()
        self.url_entry.setEditable(True)
        self.url_entry.setInsertPolicy(QComboBox.NoInsert)
        self.url_entry.setMinimumWidth(250)
        self.url_entry.addItems(recent_urls)
        url_layout.addWidget(self.url_entry)
        top_layout.addLayout(url_layout)

        # 録画時間のラベルと入力欄を縦にまとめるレイアウト
        time_layout = QVBoxLayout()
        time_label = QLabel("録画時間（分、小数可、0なら配信終了まで）")
        time_layout.addWidget(time_label)
        self.time_entry = QLineEdit()
        self.time_entry.setValidator(QDoubleValidator(0.0, 9999.0, 2))
        self.time_entry.setFixedWidth(100)  # ← 必要な幅に調整
        time_layout.addWidget(self.time_entry)
        top_layout.addLayout(time_layout)

        # 「設定」ボタンを縦レイアウトに入れて上に間隔を追加
        settings_layout = QVBoxLayout()
        settings_layout.addSpacing(20)
        self.settings_button = QPushButton("設定")
        self.settings_button.clicked.connect(self.open_settings)
        settings_layout.addWidget(self.settings_button)
        top_layout.addLayout(settings_layout)

        layout.addLayout(top_layout)

        # ログ欄
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.exit_button = QPushButton("終了")
        self.exit_button.clicked.connect(self.on_exit_clicked)  # 変更：終了ボタンの処理を独自関数へ
        layout.addWidget(self.exit_button)

        self.log_signal.connect(self.log_message)
        self.apply_font_sizes()

    def save_current_url(self):
        url = self.url_entry.currentText()
        if url and url not in recent_urls:
            recent_urls.insert(0, url)
            if len(recent_urls) > 10:
                recent_urls.pop()
            save_config()
            self.url_entry.insertItem(0, url)
            self.url_entry.setCurrentIndex(0)

    def on_record_button_clicked(self):
        self.save_current_url()  # 🔸 録画開始時に URL を保存

        url = self.url_entry.currentText()
        time_str = self.time_entry.text()

        if not url:
            self.log_message("❌ URLを入力してください")
            return

        try:
            minutes = float(time_str)
        except ValueError:
            self.log_message("❌ 時間を入力してください。")
            return

        seconds = int(minutes * 60)

        self.save_current_url()

        thread = threading.Thread(target=record_twitch_to_mp4, args=(url, seconds, self.log_signal.emit), daemon=True)
        thread.start()

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def apply_font_sizes(self):
        self.log_text.setStyleSheet(f"font-size: {log_font_size}px;")
        for widget in [self.record_button, self.url_entry, self.time_entry,
                       self.settings_button, self.exit_button]:
            widget.setStyleSheet(f"font-size: {ui_font_size}px;")

    def log_message(self, message):
        time_str = QTime.currentTime().toString("HH:mm:ss")
        self.log_text.append(f"[{time_str}] {message}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def on_exit_clicked(self):
        log_content = self.log_text.toPlainText().strip()
        if log_content:
            filename = datetime.now().strftime("%Y%m%d_%H%M%S.log")
            filepath = os.path.join(SCRIPT_DIR, filename)  # SCRIPT_DIRを使うように変更
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(log_content)
                self.log_message(f"ログを保存しました: {filepath}")
            except Exception as e:
                self.log_message(f"ログ保存エラー: {e}")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
