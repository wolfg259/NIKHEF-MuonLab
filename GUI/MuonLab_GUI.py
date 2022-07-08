from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
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
    """
    Graphical user interface for controlling and measuring with NIKHEF's MuonLab III
    (nikhef.nl/muonlab)
    
    """

    def __init__(self):
        super().__init__()

        ##### MAIN LAYOUT #####
        # set general options for window
        self.setWindowTitle("MuonLab III v0.1")

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
        pixmap_ = QPixmap(
            "C:\\Users\\DELL\Desktop\\Internship summer\\own code\\src\\NIKHEF-MuonLabIII\\GUI\\nikhef_logo.png"
        )
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
        tabs = QTabWidget()
        main_vbox.addWidget(tabs)

        # TAB 1: PHOTO MULTIPLIER VOLTAGE
        tab_PMV = QWidget()
        # use additional horizontal stacking to allow for spacer
        tab_PMV_layout_spaced = QVBoxLayout()
        tab_PMV_layout = QHBoxLayout()

        # left side layout total
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setLayout(QVBoxLayout())
        label_left = QLabel("Photo Multiplier 1")
        ##### TODO: decide on size of labels
        # label_left.setFont(QFont('Arial font', 11))
        left_frame.layout().addWidget(label_left)

        # left side input layout: slider, voltage
        left_input_layout = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_input_layout.setLayout(QHBoxLayout())
        # slider
        left_slider_layout = QFrame()
        left_slider_layout.setLayout(QVBoxLayout())
        left_slider_label = QLabel("Set Input PMT 1")
        left_slider = QSlider(Qt.Horizontal)
        left_slider_layout.layout().addWidget(left_slider_label)
        left_slider_layout.layout().addWidget(left_slider)
        left_input_layout.layout().addWidget(left_slider_layout)
        # voltage
        left_voltage_layout = QFrame()
        left_voltage_layout.setLayout(QVBoxLayout())
        left_voltage_label = QLabel("High Voltage PMT 1")
        left_voltage = QLineEdit()
        left_voltage.setFixedWidth(100)
        left_voltage.setReadOnly(True)
        left_voltage_layout.layout().addWidget(left_voltage_label)
        left_voltage_layout.layout().addWidget(left_voltage)
        left_input_layout.layout().addWidget(left_voltage_layout)
        # add left input layout to left side layout
        left_frame.layout().addWidget(left_input_layout)
        # add spacer
        left_frame.layout().addWidget(QLabel("                   "))
        # add left side layout to PMV tab layout
        tab_PMV_layout.addWidget(left_frame)

        # right side layout total
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setLayout(QVBoxLayout())
        label_right = QLabel("Photo Multiplier 2")
        right_frame.layout().addWidget(label_right)

        # right side input layout: slider, voltage
        right_input_layout = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_input_layout.setLayout(QHBoxLayout())
        # slider
        right_slider_layout = QFrame()
        right_slider_layout.setLayout(QVBoxLayout())
        right_slider_label = QLabel("Set Input PMT 2")
        right_slider = QSlider(Qt.Horizontal)
        right_slider_layout.layout().addWidget(right_slider_label)
        right_slider_layout.layout().addWidget(right_slider)
        right_input_layout.layout().addWidget(right_slider_layout)
        # voltage
        right_voltage_layout = QFrame()
        right_voltage_layout.setLayout(QVBoxLayout())
        right_voltage_label = QLabel("High Voltage PMT 2")
        right_voltage = QLineEdit()
        right_voltage.setFixedWidth(100)
        right_voltage.setReadOnly(True)
        right_voltage_layout.layout().addWidget(right_voltage_label)
        right_voltage_layout.layout().addWidget(right_voltage)
        right_input_layout.layout().addWidget(right_voltage_layout)
        # add right input layout to right side layout
        right_frame.layout().addWidget(right_input_layout)
        # add spacer
        right_frame.layout().addWidget(QLabel("                   "))
        # add right side layout to PMV tab layout
        tab_PMV_layout.addWidget(right_frame)

        # set tab layout
        tab_PMV_layout_spaced.addLayout(tab_PMV_layout)
        tab_PMV_layout_spaced.addWidget(QLabel("                   "))
        tab_PMV.setLayout(tab_PMV_layout_spaced)

        # set tab color
        ##### TODO: right color should be implemented
        # tab_PMV.setAutoFillBackground(True)
        # tab_color = tab_PMV.palette()
        # tab_color.setColor(tab_PMV.backgroundRole(), Qt.red)
        # tab_PMV.setPalette(tab_color)

        # add tab to tabs
        tabs.addTab(tab_PMV, "Photo Multiplier Voltage")

        # TAB 2: THRESHOLD LEVEL
        ##### TODO
        self.plot_widget = pg.PlotWidget()
        tabs.addTab(self.plot_widget, "Threshold Level")

        # TAB 3: LIFE TIME MEASUREMENT
        ##### TODO
        self.plot_widget_LR = pg.PlotWidget()
        tabs.addTab(self.plot_widget_LR, "Life Time Measurement")

        # TAB 4: DELTA TIME MEASUREMENT
        ##### TODO
        self.plot_widget_DT = pg.PlotWidget()
        tabs.addTab(self.plot_widget_DT, "Delta Time Measurement")

        # TAB 5: WAVEFORM CHANNEL 1
        self.plot_widget_WV = pg.PlotWidget()
        tabs.addTab(self.plot_widget_WV, "Waveform Channel 1")

        # TAB 6: HIT & COINCIDENCE RATE
        self.plot_widget_HC = pg.PlotWidget()
        tabs.addTab(self.plot_widget_HC, "Hit & Coincidence rate")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = user_interface()
    ui.show()
    sys.exit(app.exec())

