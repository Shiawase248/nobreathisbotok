from datetime import datetime
import os
import shutil
import sys
import pyautogui
from time import sleep
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui

from KKT_Module.ksoc_global import kgl
from KKT_Module.Configs import SettingConfigs
from KKT_Module.SettingProcess.SettingProccess import SettingProc, ConnectDevice, ResetDevice
from KKT_Module.DataReceive.DataReciever import FeatureMapReceiver
import time


class RadarApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.running = False
        self.timee = 0
        self.codition = 1
        self.setin = 0
        self.musicin = 0
        self.exercisein = 0
        self.memoin = 0
        self.musicplay = 0
        self.timer = None  # Timer for 10-second countdown
        self.detection_paused = False  # Flag to indicate if detection is paused
        self.energy_counter = 0 # 新增計數器
        self.energy_timer = None # 新增計時器

    def setting(self):
        if self.setin == 0:
            if self.timee == 1:
                pyautogui.click(1477, 1714)
                self.setin = 1
            elif self.timee >= 2:
                pyautogui.click(1579, 1425)
                self.codition = 2
        elif self.setin == 1:
            if self.timee == 3:
                pyautogui.click(1477, 1714)
                self.setin = 0

    def music(self):
        if self.musicin == 0:
            if self.timee == 1:
                pyautogui.click(1477, 1714)
                self.musicin = 1
            elif self.timee == 2:
                pyautogui.click(1579, 1425)
                self.codition = 3
        elif self.musicin == 1:
            if self.timee == 1:
                pyautogui.click(633, 748)
            elif self.timee == 2:
                pyautogui.click(409, 790)
            elif self.timee == 3:
                pyautogui.click(1477, 1714)
                self.musicin = 0
            elif self.timee == 4:
                pyautogui.click(659, 428)

    def exercise(self):
        if self.exercisein == 0:
            if self.timee == 1:
                pyautogui.click(1477, 1714)
                self.exercisein = 1
            elif self.timee == 2:
                pyautogui.click(1579, 1425)
                self.codition = 4
        elif self.exercisein == 1:
            if self.timee == 1:
                pyautogui.click(374, 1487)
            elif self.timee == 3:
                pyautogui.click(1477, 1714)
                self.exercisein = 0


    def memo(self):
        if self.memoin == 0:
            if self.timee == 1:
                pyautogui.click(1477, 1714)
                self.memoin = 1
            elif self.timee == 2:
                pyautogui.click(1579, 1425)
                self.codition = 1
        elif self.memoin == 1:
            if self.timee == 1:
                pyautogui.click(2317, 903)
            elif self.timee == 2:
                    pyautogui.click(2318, 985)
            elif self.timee == 3:
                pyautogui.click(1477, 1714)
                self.memoin = 0

    def pot(self):
        print("hi")# print 是印出結果的語法
        self.timee = 0

    def left(self):
        print("left")  # print 是印出結果的語法
        self.timee = 0

    def right(self):
        print("right")  # print 是印出結果的語法
        self.timee = 0

    def initUI(self):
        self.setWindowTitle('Radar Object Detection')
        self.setGeometry(100, 100, 400, 300)

        self.startButton = QtWidgets.QPushButton('Start Detection', self)
        self.startButton.clicked.connect(self.startDetection)

        self.stopButton = QtWidgets.QPushButton('Stop Detection', self)
        self.stopButton.clicked.connect(self.stopDetection)
        self.stopButton.setEnabled(False)

        self.statusButton = QtWidgets.QPushButton('Status: Not detecting', self)
        self.statusButton.setStyleSheet('background-color: red')
        self.statusButton.setEnabled(False)

        self.energyLabel = QtWidgets.QLabel('Energy: 0', self)
        self.energyLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.bellImage = QtWidgets.QLabel(self)
        self.bellImage.setAlignment(QtCore.Qt.AlignCenter)
        self.updateBellImage(0)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.startButton)
        self.layout.addWidget(self.stopButton)
        self.layout.addWidget(self.statusButton)
        self.layout.addWidget(self.energyLabel)
        self.layout.addWidget(self.bellImage)

        self.setLayout(self.layout)

    def startDetection(self):
        self.running = True
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.statusButton.setText('Detecting...')
        self.statusButton.setStyleSheet('background-color: yellow')

        self.thread = DetectionThread()
        self.thread.data_signal.connect(self.updateStatus)
        self.thread.start()

    def stopDetection(self):
        self.running = False
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.thread.stop()
        self.statusButton.setText('Status: Not detecting')
        self.statusButton.setStyleSheet('background-color: red')
        self.energyLabel.setText('Energy: 0')
        self.updateBellImage(0)
        if self.timer:
            self.timer.stop()

    def startCountdown(self):
        if self.timer:
            self.timer.stop()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.evaluateCounter)
        self.timer.start(3000)  # Start a 10-second timer

    def evaluateCounter(self):
        if self.codition == 1:
            self.setting()
        elif self.codition == 2:
            self.music()
        elif self.codition == 3:
            self.exercise()
        elif self.codition == 4:
            self.memo()

        if self.timee == 1:
            self.pot()
        elif self.timee == 2:
            self.right()
        elif self.timee >= 3:
            self.left()

        self.timee = 0  # Reset counter after 10 seconds
        self.timer.stop()

    def updateStatus(self, total_energy):
        self.energyLabel.setText(f'Energy: {total_energy}')
        current_time = time.time()
        if total_energy > 50000 and not self.detection_paused:  # 修改為 50000
            self.timee += 1
            self.startCountdown()  # Start or reset the 10-second countdown
            self.statusButton.setStyleSheet('background-color: yellow')
            self.statusButton.setText('Status: Object Detected')
            self.updateBellImage(1)
            self.pauseDetection()  # 暫停檢測1秒，避免重複偵測

        # 更新計數器和計時器
        self.energy_counter += 1
        if self.energy_timer is None:
            self.energy_timer = QtCore.QTimer(self)
            self.energy_timer.timeout.connect(self.resetEnergyCounter)
            self.energy_timer.start(3000)  # 5秒計時器

            # 偵測鼠標位置並根據觸碰次數移動
            current_mouse_position = pyautogui.position()
            if current_mouse_position == (0, 0):
                if self.energy_counter == 1:
                    pyautogui.moveTo(10, 10)  # 當鼠標位於原點，觸碰一次為右移
                    self.resetEnergyCounter()  # 重置計數器和計時器
                elif self.energy_counter == 2:
                    pyautogui.moveTo(-10, -10)  # 當鼠標位置位於原點，觸碰兩次為左移
                    self.resetEnergyCounter()  # 重置計數器和計時器
            if current_mouse_position == (10, 10):
                if self.energy_counter == 1:
                    pyautogui.moveTo(20, 20)  # 當鼠標位置位於(10,10)，觸碰一次為右移
                    self.resetEnergyCounter()  # 重置計數器和計時器
                if self.energy_counter == 2:
                    pyautogui.moveTo(0, 0)  # 鼠標位置位於(10,10)，觸碰兩次為左移
                    self.resetEnergyCounter()  # 重置計數器和計時器
            if current_mouse_position == (-10, -10):
                if self.energy_counter == 1:
                    pyautogui.moveTo(0, 0)  # 當鼠標位置位於(-10,-10)，觸碰一次為右移
                    self.resetEnergyCounter()  # 重置計數器和計時器
                if self.energy_counter == 2:
                    pyautogui.moveTo(-20, -20)  # 當鼠標位置位於(-10,-10)，觸碰兩次為左移
                    self.resetEnergyCounter()  # 重置計數器和計時器
    def resetEnergyCounter(self):
        self.energy_counter = 0
        if self.energy_timer:
            self.energy_timer.stop()
            self.energy_timer = None
    def pauseDetection(self):
        """暂停检测1秒，避免重复检测"""
        self.detection_paused = True
        self.thread.pause()  # 暫停檢測線程
        QtCore.QTimer.singleShot(1000, self.resumeDetection)  # 0.7秒後恢復檢測

    def resumeDetection(self):
        """恢复检测"""
        self.detection_paused = False
        self.thread.resume()  # 恢復檢測線程

    def updateBellImage(self, detected):
        if detected:
            pixmap = QtGui.QPixmap('img/bell_on.png')
        else:
            pixmap = QtGui.QPixmap('img/bell_off.png')
        self.bellImage.setPixmap(pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio))


