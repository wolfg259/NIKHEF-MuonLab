from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from matplotlib.ft2font import HORIZONTAL
import pyqtgraph as pg
import sys
import matplotlib.pyplot as plt
from zmq import device

# set general options for plots
pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class user_interface(QMainWindow):
    def __init__(self):
        super().__init__()

        ##### MAIN LAYOUT #####
        # set general options for window
        self.setWindowTitle('MuonLab III v0.1')

        # initiating central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # set main layout to be vertical: on top image and counts,
        # below tabs with measurements
        main_vbox = QVBoxLayout(central_widget)
        ##########


        ##### TOP ROW: IMAGE, DEVICE SELECTION, COUNTS #####
        # create hbox layout for all top bar items
        top_bar_hbox = QHBoxLayout()

        # add nikhef logo (source: https://www.nikhef.nl/media/beeldmateriaal/)
        logo_label = QLabel("test")
        ##### TODO change image location #####
        pixmap_ = QPixmap('C:\\Users\\DELL\Desktop\\Internship summer\\own code\\src\\NIKHEF-MuonLabIII\\GUI\\nikhef_logo.png')
        pixmap = pixmap_.scaledToHeight(100)
        logo_label.setPixmap(pixmap)
        top_bar_hbox.addWidget(logo_label)

        # add spacer
        top_bar_hbox.addWidget(QLabel("                   "))

        # add device selection dropbox and connection indicator
        # create vbox layout to add title
        device_vbox = QVBoxLayout()
        # create drop-down menu and label
        device_select = QComboBox()
        device_select_label = QLabel("Device")
        device_select.addItem("--select device--")
        # add widgets to own vbox
        device_vbox.addWidget(device_select_label)
        device_vbox.addWidget(device_select)
        # add status indicator
        ##### TODO: make change according to connection with muonlab
        status_indicator = QLabel("NOT CONNECTED TO \n MUONLAB III")
        device_vbox.addWidget(status_indicator)
        # add vbox layout to top bar layout
        top_bar_hbox.addLayout(device_vbox)

        # add spacer
        top_bar_hbox.addWidget(QLabel("                   "))

        # add hit counts
        # create vbox layouts to add titles above count displays
        # QFrame creates border
        counts1_vbox = QFrame()
        counts1_vbox.setFrameShape(QFrame.StyledPanel)
        counts1_vbox.setLayout(QVBoxLayout())

        counts2_vbox = QFrame()
        counts2_vbox.setFrameShape(QFrame.StyledPanel)
        counts2_vbox.setLayout(QVBoxLayout())

        # create text boxes to display counts
        box_counts_1 = QLineEdit()
        box_counts_1.setReadOnly(True)
        label_box_counts1 = QLabel("Counts/s PMT 1 \n last 10 sec average")
        
        box_counts_2 = QLineEdit()
        box_counts_2.setReadOnly(True)
        label_box_counts2 = QLabel("Counts/s PMT 2 \n last 10sec average")

        # add counts to individual layouts
        counts1_vbox.layout().addWidget(label_box_counts1)
        counts1_vbox.layout().addWidget(box_counts_1)
        
        counts2_vbox.layout().addWidget(label_box_counts2)
        counts2_vbox.layout().addWidget(box_counts_2)
        # add count layouts to top bar layout
        top_bar_hbox.addWidget(counts1_vbox)
        # add spacer
        top_bar_hbox.addWidget(QLabel("                   "))
        top_bar_hbox.addWidget(counts2_vbox)
        # add spacer
        top_bar_hbox.addWidget(QLabel("                   "))
        
        # add top bar layout to main layout
        main_vbox.addLayout(top_bar_hbox)
        ##########


        ##### TABS #####
        # create tabs widget
        tab = QTabWidget()
        main_vbox.addWidget(tab)


        # TAB 1: PHOTO MULTIPLIER VOLTAGE
        tab_PMV = QWidget()
        tab_PMV_layout = QHBoxLayout()

        # left side layout total
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setLayout(QVBoxLayout())
        label_left = QLabel("Photo Multiplier 1")
        left_frame.layout().addWidget(label_left)

        # left side input layout: slider, voltage
        left_input_layout = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_input_layout.setLayout(QHBoxLayout())
        # slider
        left_slider_layout = QVBoxLayout()
        left_slider_label = QLabel("Set Input PMT 1")
        left_slider = QSlider(Qt.Horizontal)
        left_slider_layout.addWidget(left_slider_label)
        left_slider_layout.addWidget(left_slider)
        left_input_layout.setLayout(left_slider_layout)
        # voltage
        left_voltage_layout = QVBoxLayout()
        left_voltage_label = QLabel("High Voltage PMT 1")
        left_voltage = QLineEdit()
        left_voltage.setReadOnly(True)
        left_voltage_layout.addWidget(left_voltage_label)
        left_voltage_layout.addWidget(left_voltage)
        left_input_layout.addLayout(left_voltage_layout)
        # add left input layout to left side layout
        left_frame.layout().addWidget(left_input_layout)
        # add left side layout to PMV tab layout
        tab_PMV_layout.addWidget(left_frame)
        # set tab layout
        tab_PMV.setLayout(tab_PMV_layout)

        # right side layout total
        right_layout = QVBoxLayout()
        label_right = QLabel("Photo Multiplier 1")
        right_layout.addWidget(label_right)
        
        # right side input layout: slider, voltage
        right_input_layout = QHBoxLayout()
        # slider
        right_slider_layout = QVBoxLayout()
        right_slider_label = QLabel("Set Input PMT 1")
        right_slider = QSlider(Qt.Horizontal)
        right_slider_layout.addWidget(right_slider_label)
        right_slider_layout.addWidget(right_slider)
        right_input_layout.addLayout(right_slider_layout)
        # voltage
        right_voltage_layout = QVBoxLayout()
        right_voltage_label = QLabel("High Voltage PMT 1")
        right_voltage = QLineEdit()
        right_voltage.setReadOnly(True)
        right_voltage_layout.addWidget(right_voltage_label)
        right_voltage_layout.addWidget(right_voltage)
        right_input_layout.addLayout(right_voltage_layout)
        # add right input layout to right side layout
        right_layout.addLayout(right_input_layout)
        # add right side layout to PMV tab layout
        tab_PMV_layout.addLayout(right_layout)
        # set tab layout
        tab_PMV.setLayout(tab_PMV_layout)


        


        tab.addTab(tab_PMV, "Photo Multiplier Voltage")


        # tab 2

        self.plot_widget = pg.PlotWidget()
        tab.addTab(self.plot_widget, "UI-curve")

        self.plot_widget_PR = pg.PlotWidget()
        tab.addTab(self.plot_widget_PR, "PR-curve")

        self.start_button = QDoubleSpinBox()
        main_vbox.addWidget(self.start_button)


 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = user_interface()
    ui.show()
    sys.exit(app.exec())



        





