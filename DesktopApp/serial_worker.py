# serial_worker.py
import time
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QObject, pyqtSignal

class SerialWorker(QObject):
    data_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.running = True

    def run(self):
        try:
            ser = serial.Serial(self.port, 115200, timeout=1)
            while self.running:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('latin-1').strip()
                    if data and not data.startswith("ESP32_DEVICE_IDENTIFIER"):
                    # if data:
                        # print(f"Received: {data}")
                        self.data_received.emit(data)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            ser.close()

    def stop(self):
        self.running = False

    @staticmethod
    def find_serial_port():
        # Get a list of all available serial ports
        ports = list(serial.tools.list_ports.comports())
        
        # Try connecting to each port to find the one with the ESP32
        for port in ports:
            try:
                with serial.Serial(port.device, 115200, timeout=1) as ser:
                    ser.write(b'I')  # Request identification
                    line = ser.readline().decode('latin-1').strip()
                    # print(f"Received: {line}")
                    if "ESP32_DEVICE_IDENTIFIER" in line:
                        return port.device
            except (OSError, serial.SerialException):
                pass

        # Try explicitly known ports (e.g., for Linux)
        known_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']
        for port in known_ports:
            try:
                with serial.Serial(port, 115200, timeout=1) as ser:
                    ser.write(b'I')  # Request identification
                    line = ser.readline().decode('latin-1').strip()
                    # print(f"Received: {line}")
                    if "ESP32_DEVICE_IDENTIFIER" in line:
                        return port
            except (OSError, serial.SerialException):
                pass
        
        return None
