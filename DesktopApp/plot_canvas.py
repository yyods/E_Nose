# plot_canvas.py
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(12, 10))
        self.ax1 = self.fig.add_subplot(311)
        self.ax2 = self.fig.add_subplot(312)
        self.ax3 = self.fig.add_subplot(313)
        super().__init__(self.fig)
        self.setParent(parent)
        self.anim = FuncAnimation(self.fig, self.update_plot, interval=1000, cache_frame_data=False)
        self.gas_values = [[] for _ in range(7)]
        self.temperature = []
        self.humidity = []
        self.timestamps = []

    def update_data(self, gas_values, temperature, humidity, timestamps):
        self.gas_values = gas_values
        self.temperature = temperature
        self.humidity = humidity
        self.timestamps = timestamps

    def update_plot(self, frame):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        if len(self.timestamps) == len(self.gas_values[0]):
            for i in range(7):
                self.ax1.plot(self.timestamps, self.gas_values[i], label=f'Gas Sensor {i+1}')
            self.ax1.legend()
            self.ax1.set_title('Gas Sensors')

            self.ax2.plot(self.timestamps, self.temperature, label='Temperature', color='r')
            self.ax2.legend()
            self.ax2.set_title('Temperature')

            self.ax3.plot(self.timestamps, self.humidity, label='Humidity', color='b')
            self.ax3.legend()
            self.ax3.set_title('Humidity')

            self.fig.tight_layout()

        self.draw()
