import sys
import numpy as np
import sounddevice as sd
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Thread to handle audio stream and plotting
class AudioPlotThread(QThread):
    data_signal = pyqtSignal(np.ndarray)

    def __init__(self, device_index, samplerate, blocksize):
        super().__init__()
        self.device_index = device_index
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.running = True

    def run(self):
        def callback(indata, frames, time, status):
            if status:
                print(status)
            if self.running:
                self.data_signal.emit(indata[:, 0])  # Send single channel data

        with sd.InputStream(
            device=self.device_index,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            channels=1,
            callback=callback,
        ):
            while self.running:
                sd.sleep(100)

    def stop(self):
        self.running = False

# Widget for embedding Matplotlib plots
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("mainwindow.ui", self)  # Replace with your XML file name
        self.audio_threads = []
        self.graph_widgets = []
        self.setup_ui()

    def setup_ui(self):
        # Populate audio devices in comboBox
        devices = sd.query_devices()
        input_devices = [d["name"] for d in devices if d["max_input_channels"] > 0]
        self.comboBox.addItems(input_devices)

        # Connect buttons
        self.pushButton.clicked.connect(self.start_plotting)
        self.pushButton_2.clicked.connect(self.stop_plotting)

    def start_plotting(self):
        self.stop_plotting()  # Stop any running threads

        selected_device = self.comboBox.currentIndex()
        samplerate = int(self.lineEdit_2.text())
        blocksize = int(self.lineEdit.text())

        # Create a graph for each audio input
        devices = sd.query_devices()
        input_devices = [d for d in devices if d["max_input_channels"] > 0]

        for i, device in enumerate(input_devices):
            thread = AudioPlotThread(device_index=i, samplerate=samplerate, blocksize=blocksize)
            canvas = MplCanvas(self)
            thread.data_signal.connect(lambda data, canvas=canvas: self.update_plot(canvas, data))

            self.gridLayout_4.addWidget(canvas, i + 1, 0)  # Add graphs dynamically
            thread.start()
            self.audio_threads.append(thread)
            self.graph_widgets.append(canvas)

    def update_plot(self, canvas, data):
        canvas.axes.clear()
        canvas.axes.plot(data)
        canvas.draw()

    def stop_plotting(self):
        for thread in self.audio_threads:
            thread.stop()
        self.audio_threads = []

        # Clear graphs
        for widget in self.graph_widgets:
            widget.setParent(None)
        self.graph_widgets = []

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
