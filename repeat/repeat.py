import sys
import threading
import pyautogui
import time
import keyboard
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QSpinBox, QCheckBox, QRadioButton, QMessageBox
)
import subprocess
import os
from pynput import mouse
from PyQt5.QtCore import QTimer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

def is_admin():
    return os.geteuid() == 0

def run_as_admin():
    if not is_admin():
        print("관리자 권한이 필요합니다. 스크립트를 관리자 권한으로 실행해주세요.")
        subprocess.run(["sudo", sys.executable] + sys.argv)
        sys.exit(0)

class ClickerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.running = False
        self.fixed_position = None
        self.driver = None
        self.hotkey_thread = threading.Thread(target=self.listen_hotkeys, daemon=True)
        self.hotkey_thread.start()

    def init_ui(self):
        self.setWindowTitle("🔥 범용 광클 솔루션")
        self.setFixedWidth(300)

        self.status_label = QLabel("상태: 대기 중")

        self.interval_label = QLabel("클릭 간격 (ms)")
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 10000)
        self.interval_spin.setValue(10)

        self.refresh_checkbox = QCheckBox("시작 전 새로고침 (F5)")

        self.mode_label = QLabel("클릭 모드 선택:")
        self.mouse_radio = QRadioButton("마우스 위치 기준 (시작 F1 종료 F2)")
        self.coord_radio = QRadioButton("(추가예정)특정 좌표 클릭 ")
        self.html_mode_radio = QRadioButton("(추가예정)HTML 요소 위치 클릭")
        self.mouse_radio.setChecked(True)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.interval_label)
        layout.addWidget(self.interval_spin)
        layout.addWidget(self.refresh_checkbox)
        layout.addWidget(self.mode_label)

        mode_layout = QVBoxLayout()
        mode_layout.addWidget(self.mouse_radio)
        mode_layout.addWidget(self.coord_radio)
        mode_layout.addWidget(self.html_mode_radio)
        layout.addLayout(mode_layout)

        self.setLayout(layout)
        self.show()

    def listen_hotkeys(self):
        keyboard.add_hotkey('F1', lambda: self.try_start_clicking())
        keyboard.add_hotkey('F2', lambda: self.stop_clicking())
        keyboard.add_hotkey('F8', lambda: self.trigger_html_selection()) # F8: HTML 요소 선택
        keyboard.wait()

    def try_start_clicking(self):
        if self.html_mode_radio.isChecked() and not self.fixed_position:
            self.status_label.setText("❗ F8과 HTML 요소 선택을 먼저 진행하세요.")
            return
        self.start_clicking()

    def trigger_html_selection(self):
        if not self.html_mode_radio.isChecked():
            self.status_label.setText("⚠️ HTML 모드가 아닙니다.")
            return
        self.status_label.setText("⌛ HTML 요소 클릭 대기 중...")
        QTimer.singleShot(0, self.show_html_popup)

    def show_html_popup(self):
        print("🔔 팝업 호출 시작")
        QMessageBox.information(
            self, "HTML 요소 선택",
            "클릭할 HTML 버튼 위에 마우스를 올리고 클릭하세요!"
        )
        
        print("✅ 팝업 닫힌, 클릭 대기 시작")
        QTimer.singleShot(500, self.get_html_click_position)

    def get_html_click_position(self):
        # Selenium 웹드라이버 열기
        self.driver = webdriver.Chrome()  # chromedriver 경로가 시스템 PATH에 추가되어 있어야 합니다.
        self.driver.get("https://www.naver.com")  # 원하는 웹사이트로 변경
        self.status_label.setText("🔍 웹사이트 로딩 중...")
        
        # Selenium을 사용하여 클릭된 HTML 요소 정보 추출
        def on_click(x, y, button, pressed):
            if pressed:
                action = ActionChains(self.driver)
                element = self.driver.execute_script(
                    "return document.elementFromPoint(arguments[0], arguments[1]);", x, y)
                if element:
                    self.fixed_position = (x, y)
                    self.status_label.setText(f"✅ 요소 위치 저장됨: {self.fixed_position}")
                    self.print_html_element_info(element)
                return False

        # HTML 요소 정보 출력
        def print_html_element_info(element):
            tag = element.tag_name
            id_attr = element.get_attribute('id')
            class_attr = element.get_attribute('class')
            text = element.text
            href = element.get_attribute('href') if tag == 'a' else None
            onclick = element.get_attribute('onclick')

            print("\n✅ 클릭된 HTML 요소 정보:")
            print(f"Tag: {tag}")
            print(f"ID: {id_attr}")
            print(f"Class: {class_attr}")
            print(f"Text: {text}")
            print(f"Href: {href}")
            print(f"OnClick: {onclick}")

        # 마우스 클릭 리스너
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    def start_clicking(self):
        if self.running:
            return

        self.running = True
        self.status_label.setText("🔥 클릭 시작!")

        interval = self.interval_spin.value() / 1000.0
        thread = threading.Thread(target=self.click_loop, args=(interval,))
        thread.start()

    def stop_clicking(self):
        self.running = False
        self.status_label.setText("⏹️ 클릭 종료")

    def click_loop(self, interval):
        if self.refresh_checkbox.isChecked():
            pyautogui.press('f5')
            time.sleep(1.5)

        while self.running:
            if self.coord_radio.isChecked() and self.fixed_position:
                pyautogui.click(self.fixed_position)
                pyautogui.press('enter')
            elif self.html_mode_radio.isChecked() and self.fixed_position:
                pyautogui.click(self.fixed_position)
                pyautogui.press('enter')
            else:
                pyautogui.click(pyautogui.position())
                pyautogui.press('enter')
            time.sleep(interval)

    def closeEvent(self, event):
        keyboard.unhook_all_hotkeys()
        if self.driver:
            self.driver.quit()
        event.accept()

if __name__ == '__main__':
    run_as_admin()
    app = QApplication(sys.argv)
    window = ClickerApp()
    sys.exit(app.exec_())
