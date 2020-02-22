import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication, QMainWindow

from display import Plot_canvas
from controller import Information_frame
class Base_widget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.center_widget = QWidget()
        layout = QHBoxLayout()
        self.display = Plot_canvas()
        self.information = Information_frame(self.display)
        layout.addWidget(self.display)
        layout.addWidget(self.information)
        self.center_widget.setLayout(layout)

        self.setCentralWidget(self.center_widget)
        self.setWindowTitle('PSO_RBFN!!')
    def closeEvent(self, event):
        if self.information.thread_running:
            for thread in self.information.running_threads:
                thread.stop()
                thread.wait()

if __name__ == "__main__":
    sys.argv += ['--style', 'fusion']
    app = QApplication(sys.argv)
    base = Base_widget()
    base.show()
    sys.exit(app.exec_())
