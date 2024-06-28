# E_Nose Project

The E_Nose project is a desktop application that interfaces with an ESP32-based electronic nose device to monitor gas sensors, temperature, and humidity in real-time. The application allows users to configure the device settings, view sensor data, and record the data to a CSV file.

## Project Structure

.
├── DesktopApp
│   ├── ENose.py
│   ├── **pycache**
│   │   ├── main_window.cpython-310.pyc
│   │   ├── plot_canvas.cpython-310.pyc
│   │   └── serial_worker.cpython-310.pyc
│   ├── main_window.py
│   ├── plot_canvas.py
│   ├── requirements.txt
│   ├── serial_worker.py
│   └── temp
│   ├── ENose.py
│   ├── requirements.txt
│   ├── try.cpp
│   ├── try_main_window.py
│   ├── worked_device.cpp
│   └── worked_main_window.py
├── Device
│   ├── E-nose-V1
│   │   └── E-nose-V1.ino
│   └── E-nose-V1_1
│   ├── E-nose-V1_1.ino
│   └── src
│   ├── Relay.cpp
│   └── Relay.h
└── README.md

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Pip (Python package installer)
- Git (optional, for cloning the repository)
- Arduino IDE (for programming the ESP32 device)

### Installation

1. **Clone the repository (optional):**

   ```sh
   git clone https://github.com/yourusername/E_Nose.git
   cd E_Nose/DesktopApp

   ```

2. **Install Python libraries:**

   ```sh
   pip install -r requirements.txt

   ```

3. **Run the desktop application:**

   ```sh
   python ENose.py
   ```

## Programming the ESP32 Device

    Open the E-nose-V1_1.ino file in the Arduino IDE.
    Connect your ESP32 device to your computer.
    Select the appropriate board and port in the Arduino IDE.
    Upload the code to the ESP32 device.

## Usage

    Connect Page:
        Click the "Connect" button to connect to the ESP32 device.
        The status at the bottom will indicate whether the connection was successful.

    Settings Page:
        After connecting, the settings page will load the current device settings.
        Adjust the relay solenoid durations and cycle count as needed.
        Click "Save Settings" to save the new settings to the device.
        Click "Next" to proceed to the data monitoring page.

    Running Page:
        Click "Start" to begin recording sensor data.
        The sensor data will be displayed in real-time graphs.
        Click "Stop" to stop recording data.
        The data will be saved to a CSV file.

## Notes

    The temp directory and __pycache__ directories are excluded from the repository using the .gitignore file.
    The device sends JSON-formatted data to the application, which is parsed and displayed in real-time.

## Troubleshooting

    If the connection fails, ensure the ESP32 device is properly connected and the correct port is selected.
    Check the serial output for debug messages if there are issues with data transmission.

## License

This project is licensed under the MIT License.