class DetectionThread(QtCore.QThread):
    data_signal = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True
        self.paused = False
        self.lock = QtCore.QMutex()  # 用於線程安全的鎖

    def run(self):
        connect()
        startSetting()
        self.startLoop()

    def stop(self):
        self.running = False

    def pause(self):
        """暫停檢測"""
        self.lock.lock()
        self.paused = True
        self.lock.unlock()

    def resume(self):
        """恢復檢測"""
        self.lock.lock()
        self.paused = False
        self.lock.unlock()

    def startLoop(self):
        R = FeatureMapReceiver(chirps=32)  # Receiver for getting RDI PHD map
        R.trigger(chirps=32)  # Trigger receiver before getting the data
        time.sleep(0.5)

        while self.running:  # 無限循環以獲取數據
            self.lock.lock()
            if self.paused:
                self.lock.unlock()
                continue  # 如果暂停，跳過這次循環
            self.lock.unlock()

            res = R.getResults()  # 獲取接收器數據

            if res is None:  # 如果獲取到數據
                continue  # 繼續循環

            power = np.abs(res[0])
            total_energy = np.sum(power)  # 計算總能量

            self.data_signal.emit(total_energy)


def connect():
    connect = ConnectDevice()
    connect.startUp()  # Connect to the device
    reset = ResetDevice()
    reset.startUp()  # Reset hardware register

def startSetting():
    SettingConfigs.setScriptDir("K60168-Test-00256-008-v0.0.8-20230717_240cm")  # Set the setting folder name
    ksp = SettingProc()  # Object for setting process to setup the Hardware AI and RF before receive data
    ksp.startUp(SettingConfigs)  # Start the setting process

def main():
    kgl.setLib()
    kgl.ksoclib.switchLogMode(False)

    pyautogui.moveTo(0, 0)

    app = QtWidgets.QApplication(sys.argv)
    radarApp = RadarApp()
    radarApp.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()