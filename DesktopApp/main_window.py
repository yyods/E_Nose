# main_window.py
import json
import csv
import time
import serial
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QAction, QMenuBar, QMenu, QInputDialog, QLineEdit, QStackedWidget
from PyQt5.QtCore import QThread, QTimer, Qt
from PyQt5.QtGui import QIntValidator
from serial_worker import SerialWorker
from plot_canvas import PlotCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.serial_port = None
        self.worker = None
        self.thread = None

        # Data containers
        self.gas_values = [[] for _ in range(7)]
        self.temperature = []
        self.humidity = []
        self.timestamps = []
        self.recording = False
        self.csv_file = None
        self.keep_alive_timer = QTimer()

        self.initUI()
        self.create_menu()
        self.show()

    def try_connect(self):
        try:
            port, description = SerialWorker.find_serial_port()
            if port:
                self.serial_port = port
                self.setup_worker()
                print(f"Connected to: {description}")
                self.load_settings()  # Load settings after connection
                self.start_keep_alive()
            else:
                self.status_label_bottom.setText("E-Nose not found. Please check the connection.")
        except Exception as e:
            self.status_label_bottom.setText(str(e))

    def setup_worker(self):
        self.worker = SerialWorker(self.serial_port)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.worker.data_received.connect(self.process_data)
        self.worker.error_occurred.connect(self.handle_error)
        self.thread.started.connect(self.worker.run)

        self.thread.start()

        # Send 'C' character to E-Nose to establish connection
        ser = serial.Serial(self.serial_port, 115200, timeout=1)
        ser.write(b'C')
        ser.close()

    def start_keep_alive(self):
        self.keep_alive_timer.timeout.connect(self.send_keep_alive)
        self.keep_alive_timer.start(2000)  # Send keep-alive message every 2 seconds

    def send_keep_alive(self):
        try:
            ser = serial.Serial(self.serial_port, 115200, timeout=1)
            ser.write(b'K')
            ser.close()
        except serial.SerialException as e:
            print(f"Serial error: {e}")

    def initUI(self):
        self.setWindowTitle("E-Nose Sensor Data")

        main_layout = QVBoxLayout()
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(main_layout)

        self.stacked_widget = QStackedWidget(self)
        main_layout.addWidget(self.stacked_widget)

        # Connect Page
        connect_page = QWidget()
        connect_layout = QVBoxLayout()
        connect_layout.setContentsMargins(20, 20, 20, 20)
        connect_layout.setSpacing(10)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.try_connect)
        
        button_layout = QHBoxLayout()
        
        self.connect_exit_button = QPushButton("EXIT")
        self.connect_exit_button.clicked.connect(self.close)

        button_layout.addWidget(self.connect_exit_button)
        button_layout.addStretch()
        button_layout.addWidget(self.connect_button)
        
        connect_layout.addLayout(button_layout)
        connect_page.setLayout(connect_layout)
        self.stacked_widget.addWidget(connect_page)
        self.resize(400, 200)  # Adjust the window size to connect page

        # Settings Page
        self.settings_page = QWidget()
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_layout.setSpacing(10)

        relaySolenoid1_layout = QHBoxLayout()
        self.relaySolenoid1_label = QLabel("Relay Solenoid 1 Duration (seconds):")
        self.relaySolenoid1_duration = QLineEdit(self)
        self.relaySolenoid1_duration.setValidator(QIntValidator(0, 1000))  # Only accept integers
        relaySolenoid1_layout.addWidget(self.relaySolenoid1_label)
        relaySolenoid1_layout.addWidget(self.relaySolenoid1_duration)
        settings_layout.addLayout(relaySolenoid1_layout)

        relaySolenoid2_layout = QHBoxLayout()
        self.relaySolenoid2_label = QLabel("Relay Solenoid 2 Duration (seconds):")
        self.relaySolenoid2_duration = QLineEdit(self)
        self.relaySolenoid2_duration.setValidator(QIntValidator(0, 1000))  # Only accept integers
        relaySolenoid2_layout.addWidget(self.relaySolenoid2_label)
        relaySolenoid2_layout.addWidget(self.relaySolenoid2_duration)
        settings_layout.addLayout(relaySolenoid2_layout)

        cycle_layout = QHBoxLayout()
        self.cycle_label = QLabel("Number of Cycles:")
        self.cycle_duration = QLineEdit(self)
        self.cycle_duration.setValidator(QIntValidator(1, 100))  # Only accept integers between 1 and 100
        cycle_layout.addWidget(self.cycle_label)
        cycle_layout.addWidget(self.cycle_duration)
        settings_layout.addLayout(cycle_layout)

        self.save_settings_button = QPushButton("Save Settings")
        self.save_settings_button.clicked.connect(self.save_settings)
        self.save_settings_button.setEnabled(False)  # Initially disabled

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_running_page)
        self.next_button.setEnabled(True)  # Initially enabled

        button_layout = QHBoxLayout()
        self.settings_exit_button = QPushButton("EXIT")
        self.settings_exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.settings_exit_button)

        button_layout.addStretch()
        button_layout.addWidget(self.save_settings_button)
        button_layout.addWidget(self.next_button)

        settings_layout.addLayout(button_layout)
        self.settings_page.setLayout(settings_layout)
        self.stacked_widget.addWidget(self.settings_page)

        # Connect textChanged signals to enableSaveSettings
        self.relaySolenoid1_duration.textChanged.connect(self.enable_save_settings)
        self.relaySolenoid2_duration.textChanged.connect(self.enable_save_settings)
        self.cycle_duration.textChanged.connect(self.enable_save_settings)

        # Running Page
        self.running_page = QWidget()
        running_layout = QVBoxLayout()
        running_layout.setContentsMargins(20, 20, 20, 20)
        running_layout.setSpacing(10)

        self.plot_canvas = PlotCanvas(self)
        running_layout.addWidget(self.plot_canvas)

        button_layout = QHBoxLayout()
        
        self.running_exit_button = QPushButton("EXIT")
        self.running_exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.running_exit_button)

        button_layout.addStretch()

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_recording)
        self.start_button.setEnabled(True)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.stop_button)

        running_layout.addLayout(button_layout)
        self.running_page.setLayout(running_layout)
        self.stacked_widget.addWidget(self.running_page)

        # Bottom Layout (persistent)
        bottom_layout = QVBoxLayout()

        sensor_status_layout = QHBoxLayout()
        self.sensor_data_label = QLabel("Sensor Data: ")
        sensor_status_layout.addWidget(self.sensor_data_label, alignment=Qt.AlignLeft)
        self.status_label_bottom = QLabel("Status: Not connected")
        sensor_status_layout.addWidget(self.status_label_bottom, alignment=Qt.AlignRight)

        bottom_layout.addLayout(sensor_status_layout)

        main_layout.addLayout(bottom_layout)

    def create_menu(self):
        menubar = QMenuBar(self)
        file_menu = QMenu("File", self)
        menubar.addMenu(file_menu)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        self.setMenuBar(menubar)

    def enable_save_settings(self):
        self.save_settings_button.setEnabled(True)
        self.next_button.setEnabled(False)

    def save_settings(self):
        settings = {
            "relaySolenoid1": {"duration": int(self.relaySolenoid1_duration.text())},
            "relaySolenoid2": {"duration": int(self.relaySolenoid2_duration.text())},
            "cycle": int(self.cycle_duration.text())
        }
        try:
            ser = serial.Serial(self.serial_port, 115200, timeout=1)
            ser.write(b'S')
            ser.write(json.dumps(settings).encode('utf-8'))
            ser.close()
        except serial.SerialException as e:
            print(f"Serial error: {e}")

        self.save_settings_button.setEnabled(False)
        self.next_button.setEnabled(True)

    def show_running_page(self):
        self.stacked_widget.setCurrentWidget(self.running_page)
        self.plot_canvas.show()
        self.resize(1280, 800)  # Adjust the window size to show all graphs

    def process_data(self, data):
        try:
            if data.startswith("DEBUG:"):
                print(data)
                return

            parsed_data = json.loads(data)

            if 'itemNumber' in parsed_data:
                item_number = parsed_data['itemNumber']
                gas_values = parsed_data['gasValues']
                temperature = parsed_data['temperature']
                humidity = parsed_data['humidity']
                operation_status = parsed_data['operationStatus']

                if self.recording:
                    self.timestamps.append(item_number)
                    if self.csv_file is not None:
                        with open(self.csv_file, 'a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([item_number] + gas_values + [temperature, humidity])

                for i in range(7):
                    self.gas_values[i].append(gas_values[i])
                self.temperature.append(temperature)
                self.humidity.append(humidity)

                # Keep the last 100 data points for plotting
                for i in range(7):
                    self.gas_values[i] = self.gas_values[i][-100:]
                self.temperature = self.temperature[-100:]
                self.humidity = self.humidity[-100:]
                self.timestamps = self.timestamps[-100:]

                self.plot_canvas.update_data(self.gas_values, self.temperature, self.humidity, self.timestamps)

                # Update bottom layout labels
                self.sensor_data_label.setText(f"Latest Data - Gas: {gas_values} Temp: {temperature} Humidity: {humidity}")

                # Handle operation status
                if operation_status == 2:  # COMPLETED
                    self.stop_recording()

            elif 'relaySolenoid1' in parsed_data:
                # Process settings data
                self.relaySolenoid1_duration.setText(str(parsed_data['relaySolenoid1']['duration']))
                self.relaySolenoid2_duration.setText(str(parsed_data['relaySolenoid2']['duration']))
                self.cycle_duration.setText(str(parsed_data['cycle']))
                self.stacked_widget.setCurrentWidget(self.settings_page)
                self.save_settings_button.setEnabled(False)  # Initially disabled
                self.next_button.setEnabled(True)  # Initially enabled
                self.resize(400, 300)  # Adjust the window size to settings page

        except json.JSONDecodeError:
            print(f"Failed to decode JSON: {data}")

    def handle_error(self, error):
        print(f"Error: {error}")
        self.status_label_bottom.setText(f"Error: {error}")
        if self.worker:
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()

    def send_command(self, command):
        try:
            ser = serial.Serial(self.serial_port, 115200, timeout=1)
            ser.write(command.encode())
            ser.close()
        except serial.SerialException as e:
            print(f"Serial error: {e}")

    def start_recording(self):
        csv_file, ok = QInputDialog.getText(self, 'CSV File Name', 'Enter CSV file name:')
        if ok and csv_file:
            self.csv_file = f"{csv_file}.csv"
        else:
            self.csv_file = f"data_{int(time.time())}.csv"
        self.recording = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.start_time = time.monotonic()
        self.clear_plots()
        with open(self.csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Gas1', 'Gas2', 'Gas3', 'Gas4', 'Gas5', 'Gas6', 'Gas7', 'Temperature', 'Humidity'])
        
        # Send 'A' command to start alternating relays
        self.send_command('A')
        # Send 'R' character to E-Nose to reset item number
        self.send_command('R')

    def stop_recording(self):
        self.send_command('B')  # Send 'B' command to stop alternating relays
        self.recording = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.stacked_widget.setCurrentWidget(self.settings_page)  # Navigate back to settings page
        self.resize(400, 300)  # Adjust the window size to settings page

    def clear_plots(self):
        self.gas_values = [[] for _ in range(7)]
        self.temperature = []
        self.humidity = []
        self.timestamps = []

    def load_settings(self):
        try:
            ser = serial.Serial(self.serial_port, 115200, timeout=1)
            ser.write(b'L')  # Command to load settings
            ser.close()
        except serial.SerialException as e:
            print(f"Serial error: {e}")

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
        self.keep_alive_timer.stop()  # Stop the keep-alive timer
        event.accept()
