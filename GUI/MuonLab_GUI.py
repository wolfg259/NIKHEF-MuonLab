from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import pyqtgraph as pg
import sys
import threading
import numpy as np
import matplotlib.pyplot as plt
import os

from MuonLab_controller import list_devices, MuonLab_experiment

# set general options for plots
pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class user_interface(QMainWindow):
    """
    Graphical user interface for controlling and measuring with NIKHEF's MuonLab III
    (nikhef.nl/muonlab)
    
    """

    def __init__(
        self,
        set_PMV_tab=True,
        set_TL_tab=True,
        set_LFT_tab=True,
        set_DT_tab=True,
        set_WF_tab=True,
        set_HC_tab=True,
    ):
        super().__init__()

        # create experiment object
        self.experiment = None
        self.filename = None

        ##### MAIN LAYOUT #####
        # initiating central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        app.aboutToQuit.connect(self.closing_func)

        # set general options for window
        self.setWindowTitle("MuonLab III v0.1")
        self.setWindowIcon(
            QIcon(
                "C:\\Users\\DELL\Desktop\\Internship summer\\own code\\src\\NIKHEF-MuonLabIII\\GUI\\nikhef_logo.png"
            )
        )
        palette_grey = central_widget.palette()
        palette_grey.setColor(QPalette.Background, QColor(100, 100, 100))
        palette_light_grey = central_widget.palette()
        palette_light_grey.setColor(QPalette.Background, QColor(240, 240, 240))
        palette_white = central_widget.palette()
        palette_white.setColor(QPalette.Background, QColor(255, 255, 255))
        palette_red = central_widget.palette()
        palette_red.setColor(QPalette.Background, QColor(230, 25, 61))
        central_widget.setAutoFillBackground(True)
        central_widget.setPalette(palette_light_grey)
        bold_font = QFont()
        bold_font.setBold(True)

        # set main layout to be vertical: on top image and counts,
        # below tabs with measurements
        main_vbox = QVBoxLayout(central_widget)
        ##########

        ##### TOP ROW: IMAGE, DEVICE SELECTION, COUNTS #####
        # create hbox layout for all top bar items
        top_bar_hbox = QHBoxLayout()

        # add nikhef logo (source: https://www.nikhef.nl/media/beeldmateriaal/)
        logo_label = QLabel("test")
        logo_path = os.path.join(os.path.dirname(__file__), "nikhef_logo.png")
        pixmap_ = QPixmap(logo_path)
        pixmap = pixmap_.scaledToHeight(100)
        logo_label.setPixmap(pixmap)
        top_bar_hbox.addWidget(logo_label)

        # add spacer
        top_bar_hbox.addWidget(QLabel("                   "))

        # add device selection dropbox, connection indicator, save button
        # create vbox layout to add title
        device_vbox = QVBoxLayout()
        # create drop-down menu and label
        self.device_select = QComboBox()
        device_select_label = QLabel("Device")
        self.device_select.addItem("--select device--")
        connected_devices = list_devices()
        for device in connected_devices:
            self.device_select.addItem(device)
        self.device_select.currentIndexChanged.connect(self.device_select_func)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_data)

        # add status indicator
        self.status_indicator = QLineEdit()
        self.status_indicator.setFixedWidth(150)
        self.status_indicator.setReadOnly(True)
        self.status_indicator.setText("NOT CONNECTED")

        # add widgets to own vbox
        device_vbox.addWidget(device_select_label)
        device_vbox.addWidget(self.device_select)
        device_vbox.addWidget(self.status_indicator)
        device_vbox.addWidget(self.save_button)

        # add vbox layout to top bar layout
        top_bar_hbox.addLayout(device_vbox)

        # add spacer
        top_bar_hbox.addWidget(QLabel("                   "))

        # add hit counts
        # create vbox layouts to add titles above count displays
        # (QFrame creates border)
        counts1_vbox = QFrame()
        counts1_vbox.setFrameShape(QFrame.StyledPanel)
        counts1_vbox.setLayout(QVBoxLayout())

        counts2_vbox = QFrame()
        counts2_vbox.setFrameShape(QFrame.StyledPanel)
        counts2_vbox.setLayout(QVBoxLayout())

        # create text boxes to display counts
        self.box_counts_1 = QLineEdit()
        self.box_counts_1.setFixedWidth(100)
        self.box_counts_1.setReadOnly(True)

        label_box_counts1 = QLabel("Counts/s PMT 1 \n last 10 sec average")

        self.box_counts_2 = QLineEdit()
        self.box_counts_2.setFixedWidth(100)
        self.box_counts_2.setReadOnly(True)
        label_box_counts2 = QLabel("Counts/s PMT 2 \n last 10sec average")

        # add counts to individual layouts
        counts1_vbox.layout().addWidget(label_box_counts1)
        counts1_vbox.layout().addWidget(self.box_counts_1)

        counts2_vbox.layout().addWidget(label_box_counts2)
        counts2_vbox.layout().addWidget(self.box_counts_2)
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

        ##### TAB 1: PHOTO MULTIPLIER VOLTAGE
        # general layout: two sliders for adjusting pmt1/pmt2 voltage
        if set_PMV_tab:

            tab_PMV = QWidget()
            # use additional horizontal stacking to allow for spacer
            tab_PMV_layout_spaced = QVBoxLayout()
            tab_PMV_layout = QHBoxLayout()

            # left side layout total
            left_frame = QFrame()
            left_frame.setFrameShape(QFrame.StyledPanel)
            left_frame.setLayout(QVBoxLayout())
            label_left = QLabel("Photo Multiplier 1")
            label_left.setFont(bold_font)
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
            self.left_slider = QSlider(Qt.Horizontal)
            self.left_slider.setRange(0, 254)
            self.left_slider.valueChanged.connect(self.PMT_1_voltage_func)
            self.left_slider.setTickPosition(QSlider.TicksBelow)
            left_slider_layout.layout().addWidget(left_slider_label)
            left_slider_layout.layout().addWidget(self.left_slider)
            left_input_layout.layout().addWidget(left_slider_layout)
            # voltage
            left_voltage_layout = QFrame()
            left_voltage_layout.setLayout(QVBoxLayout())
            left_voltage_label = QLabel("High Voltage PMT 1")
            self.left_voltage = QLineEdit()
            self.left_voltage.setFixedWidth(100)
            self.left_voltage.setReadOnly(True)
            left_voltage_layout.layout().addWidget(left_voltage_label)
            left_voltage_layout.layout().addWidget(self.left_voltage)
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
            label_right.setFont(bold_font)
            right_frame.layout().addWidget(label_right)

            # right side input layout: slider, voltage
            right_input_layout = QFrame()
            right_frame.setFrameShape(QFrame.StyledPanel)
            right_input_layout.setLayout(QHBoxLayout())
            # slider
            right_slider_layout = QFrame()
            right_slider_layout.setLayout(QVBoxLayout())
            right_slider_label = QLabel("Set Input PMT 2")
            self.right_slider = QSlider(Qt.Horizontal)
            self.right_slider.setRange(0, 254)
            self.right_slider.valueChanged.connect(self.PMT_2_voltage_func)
            self.right_slider.setTickPosition(QSlider.TicksBelow)
            right_slider_layout.layout().addWidget(right_slider_label)
            right_slider_layout.layout().addWidget(self.right_slider)
            right_input_layout.layout().addWidget(right_slider_layout)
            # voltage
            right_voltage_layout = QFrame()
            right_voltage_layout.setLayout(QVBoxLayout())
            right_voltage_label = QLabel("High Voltage PMT 2")
            self.right_voltage = QLineEdit()
            self.right_voltage.setFixedWidth(100)
            self.right_voltage.setReadOnly(True)
            right_voltage_layout.layout().addWidget(right_voltage_label)
            right_voltage_layout.layout().addWidget(self.right_voltage)
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

        ##### TAB 2: THRESHOLD LEVEL
        # general layout: two sliders for adjusting ch1/ch2 threshold voltage
        if set_TL_tab:
            tab_TL = QWidget()
            # use additional horizontal stacking to allow for spacer
            tab_TL_layout_spaced = QVBoxLayout()
            tab_TL_layout = QHBoxLayout()

            # left side layout total
            left_frame_TL = QFrame()
            left_frame_TL.setFrameShape(QFrame.StyledPanel)
            left_frame_TL.setLayout(QVBoxLayout())
            label_left_TL = QLabel("Photo Multiplier 1")
            label_left_TL.setFont(bold_font)
            ##### TODO: decide on size of labels
            # label_left.setFont(QFont('Arial font', 11))
            left_frame_TL.layout().addWidget(label_left_TL)

            # left side input layout: slider, voltage
            left_input_layout_TL = QFrame()
            left_frame_TL.setFrameShape(QFrame.StyledPanel)
            left_input_layout_TL.setLayout(QHBoxLayout())
            # slider
            left_slider_layout_TL = QFrame()
            left_slider_layout_TL.setLayout(QVBoxLayout())
            # left_slider_label_TL = QLabel("Set Input PMT 1")
            self.left_slider_TL = QSlider(Qt.Horizontal)
            self.left_slider_TL.setRange(0, 254)
            self.left_slider_TL.setValue(101)
            self.left_slider_TL.valueChanged.connect(self.threshold_voltage_ch_1_func)
            self.left_slider_TL.setTickPosition(QSlider.TicksBelow)
            left_slider_layout_TL.layout().addWidget(QLabel("Set threshold voltage"))
            left_slider_layout_TL.layout().addWidget(self.left_slider_TL)
            left_input_layout_TL.layout().addWidget(left_slider_layout_TL)
            # voltage
            left_voltage_layout_TL = QFrame()
            left_voltage_layout_TL.setLayout(QVBoxLayout())
            left_voltage_label_TL = QLabel("Threshold voltage (mV)")
            self.left_voltage_TL = QLineEdit()
            self.left_voltage_TL.setFixedWidth(100)
            self.left_voltage_TL.setReadOnly(True)
            left_voltage_layout_TL.layout().addWidget(left_voltage_label_TL)
            left_voltage_layout_TL.layout().addWidget(self.left_voltage_TL)
            left_input_layout_TL.layout().addWidget(left_voltage_layout_TL)
            # add left input layout to left side layout
            left_frame_TL.layout().addWidget(left_input_layout_TL)
            # add spacer
            left_frame_TL.layout().addWidget(QLabel("                   "))
            # add left side layout to PMV tab layout
            tab_TL_layout.addWidget(left_frame_TL)

            # right side layout total
            right_frame_TL = QFrame()
            right_frame_TL.setFrameShape(QFrame.StyledPanel)
            right_frame_TL.setLayout(QVBoxLayout())
            label_right_TL = QLabel("Photo Multiplier 2")
            label_right_TL.setFont(bold_font)
            ##### TODO: decide on size of labels
            # label_right.setFont(QFont('Arial font', 11))
            right_frame_TL.layout().addWidget(label_right_TL)

            # right side input layout: slider, voltage
            right_input_layout_TL = QFrame()
            right_frame_TL.setFrameShape(QFrame.StyledPanel)
            right_input_layout_TL.setLayout(QHBoxLayout())
            # slider
            right_slider_layout_TL = QFrame()
            right_slider_layout_TL.setLayout(QVBoxLayout())
            self.right_slider_TL = QSlider(Qt.Horizontal)
            self.right_slider_TL.setRange(0, 254)
            self.right_slider_TL.setValue(101)
            self.right_slider_TL.valueChanged.connect(self.threshold_voltage_ch_2_func)
            self.right_slider_TL.setTickPosition(QSlider.TicksBelow)
            right_slider_layout_TL.layout().addWidget(QLabel("Set threshold voltage"))
            right_slider_layout_TL.layout().addWidget(self.right_slider_TL)
            right_input_layout_TL.layout().addWidget(right_slider_layout_TL)
            # voltage
            right_voltage_layout_TL = QFrame()
            right_voltage_layout_TL.setLayout(QVBoxLayout())
            right_voltage_label_TL = QLabel("Threshold voltage (mV)")
            self.right_voltage_TL = QLineEdit()
            self.right_voltage_TL.setFixedWidth(100)
            self.right_voltage_TL.setReadOnly(True)
            right_voltage_layout_TL.layout().addWidget(right_voltage_label_TL)
            right_voltage_layout_TL.layout().addWidget(self.right_voltage_TL)
            right_input_layout_TL.layout().addWidget(right_voltage_layout_TL)
            # add right input layout to right side layout
            right_frame_TL.layout().addWidget(right_input_layout_TL)
            # add spacer
            right_frame_TL.layout().addWidget(QLabel("                   "))
            # add right side layout to PMV tab layout
            tab_TL_layout.addWidget(right_frame_TL)

            # set tab layout
            tab_TL_layout_spaced.addLayout(tab_TL_layout)
            tab_TL_layout_spaced.addWidget(QLabel("                   "))
            tab_TL.setLayout(tab_TL_layout_spaced)

            # add tab to tabs
            tabs.addTab(tab_TL, "Threshold Level")

        ##### TAB 3: LIFE TIME MEASUREMENT
        # general layout:
        #   left: adjust range, adjust bins, start/stop, reset display, reset counts
        #   right: histogram plot
        if set_LFT_tab:

            tab_LFT = QWidget()
            # to change color:
            # tab_LFT.setAutoFillBackground(True)
            # tab_LFT.setPalette(palette_red)
            tab_LFT_layout = QHBoxLayout()

            # left side layout total
            left_frame_LFT = QFrame()
            left_frame_LFT.setLayout(QVBoxLayout())

            # frame containing bins, start/stop, reset display
            frame_settings_LFT = QFrame()
            frame_settings_LFT.setFrameShape(QFrame.StyledPanel)
            frame_settings_LFT.setLayout(QVBoxLayout())

            # slider to adjust horizontal range of plot
            slider_label_LFT = QLabel("Horizontal position")
            self.slider_LFT = QSlider(Qt.Horizontal)
            self.slider_LFT.setRange(0, 200)
            self.slider_LFT.setValue(50)
            self.slider_LFT.setTickPosition(QSlider.TicksBelow)

            frame_settings_LFT.layout().addWidget(slider_label_LFT)
            frame_settings_LFT.layout().addWidget(self.slider_LFT)
            frame_settings_LFT.layout().addWidget(QLabel("                   "))

            # number of bins
            bins_label_LFT = QLabel("Number of bins")
            self.bins_dropper_LFT = QComboBox()
            self.bins_dropper_LFT.addItem("64")
            self.bins_dropper_LFT.addItem("128")
            self.bins_dropper_LFT.addItem("256")
            self.bins_dropper_LFT.addItem("512")
            self.bins_dropper_LFT.addItem("1024")
            self.bins_dropper_LFT.addItem("2048")

            frame_settings_LFT.layout().addWidget(bins_label_LFT)
            frame_settings_LFT.layout().addWidget(self.bins_dropper_LFT)
            frame_settings_LFT.layout().addWidget(QLabel("                   "))

            # start/stop experiment
            start_stop_frame_LFT = QFrame()
            start_stop_frame_LFT.setLayout(QHBoxLayout())

            # start
            start_frame_LFT = QFrame()
            start_frame_LFT.setLayout(QVBoxLayout())
            self.start_button_LFT = QPushButton("Start")
            self.start_button_LFT.clicked.connect(self.start_lifetime_func)
            start_frame_LFT.layout().addWidget(QLabel("Record data"))
            start_frame_LFT.layout().addWidget(self.start_button_LFT)

            # stop
            stop_frame_LFT = QFrame()
            stop_frame_LFT.setLayout(QVBoxLayout())
            self.stop_button_LFT = QPushButton("Stop")
            self.stop_button_LFT.clicked.connect(self.stop_lifetime_func)
            stop_frame_LFT.layout().addWidget(QLabel("   "))
            stop_frame_LFT.layout().addWidget(self.stop_button_LFT)

            # status
            status_frame_LFT = QFrame()
            status_frame_LFT.setLayout(QVBoxLayout())
            self.status_display_LFT = QLineEdit()
            self.status_display_LFT.setFixedWidth(100)
            self.status_display_LFT.setReadOnly(True)

            status_frame_LFT.layout().addWidget(QLabel("Status"))
            status_frame_LFT.layout().addWidget(self.status_display_LFT)

            start_stop_frame_LFT.layout().addWidget(start_frame_LFT)
            start_stop_frame_LFT.layout().addWidget(stop_frame_LFT)
            start_stop_frame_LFT.layout().addWidget(status_frame_LFT)

            frame_settings_LFT.layout().addWidget(start_stop_frame_LFT)
            frame_settings_LFT.layout().addWidget(QLabel("                   "))

            # reset display
            ##### TODO: redundant reset button on lft tab?
            # reset_button_LFT = QPushButton("Reset")

            # frame_settings_LFT.layout().addWidget(QLabel("Reset Display"))
            # frame_settings_LFT.layout().addWidget(reset_button_LFT)

            # event counter and resetter
            event_row_LFT = QFrame()
            event_row_LFT.setLayout(QHBoxLayout())
            event_counter_frame_LFT = QFrame()
            event_counter_frame_LFT.setLayout(QVBoxLayout())
            self.event_display_LFT = QLineEdit()
            self.event_display_LFT.setFixedWidth(100)
            self.event_display_LFT.setReadOnly(True)

            event_counter_frame_LFT.layout().addWidget(QLabel("Total events"))
            event_counter_frame_LFT.layout().addWidget(self.event_display_LFT)

            reset_event_frame_LFT = QFrame()
            reset_event_frame_LFT.setLayout(QVBoxLayout())
            self.reset_button = QPushButton("Reset")
            self.reset_button.clicked.connect(self.reset_lifetime_func)

            reset_event_frame_LFT.layout().addWidget(QLabel("Reset total events"))
            reset_event_frame_LFT.layout().addWidget(self.reset_button)

            event_row_LFT.layout().addWidget(event_counter_frame_LFT)
            event_row_LFT.layout().addWidget(reset_event_frame_LFT)

            left_frame_LFT.layout().addWidget(frame_settings_LFT)
            left_frame_LFT.layout().addWidget(event_row_LFT)

            # display/plotting widget
            plot_frame_LFT = QFrame()
            plot_frame_LFT.setAutoFillBackground(True)
            plot_frame_LFT.setPalette(palette_white)
            plot_frame_LFT.setLayout(QVBoxLayout())
            plot_frame_LFT.setFrameShape(QFrame.StyledPanel)
            self.figure_LFT = plt.figure()
            self.display_LFT = FigureCanvas(self.figure_LFT)
            # empty initial plot
            ax_LFT = self.figure_LFT.add_subplot(111)
            ax_LFT.hist([])
            ax_LFT.set_xlim(left=0)
            ax_LFT.set_ylim(bottom=0)
            ax_LFT.set_xlabel("Lifetime (ns)")
            ax_LFT.set_ylabel("Counts")
            ax_LFT.grid()
            self.display_LFT.draw()

            plot_frame_LFT.layout().addWidget(self.display_LFT)

            tab_LFT_layout.layout().addWidget(left_frame_LFT)
            tab_LFT_layout.layout().addWidget(plot_frame_LFT)

            tab_LFT.setLayout(tab_LFT_layout)

            tabs.addTab(tab_LFT, "Life Time Measurement")

        # TAB 4: DELTA TIME MEASUREMENT
        # general layout:
        #   left: start/stop, reset display
        #   right: histogram plot
        if set_DT_tab:

            tab_DT = QWidget()
            tab_DT_layout = QHBoxLayout()

            # left side layout total
            left_frame_DT = QFrame()
            left_frame_DT.setLayout(QVBoxLayout())

            left_settings_DT = QFrame()
            left_settings_DT.setFrameShape(QFrame.StyledPanel)
            left_settings_DT.setLayout(QVBoxLayout())

            # bins drop down menu
            bins_label_DT = QLabel("Number of bins")
            self.bins_dropper_DT = QComboBox()
            self.bins_dropper_DT.addItem("64")
            self.bins_dropper_DT.addItem("128")
            self.bins_dropper_DT.addItem("256")
            self.bins_dropper_DT.addItem("512")
            self.bins_dropper_DT.addItem("1024")
            self.bins_dropper_DT.addItem("2048")

            # start/stop dT measuring
            start_stop_frame_DT = QFrame()
            start_stop_frame_DT.setLayout(QHBoxLayout())

            start_frame_DT = QFrame()
            start_frame_DT.setLayout(QVBoxLayout())
            self.start_button_DT = QPushButton("Start")
            self.start_button_DT.clicked.connect(self.start_delta_time_func)
            start_frame_DT.layout().addWidget(QLabel("Record data"))
            start_frame_DT.layout().addWidget(self.start_button_DT)

            stop_frame_DT = QFrame()
            stop_frame_DT.setLayout(QVBoxLayout())
            self.stop_button_DT = QPushButton("Stop")
            self.stop_button_DT.clicked.connect(self.stop_delta_time_func)
            stop_frame_DT.layout().addWidget(QLabel("   "))
            stop_frame_DT.layout().addWidget(self.stop_button_DT)

            status_frame_DT = QFrame()
            status_frame_DT.setLayout(QVBoxLayout())
            self.status_display_DT = QLineEdit()
            self.status_display_DT.setFixedWidth(100)
            self.status_display_DT.setReadOnly(True)

            status_frame_DT.layout().addWidget(QLabel("Status"))
            status_frame_DT.layout().addWidget(self.status_display_DT)

            start_stop_frame_DT.layout().addWidget(start_frame_DT)
            start_stop_frame_DT.layout().addWidget(stop_frame_DT)
            start_stop_frame_DT.layout().addWidget(status_frame_DT)

            left_settings_DT.layout().addWidget(bins_label_DT)
            left_settings_DT.layout().addWidget(self.bins_dropper_DT)
            left_settings_DT.layout().addWidget(start_stop_frame_DT)

            # reset display
            reset_frame_DT = QFrame()
            reset_frame_DT.setLayout(QVBoxLayout())
            self.reset_button_DT = QPushButton("Reset")
            self.reset_button_DT.clicked.connect(self.reset_delta_time_func)

            reset_frame_DT.layout().addWidget(QLabel("Reset Display"))
            reset_frame_DT.layout().addWidget(self.reset_button_DT)

            left_settings_DT.layout().addWidget(reset_frame_DT)

            left_frame_DT.layout().addWidget(QLabel("                   "))
            left_frame_DT.layout().addWidget(left_settings_DT)
            left_frame_DT.layout().addWidget(QLabel("                   "))

            # display/plotting widget
            plot_frame_DT = QFrame()
            plot_frame_DT.setLayout(QVBoxLayout())
            plot_frame_DT.setFrameShape(QFrame.StyledPanel)
            self.figure_DT = plt.figure()
            self.display_DT = FigureCanvas(self.figure_DT)
            # empty initial plot
            ax_DT = self.figure_DT.add_subplot(111)
            ax_DT.hist([])
            ax_DT.set_ylim(bottom=0)
            ax_DT.set_xlabel("Delta time (ns)")
            ax_DT.set_ylabel("Counts")
            ax_DT.grid()
            self.display_DT.draw()

            plot_frame_DT.layout().addWidget(self.display_DT)

            tab_DT_layout.addWidget(left_frame_DT)
            tab_DT_layout.addWidget(plot_frame_DT)

            tab_DT.setLayout(tab_DT_layout)

            tabs.addTab(tab_DT, "Delta Time Measurement")

        # TAB 5: WAVEFORM CHANNEL 1
        # general layout:
        #   left: start/stop taking data, pre-trigger time, time displayed
        #   right: plot widget displaying digitised signal
        if set_WF_tab:

            tab_WF = QWidget()
            tab_WF_layout = QHBoxLayout()

            # left side layout total
            left_frame_WF = QFrame()
            left_frame_WF.setLayout(QVBoxLayout())

            left_settings_WF = QFrame()
            left_settings_WF.setFrameShape(QFrame.StyledPanel)
            left_settings_WF.setLayout(QVBoxLayout())

            # start/stop measuring
            start_stop_frame_WF = QFrame()
            start_stop_frame_WF.setLayout(QHBoxLayout())

            start_frame_WF = QFrame()
            start_frame_WF.setLayout(QVBoxLayout())
            self.start_button_WF = QPushButton("Start")
            self.start_button_WF.clicked.connect(self.start_waveform_func)
            start_frame_WF.layout().addWidget(QLabel("Display data"))
            start_frame_WF.layout().addWidget(self.start_button_WF)

            stop_frame_WF = QFrame()
            stop_frame_WF.setLayout(QVBoxLayout())
            self.stop_button_WF = QPushButton("Stop")
            self.stop_button_WF.clicked.connect(self.stop_waveform_func)
            stop_frame_WF.layout().addWidget(QLabel("   "))
            stop_frame_WF.layout().addWidget(self.stop_button_WF)

            status_frame_WF = QFrame()
            status_frame_WF.setLayout(QVBoxLayout())
            self.status_display_WF = QLineEdit()
            self.status_display_WF.setFixedWidth(100)
            self.status_display_WF.setReadOnly(True)

            status_frame_WF.layout().addWidget(QLabel("Status"))
            status_frame_WF.layout().addWidget(self.status_display_WF)

            start_stop_frame_WF.layout().addWidget(start_frame_WF)
            start_stop_frame_WF.layout().addWidget(stop_frame_WF)
            start_stop_frame_WF.layout().addWidget(status_frame_WF)

            # pre-trigger time, time displayed
            times_frame_WF = QFrame()
            times_frame_WF.setLayout(QHBoxLayout())

            pre_trigger_frame_WF = QFrame()
            pre_trigger_frame_WF.setLayout(QVBoxLayout())
            self.pre_trigger_slider_WF = QSlider(Qt.Horizontal)
            self.pre_trigger_slider_WF.setRange(0, 10)
            self.pre_trigger_slider_WF.setValue(0)
            self.pre_trigger_slider_WF.setTickPosition(QSlider.TicksBelow)
            pre_trigger_frame_WF.layout().addWidget(QLabel("Pre-trigger time (ns)"))
            pre_trigger_frame_WF.layout().addWidget(self.pre_trigger_slider_WF)

            time_disp_frame_WF = QFrame()
            time_disp_frame_WF.setLayout(QVBoxLayout())
            self.time_slider_WF = QSlider(Qt.Horizontal)
            self.time_slider_WF.setRange(14, 99)
            self.time_slider_WF.setValue(50)
            self.time_slider_WF.setTickPosition(QSlider.TicksBelow)
            time_disp_frame_WF.layout().addWidget(QLabel("Time displayed (ns)"))
            time_disp_frame_WF.layout().addWidget(self.time_slider_WF)

            times_frame_WF.layout().addWidget(pre_trigger_frame_WF)
            times_frame_WF.layout().addWidget(time_disp_frame_WF)

            left_settings_WF.layout().addWidget(start_stop_frame_WF)
            left_settings_WF.layout().addWidget(times_frame_WF)

            left_frame_WF.layout().addWidget(QLabel("                   "))
            left_frame_WF.layout().addWidget(left_settings_WF)
            left_frame_WF.layout().addWidget(QLabel("                   "))

            # display/plotting widget
            plot_frame_WF = QFrame()
            plot_frame_WF.setLayout(QVBoxLayout())
            plot_frame_WF.setFrameShape(QFrame.StyledPanel)
            self.figure_WF = plt.figure()
            self.display_WF = FigureCanvas(self.figure_WF)
            # empty initial plot
            ax_WF = self.figure_WF.add_subplot(111)
            ax_WF.set_facecolor((0, 0, 0))
            ax_WF.plot([0], [0])
            ax_WF.set_xlim(left=0)
            ax_WF.set_ylim(300, 0)
            ax_WF.set_xlabel("Time (ns)")
            ax_WF.set_ylabel("Amplitude (mV)")
            ax_WF.grid()
            self.display_WF.draw()

            plot_frame_WF.layout().addWidget(self.display_WF)

            tab_WF_layout.addWidget(left_frame_WF)
            tab_WF_layout.addWidget(plot_frame_WF)

            tab_WF.setLayout(tab_WF_layout)

            tabs.addTab(tab_WF, "Waveform Channel 1")

        # TAB 6: HIT & COINCIDENCE RATE
        # general layout:
        #   top: left: hit rate ch1/ch2, right: start/stop
        #   bottom: left: coincidence rate ch1/ch2, right: start/stop
        if set_HC_tab:
            tab_HC = QWidget()
            tab_HC_layout = QVBoxLayout()

            # top panel: hit rate/settings
            top_frame_HC = QFrame()
            top_frame_HC.setFrameShape(QFrame.StyledPanel)
            top_frame_HC.setLayout(QHBoxLayout())

            # top left panel: hit rate
            hit_rate_frame = QFrame()
            hit_rate_frame.setFrameShape(QFrame.StyledPanel)
            hit_rate_frame.setLayout(QVBoxLayout())

            # hits ch1
            hits_ch1_frame = QFrame()
            hits_ch1_frame.setLayout(QHBoxLayout())
            # hits in last second
            hits_ls_ch1_frame = QFrame()
            hits_ls_ch1_frame.setLayout(QVBoxLayout())
            self.hits_ls_ch1 = QLineEdit()
            self.hits_ls_ch1.setFixedWidth(100)
            self.hits_ls_ch1.setReadOnly(True)

            hits_ls_ch1_frame.layout().addWidget(QLabel("Hits in last second"))
            hits_ls_ch1_frame.layout().addWidget(self.hits_ls_ch1)
            # hits total
            hits_tot_ch1_frame = QFrame()
            hits_tot_ch1_frame.setLayout(QVBoxLayout())
            self.hits_tot_ch1 = QLineEdit()
            self.hits_tot_ch1.setFixedWidth(100)
            self.hits_tot_ch1.setReadOnly(True)

            hits_tot_ch1_frame.layout().addWidget(QLabel("Total hits"))
            hits_tot_ch1_frame.layout().addWidget(self.hits_tot_ch1)
            # hits/s average over run time
            hits_avg_ch1_frame = QFrame()
            hits_avg_ch1_frame.setLayout(QVBoxLayout())
            self.hits_avg_ch1 = QLineEdit()
            self.hits_avg_ch1.setFixedWidth(100)
            self.hits_avg_ch1.setReadOnly(True)

            hits_avg_ch1_frame.layout().addWidget(
                QLabel("Average number of hits \nper sec over run time")
            )
            hits_avg_ch1_frame.layout().addWidget(self.hits_avg_ch1)

            hits_ch1_frame.layout().addWidget(QLabel("Channel 1"))
            hits_ch1_frame.layout().addWidget(hits_ls_ch1_frame)
            hits_ch1_frame.layout().addWidget(hits_tot_ch1_frame)
            hits_ch1_frame.layout().addWidget(hits_avg_ch1_frame)

            # hits ch2
            hits_ch2_frame = QFrame()
            hits_ch2_frame.setLayout(QHBoxLayout())
            # hits in last second
            hits_ls_ch2_frame = QFrame()
            hits_ls_ch2_frame.setLayout(QVBoxLayout())
            self.hits_ls_ch2 = QLineEdit()
            self.hits_ls_ch2.setFixedWidth(100)
            self.hits_ls_ch2.setReadOnly(True)

            hits_ls_ch2_frame.layout().addWidget(QLabel("Hits in last second"))
            hits_ls_ch2_frame.layout().addWidget(self.hits_ls_ch2)
            # hits total
            hits_tot_ch2_frame = QFrame()
            hits_tot_ch2_frame.setLayout(QVBoxLayout())
            self.hits_tot_ch2 = QLineEdit()
            self.hits_tot_ch2.setFixedWidth(100)
            self.hits_tot_ch2.setReadOnly(True)

            hits_tot_ch2_frame.layout().addWidget(QLabel("Total hits"))
            hits_tot_ch2_frame.layout().addWidget(self.hits_tot_ch2)
            # hits/s average over total
            hits_avg_ch2_frame = QFrame()
            hits_avg_ch2_frame.setLayout(QVBoxLayout())
            self.hits_avg_ch2 = QLineEdit()
            self.hits_avg_ch2.setFixedWidth(100)
            self.hits_avg_ch2.setReadOnly(True)

            hits_avg_ch2_frame.layout().addWidget(
                QLabel("Average number of hits \nper sec over run time")
            )
            hits_avg_ch2_frame.layout().addWidget(self.hits_avg_ch2)

            hits_ch2_frame.layout().addWidget(QLabel("Channel 2"))
            hits_ch2_frame.layout().addWidget(hits_ls_ch2_frame)
            hits_ch2_frame.layout().addWidget(hits_tot_ch2_frame)
            hits_ch2_frame.layout().addWidget(hits_avg_ch2_frame)

            # hit rate settings
            hit_rate_settings_frame = QFrame()
            hit_rate_settings_frame.setFrameShape(QFrame.StyledPanel)
            hit_rate_settings_frame.setLayout(QVBoxLayout())
            # start/stop, status, reset
            start_stop_frame_HC = QFrame()
            start_stop_frame_HC.setLayout(QHBoxLayout())

            # start
            start_frame_HC = QFrame()
            start_frame_HC.setLayout(QVBoxLayout())
            self.start_button_HC = QPushButton("Start")
            self.start_button_HC.clicked.connect(self.start_hit_rate_func)
            start_frame_HC.layout().addWidget(QLabel("Record data"))
            start_frame_HC.layout().addWidget(self.start_button_HC)

            # stop
            stop_frame_HC = QFrame()
            stop_frame_HC.setLayout(QVBoxLayout())
            self.stop_button_HC = QPushButton("Stop")
            self.stop_button_HC.clicked.connect(self.stop_hit_rate_func)
            stop_frame_HC.layout().addWidget(QLabel("   "))
            stop_frame_HC.layout().addWidget(self.stop_button_HC)

            # status
            status_frame_HC = QFrame()
            status_frame_HC.setLayout(QVBoxLayout())
            self.status_display_HC = QLineEdit()
            self.status_display_HC.setFixedWidth(100)
            self.status_display_HC.setReadOnly(True)
            self.status_display_HC.setText("  ")

            status_frame_HC.layout().addWidget(QLabel("Status"))
            status_frame_HC.layout().addWidget(self.status_display_HC)

            # reset
            reset_button_frame_HC = QFrame()
            reset_button_frame_HC.setLayout(QVBoxLayout())
            self.reset_button_HC = QPushButton("Reset")
            self.reset_button_HC.clicked.connect(self.reset_hit_rate_func)
            reset_button_frame_HC.layout().addWidget(QLabel("  "))
            reset_button_frame_HC.layout().addWidget(self.reset_button_HC)

            start_stop_frame_HC.layout().addWidget(start_frame_HC)
            start_stop_frame_HC.layout().addWidget(stop_frame_HC)
            start_stop_frame_HC.layout().addWidget(status_frame_HC)
            start_stop_frame_HC.layout().addWidget(reset_button_frame_HC)

            # run time
            run_time_HC_frame = QFrame()
            run_time_HC_frame.setLayout(QVBoxLayout())
            self.run_time_HC = QLineEdit()
            self.run_time_HC.setFixedWidth(200)
            self.run_time_HC.setReadOnly(True)
            run_time_HC_frame.layout().addWidget(QLabel("Run time"))
            run_time_HC_frame.layout().addWidget(self.run_time_HC)

            hit_rate_settings_frame.layout().addWidget(start_stop_frame_HC)
            hit_rate_settings_frame.layout().addWidget(run_time_HC_frame)

            rate_label = QLabel("Hit rate")
            rate_label.setFont(bold_font)
            hit_rate_frame.layout().addWidget(rate_label)
            hit_rate_frame.layout().addWidget(hits_ch1_frame)
            hit_rate_frame.layout().addWidget(hits_ch2_frame)

            top_frame_HC.layout().addWidget(hit_rate_frame)
            top_frame_HC.layout().addWidget(hit_rate_settings_frame)

            # bottom panel: coincidence rate/settings
            bottom_frame_HC = QFrame()
            bottom_frame_HC.setFrameShape(QFrame.StyledPanel)
            bottom_frame_HC.setLayout(QHBoxLayout())

            # bottom left panel: coincidence rate
            coin_rate_frame = QFrame()
            coin_rate_frame.setFrameShape(QFrame.StyledPanel)
            coin_rate_frame.setLayout(QVBoxLayout())

            coin_rates_horiz_frame = QFrame()
            coin_rates_horiz_frame.setLayout(QHBoxLayout())

            # total coincidences
            coin_tot_frame = QFrame()
            coin_tot_frame.setLayout(QVBoxLayout())
            self.coin_tot = QLineEdit()
            self.coin_tot.setFixedWidth(200)
            self.coin_tot.setReadOnly(True)
            coin_tot_frame.layout().addWidget(QLabel("Total coincidences"))
            coin_tot_frame.layout().addWidget(self.coin_tot)

            # average coincidences/s over run time
            coin_avg_frame = QFrame()
            coin_avg_frame.setLayout(QVBoxLayout())
            self.coin_avg = QLineEdit()
            self.coin_avg.setFixedWidth(200)
            self.coin_avg.setReadOnly(True)
            coin_avg_frame.layout().addWidget(
                QLabel("Average coincidences per \nsec over run time")
            )
            coin_avg_frame.layout().addWidget(self.coin_avg)

            coin_rates_horiz_frame.layout().addWidget(coin_tot_frame)
            coin_rates_horiz_frame.layout().addWidget(coin_avg_frame)

            coin_label = QLabel("Coincidences")
            coin_label.setFont(bold_font)
            coin_rate_frame.layout().addWidget(coin_label)
            coin_rate_frame.layout().addWidget(coin_rates_horiz_frame)

            # coincidence rate settings
            coin_rate_settings_frame = QFrame()
            coin_rate_settings_frame.setFrameShape(QFrame.StyledPanel)
            coin_rate_settings_frame.setLayout(QVBoxLayout())
            # start/stop, status, reset     _coin
            start_stop_frame_coin_HC = QFrame()
            start_stop_frame_coin_HC.setLayout(QHBoxLayout())

            # start
            start_frame_coin_HC = QFrame()
            start_frame_coin_HC.setLayout(QVBoxLayout())
            self.start_button_coin_HC = QPushButton("Start")
            self.start_button_coin_HC.clicked.connect(self.start_coincidence_func)
            start_frame_coin_HC.layout().addWidget(QLabel("Record data"))
            start_frame_coin_HC.layout().addWidget(self.start_button_coin_HC)

            # stop
            stop_frame_coin_HC = QFrame()
            stop_frame_coin_HC.setLayout(QVBoxLayout())
            self.stop_button_coin_HC = QPushButton("Stop")
            self.stop_button_coin_HC.clicked.connect(self.stop_coincidence_func)
            stop_frame_coin_HC.layout().addWidget(QLabel("   "))
            stop_frame_coin_HC.layout().addWidget(self.stop_button_coin_HC)

            # status
            status_frame_coin_HC = QFrame()
            status_frame_coin_HC.setLayout(QVBoxLayout())
            self.status_display_coin_HC = QLineEdit()
            self.status_display_coin_HC.setFixedWidth(100)
            self.status_display_coin_HC.setReadOnly(True)

            status_frame_coin_HC.layout().addWidget(QLabel("Status"))
            status_frame_coin_HC.layout().addWidget(self.status_display_coin_HC)

            # reset
            reset_button_frame_coin_HC = QFrame()
            reset_button_frame_coin_HC.setLayout(QVBoxLayout())
            self.reset_button_coin_HC = QPushButton("Reset")
            self.reset_button_coin_HC.clicked.connect(self.reset_coincidence_func)
            reset_button_frame_coin_HC.layout().addWidget(QLabel("  "))
            reset_button_frame_coin_HC.layout().addWidget(self.reset_button_coin_HC)

            start_stop_frame_coin_HC.layout().addWidget(start_frame_coin_HC)
            start_stop_frame_coin_HC.layout().addWidget(stop_frame_coin_HC)
            start_stop_frame_coin_HC.layout().addWidget(status_frame_coin_HC)
            start_stop_frame_coin_HC.layout().addWidget(reset_button_frame_coin_HC)

            # run time
            run_time_coin_HC_frame = QFrame()
            run_time_coin_HC_frame.setLayout(QVBoxLayout())
            self.run_time_coin_HC = QLineEdit()
            self.run_time_coin_HC.setFixedWidth(200)
            self.run_time_coin_HC.setReadOnly(True)
            run_time_coin_HC_frame.layout().addWidget(QLabel("Run time"))
            run_time_coin_HC_frame.layout().addWidget(self.run_time_coin_HC)

            coin_rate_settings_frame.layout().addWidget(start_stop_frame_coin_HC)
            coin_rate_settings_frame.layout().addWidget(run_time_coin_HC_frame)

            bottom_frame_HC.layout().addWidget(coin_rate_frame)
            bottom_frame_HC.layout().addWidget(coin_rate_settings_frame)

            tab_HC_layout.addWidget(top_frame_HC)
            tab_HC_layout.addWidget(bottom_frame_HC)

            tab_HC.setLayout(tab_HC_layout)

            tabs.addTab(tab_HC, "Hit and coincidence rate")

    ##### FUNCTIONS #####
    ##### TOP BAR #####
    def device_select_func(self):
        """
        Establishes connection with selected port
        
        """

        self.device = self.device_select.currentText()

        # close measuring loop and set settings back to default
        if self.experiment:
            try:
                self.experiment.run_measurements = False
                self.experiment.set_value_PMT_1(0)
                self.experiment.set_value_PMT_2(0)
                self.experiment.set_threshold_ch_1(101)
                self.experiment.set_threshold_ch_2(101)
            except:
                pass

            # close connection if a connection is already established
            self.experiment.device.close()


        # initialise MuonLab III if right port is chosen and
        # initialise threading
        try:
            self.experiment = MuonLab_experiment(port=self.device)

            self.status_indicator.setText("CONNECTED")
            self.left_voltage.setText("300.0")
            self.left_slider.setValue(0)
            self.right_voltage.setText("300.0")
            self.right_slider.setValue(0)
            self.left_voltage_TL.setText("151.0")
            self.left_slider_TL.setValue(101)
            self.right_voltage_TL.setText("151.0")
            self.right_slider_TL.setValue(101)

            # timers to update set widgets every second
            self.box_counts_1_timer = QTimer()
            self.box_counts_1_timer.start(500)
            self.box_counts_1_timer.timeout.connect(self.box_counts_1_func)

            self.box_counts_2_timer = QTimer()
            self.box_counts_2_timer.start(500)
            self.box_counts_2_timer.timeout.connect(self.box_counts_2_func)

            ##### THREADING #####
            self.main_thread = threading.Thread(
                target=self.experiment.data_acquisition, args=()
            )
            self.main_thread.start()

        # if no connection can be established:
        except:

            # reset all settings
            self.experiment = None
            self.status_indicator.setText("NOT CONNECTED")
            self.left_voltage.setText(" ")
            self.left_slider.setValue(0)
            self.right_voltage.setText(" ")
            self.right_slider.setValue(0)
            self.left_voltage_TL.setText(" ")
            self.left_slider_TL.setValue(101)
            self.right_voltage_TL.setText(" ")
            self.left_slider_TL.setValue(101)
            self.box_counts_1.setText(" ")
            self.box_counts_2.setText(" ")

            # stop all timers from updating if they are running
            try:
                self.main_thread.close()
            except:
                pass
            try:
                self.lifetime_timer.disconnect()
            except:
                pass
            try:
                self.delta_time_timer.disconnect()
            except:
                pass
            try:
                self.hit_rate_timer.disconnect()
            except:
                pass
            try:
                self.coincidence_timer.disconnect()
            except:
                pass
            try:
                self.signal_timer.disconnect()
            except:
                pass
            try:
                self.box_counts_1_timer.disconnect()
            except:
                pass
            try:
                self.box_counts_2_timer.disconnect()
            except:
                pass

    def save_data(self):
        """
        Requests file name and saves data if a MuonLab is connected
        
        """

        if self.experiment != None:
            filename, _ = QFileDialog.getSaveFileName(filter="CSV files (*.csv)")
            self.experiment.filename = filename
            self.experiment.save_data()

    def box_counts_1_func(self):
        """
        Sets average hit count of channel 1 in top bar
        
        """

        last_avg = str(round(np.mean(self.experiment.hits_ch1_last_10), 1))
        self.box_counts_1.setText(last_avg)

    def box_counts_2_func(self):
        """
        Sets average hit count of channel 2 in top bar
        
        """

        last_avg = str(round(np.mean(self.experiment.hits_ch2_last_10), 1))
        self.box_counts_2.setText(last_avg)
   
    ##########

    ##### TAB: PHOTO MULTIPLIER VOLTAGE
    def PMT_1_voltage_func(self):
        """
        Changes high voltage over channel 1 (PMT 1). Values are allowed in range(0, 254).
        Voltage is calculated as: HV = 300+((nBit/255)*1500)
        
        """

        value = self.left_slider.value()
        display_value = str(round(300 + ((value / 255) * 1400), 0))
        self.experiment.set_value_PMT_1(value)
        self.left_voltage.setText(display_value)

    def PMT_2_voltage_func(self):
        """
        Changes high voltage over channel 1 (PMT 1). Values are allowed in range(0, 254).
        Voltage is calculated as: HV = 300+((nBit/255)*1500)
        
        """

        value = self.right_slider.value()
        display_value = str(round(300 + ((value / 255) * 1400), 0))
        self.experiment.set_value_PMT_2(value)
        self.right_voltage.setText(display_value)

    ##########

    ##### TAB: THRESHOLD VOLTAGE #####
    def threshold_voltage_ch_1_func(self):
        """
        Changes threshold voltage on channel 1 (PMT 1). Values are allowed in range(0, 254).
        Voltage is calculated as: V = (nBit/255)*380mV
        
        """

        value = self.left_slider_TL.value()
        display_value = str(round((value / 255) * 380, 0))
        self.experiment.set_threshold_ch_1(value)
        self.left_voltage_TL.setText(display_value)

    def threshold_voltage_ch_2_func(self):
        """
        Changes threshold voltage on channel 1 (PMT 1). Values are allowed in range(0, 254).
        Voltage is calculated as: V = (nBit/255)*380mV
        
        """

        value = self.right_slider_TL.value()
        display_value = str(round((value / 255) * 380, 0))
        self.experiment.set_threshold_ch_2(value)
        self.right_voltage_TL.setText(display_value)

    ##########

    ##### TAB: LIFETIME MEASUREMENT #####
    def start_lifetime_func(self):
        """
        Starts lifetime measurement and data collection
        
        """

        # reset all current values
        self.reset_lifetime_func()

        # ask for filename if none has been given yet
        if self.experiment.filename == None:
            self.save_data()

        # set MuonLab to measure lifetimes and to save data
        self.experiment.set_measurement(lifetime=True)
        self.experiment.start_save = True

        # create timer to update plot
        self.lifetime_timer = QTimer()
        self.lifetime_timer.start(500)
        self.lifetime_timer.timeout.connect(self.update_lifetime_func)

        # set status indicator
        self.status_display_LFT.setText("RUNNING")

    def stop_lifetime_func(self):
        """
        Stops lifetime measurement
        
        """

        # stop automatic updating
        self.lifetime_timer.disconnect()

        # set MuonLab to stop measuring lifetimes
        self.experiment.set_measurement(lifetime=False)

        # update status display
        self.status_display_LFT.setText("STOPPED")

    def reset_lifetime_func(self):
        """
        Resets values in lifetime measurement
        
        """
        self.experiment.lifetimes = []

        # plot empty histogram
        self.figure_LFT.clear()
        ax = self.figure_LFT.add_subplot(111)
        ax.hist([])
        plt.xlim(left=0)
        plt.ylim(bottom=0)
        plt.xlabel("Lifetime (ns)")
        plt.ylabel("Counts")
        plt.grid()
        self.display_LFT.draw()

    def update_lifetime_func(self):
        """ 
        Updates plots and total events in lifetime tab
        
        """

        # get values
        lifetimes = self.experiment.lifetimes
        bins = int(self.bins_dropper_LFT.currentText())
        x_max = self.slider_LFT.value() * 100

        # plot values in histogram
        self.figure_LFT.clear()
        ax_LFT = self.figure_LFT.add_subplot(111)
        ax_LFT.hist(
            lifetimes,
            color=[230 / 255, 25 / 255, 61 / 255],
            edgecolor="black",
            linewidth=0.5,
            bins=bins,
        )
        ax_LFT.set_xlim(0, x_max)
        ax_LFT.set_ylim(bottom=0)
        ax_LFT.set_xlabel("Lifetime (ns)")
        ax_LFT.set_ylabel("Counts")
        ax_LFT.grid()
        self.display_LFT.draw()

        # update total events count
        self.event_display_LFT.setText(str(len(lifetimes)))

    ##########

    ##### TAB: DELTA TIME MEASUREMENT #####
    def start_delta_time_func(self):
        """
        Starts Delta time measurement and data collection
        
        """

        # reset all current values
        self.reset_delta_time_func()

        # ask for filename if none has been given yet
        if self.experiment.filename == None:
            self.save_data()

        # set MuonLab to measure lifetimes and to save data
        self.experiment.set_measurement(delta_time=True)
        self.experiment.start_save = True

        # create timer to update plot
        self.delta_time_timer = QTimer()
        self.delta_time_timer.start(500)
        self.delta_time_timer.timeout.connect(self.update_delta_time_func)

        # set status indicator
        self.status_display_DT.setText("RUNNING")

    def stop_delta_time_func(self):
        """
        Stops Delta time measurement
        
        """

        # stop automatic updating
        self.delta_time_timer.disconnect()

        # set MuonLab to stop measuring Delta times
        self.experiment.set_measurement(delta_time=False)

        # update status display
        self.status_display_DT.setText("STOPPED")

    def reset_delta_time_func(self):
        """
        Resets values in Delta time measurement
        
        """
        self.experiment.delta_times = []

        # plot empty histogram
        self.figure_DT.clear()
        ax = self.figure_DT.add_subplot(111)
        ax.hist([])
        plt.xlim(left=0)
        plt.ylim(bottom=0)
        plt.xlabel("Delta time (ns)")
        plt.ylabel("Counts")
        plt.grid()
        self.display_DT.draw()

    def update_delta_time_func(self):
        """
        Updates plot in Delta time tab
        
        """

        # get values
        delta_times = self.experiment.delta_times
        bins = int(self.bins_dropper_DT.currentText())

        # plot values in histogram
        self.figure_DT.clear()
        ax_DT = self.figure_DT.add_subplot(111)
        ax_DT.hist(
            delta_times,
            color=[230 / 255, 25 / 255, 61 / 255],
            edgecolor="black",
            linewidth=0.5,
            bins=bins,
        )
        ax_DT.set_ylim(bottom=0)
        ax_DT.set_xlabel("Delta time (ns)")
        ax_DT.set_ylabel("Counts")
        ax_DT.grid()
        self.display_DT.draw()

    ##########

    ##### TAB: WAVEFORM CHANNEL 1 #####
    def start_waveform_func(self):
        """
        Programs MuonLab III to return digitised values of the "raw" input signal of
        channel 1.
        
        """

        # set MuonLab to return the digitised input signal of channel 1
        self.experiment.set_measurement(waveform=True)

        # create timer to update plot
        self.signal_timer = QTimer()
        self.signal_timer.start(500)
        self.signal_timer.timeout.connect(self.update_waveform_func)

        # update statys indicator
        self.status_display_WF.setText("RUNNING")

    def stop_waveform_func(self):
        """
        Stops plot in waveform tab
        
        """

        # stop automatic updating
        self.signal_timer.disconnect()

        # set MuonLab to stop returning input signal
        self.experiment.set_measurement(waveform=False)

        # clear plot
        self.figure_WF.clear()
        ax_WF = self.figure_WF.add_subplot(111)
        ax_WF.set_facecolor((0, 0, 0))
        ax_WF.plot([0], [0])
        ax_WF.set_xlim(left=0)
        ax_WF.set_ylim(300, 0)
        ax_WF.set_xlabel("Time (ns)")
        ax_WF.set_ylabel("Amplitude (mV)")
        ax_WF.grid()
        self.display_WF.draw()

        # update status display
        self.status_display_WF.setText("STOPPED")

    def update_waveform_func(self):
        """
        Updates plot in waveform tab
        
        """

        # get values
        total_waveform = self.experiment.input_signal

        # range to view is set with sliders in tab. step size of data = 5ns
        pre_trigger = int(self.pre_trigger_slider_WF.value())
        time_to_display = int(self.time_slider_WF.value())
        n_steps = time_to_display - pre_trigger

        # offset from zero is put in manually
        threshold_value = self.left_slider_TL.value()
        signal_data = total_waveform[pre_trigger:time_to_display]

        x_data = np.arange(0, n_steps) * 5

        # plot values
        self.figure_WF.clear()
        ax_WF = self.figure_WF.add_subplot(111)
        ax_WF.set_facecolor((0, 0, 0))
        # plot data
        ax_WF.plot(x_data, signal_data, color=[230 / 255, 25 / 255, 61 / 255])
        # plot threshold as straight line
        ax_WF.plot(
            [0, x_data[-1]],
            [threshold_value, threshold_value],
            color=[150 / 255, 25 / 255, 61 / 255],
        )
        ax_WF.plot
        ax_WF.set_ylim(300, 0)
        ax_WF.set_xlim(0, x_data[-1])
        ax_WF.set_xlabel("Time (ns)")
        ax_WF.set_ylabel("Amplitude (mV)")
        ax_WF.grid()
        self.display_WF.draw()

    ##########

    ##### TAB: HIT AND COINCIDENCE RATE #####
    def start_hit_rate_func(self):
        """
        Starts hit rate measurements and data collection
        
        """

        ##### TODO: data collection
        # reset all values
        self.reset_hit_rate_func()

        # ask for filename if none has been given yet
        if self.experiment.filename == None:
            self.save_data()

        # set MuonLab to record data
        self.experiment.start_save = True

        # create timer to update all three hit boxes
        self.hit_rate_timer = QTimer()
        self.hit_rate_timer.start(100)
        self.hit_rate_timer.timeout.connect(self.update_hit_rate_func)

        # determine start time to monitor runtime
        self.hit_rate_start_t = datetime.now()

        # set status indicator
        self.status_display_HC.setText("RUNNING")

    def stop_hit_rate_func(self):
        """
        Stops hit rate measurement
        
        """

        # stop automatic updating
        self.hit_rate_timer.disconnect()

        # update status display
        self.status_display_HC.setText("STOPPED")

    def reset_hit_rate_func(self):
        """
        Resets values in hit rate measurement
        
        """

        # set all associated attributes of controller to zero
        self.experiment.hit_byte_counter = 0

        self.experiment.hits_ch1_total = 0
        self.experiment.hits_ch1_last_10 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.experiment.hits_ch1_avg = 0

        self.experiment.hits_ch2_total = 0
        self.experiment.hits_ch2_last_10 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.experiment.hits_ch2_avg = 0

        # reset runtime
        self.hit_rate_start_t = datetime.now()
        zero_time = timedelta(seconds=0)
        self.run_time_HC.setText(str(zero_time))

    def update_hit_rate_func(self):
        """
        Sets values in hit rate boxes in hit rate and coincidence tab
        
        """

        # get values
        # channel 1
        hits_in_last_second_ch1 = str(self.experiment.hits_ch1_last_10[-1])
        hits_total_ch1 = str(self.experiment.hits_ch1_total)
        hits_avg_ch1 = str(round(self.experiment.hits_ch1_avg, 1))

        # channel 2
        hits_in_last_second_ch2 = str(self.experiment.hits_ch2_last_10[-1])
        hits_total_ch2 = str(self.experiment.hits_ch2_total)
        hits_avg_ch2 = str(round(self.experiment.hits_ch2_avg, 1))

        # set display values
        # channel 1
        self.hits_ls_ch1.setText(hits_in_last_second_ch1)
        self.hits_tot_ch1.setText(hits_total_ch1)
        self.hits_avg_ch1.setText(hits_avg_ch1)

        # channel 2
        self.hits_ls_ch2.setText(hits_in_last_second_ch2)
        self.hits_tot_ch2.setText(hits_total_ch2)
        self.hits_avg_ch2.setText(hits_avg_ch2)

        # runtime
        runtime = str(datetime.now() - self.hit_rate_start_t)
        self.run_time_HC.setText(runtime)

    def start_coincidence_func(self):
        """
        Starts coincident hit measurements and data collection
        
        """

        # reset all values
        self.reset_coincidence_func()

        # ask for filename if none has been given yet
        if self.experiment.filename == None:
            self.save_data()

        # set MuonLab to measure coincidences and to save data
        self.experiment.set_measurement(coincidence=True)
        self.experiment.start_save = True

        # create timer to update both coincidence boxes
        self.coincidence_timer = QTimer()
        self.coincidence_timer.start(100)
        self.coincidence_timer.timeout.connect(self.update_coincidence_func)

        # determine start time to monitor runtime
        self.coincidence_start_t = datetime.now()

        # set status indicator
        self.status_display_coin_HC.setText("RUNNING")

    def stop_coincidence_func(self):
        """
        Stops coincident hits measurement

        """

        # stop automatic updating
        self.coincidence_timer.disconnect()

        # set MuonLab to stop measuring coincidences
        self.experiment.set_measurement(coincidence=False)

        # update status display
        self.status_display_coin_HC.setText("STOPPED")

    def reset_coincidence_func(self):
        """
        Resets values in coincident hits measurement
        
        """

        # set all associated attributes of controller to zero
        self.experiment.coincidences = 0

        # reset runtime
        self.coincidence_start_t = datetime.now()
        zero_time = timedelta(seconds=0)
        self.run_time_coin_HC.setText(str(zero_time))

    def update_coincidence_func(self):
        """
        Sets values in coincidence boxes in hit rate and coincidence tab
        
        """

        # get values
        coincidences = self.experiment.coincidences
        runtime = datetime.now() - self.coincidence_start_t
        runtime_in_sec = runtime.total_seconds()
        coincidences_per_sec = round(coincidences / runtime_in_sec, 2)

        # set display values
        self.coin_tot.setText(str(coincidences))
        self.coin_avg.setText(str(coincidences_per_sec))

        # runtime
        self.run_time_coin_HC.setText(str(runtime))

    ##########

    ##### UTILITIES #####
    def closing_func(self):
        """
        Ensures MuonLab III is properly closed before GUI is 
        shut off
        
        """

        # set all MuonLab settings back to default and close measuring loop
        try:
            self.experiment.run_measurements = False
            self.experiment.set_value_PMT_1(0)
            self.experiment.set_value_PMT_2(0)
            self.experiment.set_threshold_ch_1(101)
            self.experiment.set_threshold_ch_2(101)
        except:
            pass

    	# close thread
        try:
            self.main_thread.close()
        except:
            pass

        # close off serial connection to port
        try:
            self.experiment.device.close()
        except:
            pass

    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = user_interface()
    ui.show()
    sys.exit(app.exec())

