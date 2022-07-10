from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from matplotlib.cbook import boxplot_stats
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

    def __init__(self, 
            set_PMV_tab = True,
            set_TL_tab = True,
            set_LFT_tab = True,
            set_DT_tab = True,
            set_WF_tab = True,
            set_HC_tab = True
        ):
        super().__init__()

        ##### MAIN LAYOUT #####
        # initiating central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # set general options for window
        self.setWindowTitle("MuonLab III v0.1")
        self.setWindowIcon(QIcon(
            "C:\\Users\\DELL\Desktop\\Internship summer\\own code\\src\\NIKHEF-MuonLabIII\\GUI\\nikhef_logo.png"
            ))
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
        # (QFrame creates border)
        counts1_vbox = QFrame()
        counts1_vbox.setFrameShape(QFrame.StyledPanel)
        counts1_vbox.setLayout(QVBoxLayout())

        counts2_vbox = QFrame()
        counts2_vbox.setFrameShape(QFrame.StyledPanel)
        counts2_vbox.setLayout(QVBoxLayout())

        # create text boxes to display counts
        box_counts_1 = QLineEdit()
        box_counts_1.setFixedWidth(100)
        box_counts_1.setReadOnly(True)
        label_box_counts1 = QLabel("Counts/s PMT 1 \n last 10 sec average")

        box_counts_2 = QLineEdit()
        box_counts_2.setFixedWidth(100)
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
            left_slider.setTickPosition(QSlider.TicksBelow)
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
            right_slider.setTickPosition(QSlider.TicksBelow)
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
            #left_slider_label_TL = QLabel("Set Input PMT 1")
            left_slider_TL = QSlider(Qt.Horizontal)
            left_slider_TL.setTickPosition(QSlider.TicksBelow)
            left_slider_layout_TL.layout().addWidget(QLabel("Set threshold voltage"))
            left_slider_layout_TL.layout().addWidget(left_slider_TL)
            left_input_layout_TL.layout().addWidget(left_slider_layout_TL)
            # voltage
            left_voltage_layout_TL = QFrame()
            left_voltage_layout_TL.setLayout(QVBoxLayout())
            left_voltage_label_TL = QLabel("Threshold voltage (mV)")
            left_voltage_TL = QLineEdit()
            left_voltage_TL.setFixedWidth(100)
            left_voltage_TL.setReadOnly(True)
            left_voltage_layout_TL.layout().addWidget(left_voltage_label_TL)
            left_voltage_layout_TL.layout().addWidget(left_voltage_TL)
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
            #right_slider_label_TL = QLabel("Set Input PMT 1")
            right_slider_TL = QSlider(Qt.Horizontal)
            right_slider_TL.setTickPosition(QSlider.TicksBelow)
            #right_slider_layout_TL.layout().addWidget(right_slider_label_TL)
            right_slider_layout_TL.layout().addWidget(QLabel("Set threshold voltage"))
            right_slider_layout_TL.layout().addWidget(right_slider_TL)
            right_input_layout_TL.layout().addWidget(right_slider_layout_TL)
            # voltage
            right_voltage_layout_TL = QFrame()
            right_voltage_layout_TL.setLayout(QVBoxLayout())
            right_voltage_label_TL = QLabel("Threshold voltage (mV)")
            right_voltage_TL = QLineEdit()
            right_voltage_TL.setFixedWidth(100)
            right_voltage_TL.setReadOnly(True)
            right_voltage_layout_TL.layout().addWidget(right_voltage_label_TL)
            right_voltage_layout_TL.layout().addWidget(right_voltage_TL)
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
            #tab_LFT.setAutoFillBackground(True)
            #tab_LFT.setPalette(palette_red)
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
            slider_LFT = QSlider(Qt.Horizontal)
            slider_LFT.setTickPosition(QSlider.TicksBelow)
            
            frame_settings_LFT.layout().addWidget(slider_label_LFT)
            frame_settings_LFT.layout().addWidget(slider_LFT)
            frame_settings_LFT.layout().addWidget(QLabel("                   "))

            # number of bins
            bins_label_LFT = QLabel("Number of bins")
            bins_dropper_LFT = QComboBox()
            bins_dropper_LFT.addItem("64")
            bins_dropper_LFT.addItem("128")
            bins_dropper_LFT.addItem("2048")

            frame_settings_LFT.layout().addWidget(bins_label_LFT)
            frame_settings_LFT.layout().addWidget(bins_dropper_LFT)
            frame_settings_LFT.layout().addWidget(QLabel("                   "))

            # start/stop experiment
            start_stop_frame_LFT = QFrame()
            start_stop_frame_LFT.setLayout(QHBoxLayout())

            start_frame_LFT = QFrame()
            start_frame_LFT.setLayout(QVBoxLayout())
            start_button_LFT = QPushButton("Start")
            start_frame_LFT.layout().addWidget(QLabel("Record data"))
            start_frame_LFT.layout().addWidget(start_button_LFT)

            stop_frame_LFT = QFrame()
            stop_frame_LFT.setLayout(QVBoxLayout())
            stop_button_LFT = QPushButton("Stop")
            stop_frame_LFT.layout().addWidget(QLabel("   "))
            stop_frame_LFT.layout().addWidget(stop_button_LFT)
            
            status_frame_LFT = QFrame()
            status_frame_LFT.setLayout(QVBoxLayout())
            status_display_LFT = QLineEdit()
            status_display_LFT.setFixedWidth(100)
            status_display_LFT.setReadOnly(True)
            
            status_frame_LFT.layout().addWidget(QLabel("Status"))
            status_frame_LFT.layout().addWidget(status_display_LFT)

            start_stop_frame_LFT.layout().addWidget(start_frame_LFT)
            start_stop_frame_LFT.layout().addWidget(stop_frame_LFT)
            start_stop_frame_LFT.layout().addWidget(status_frame_LFT)

            frame_settings_LFT.layout().addWidget(start_stop_frame_LFT)
            frame_settings_LFT.layout().addWidget(QLabel("                   "))

            # reset display
            reset_button_LFT = QPushButton("Reset")

            frame_settings_LFT.layout().addWidget(QLabel("Reset Display"))
            frame_settings_LFT.layout().addWidget(reset_button_LFT)

            # event counter and resetter
            event_row_LFT = QFrame()
            event_row_LFT.setLayout(QHBoxLayout())
            event_counter_frame_LFT = QFrame()
            event_counter_frame_LFT.setLayout(QVBoxLayout())
            event_display_LFT = QLineEdit()
            event_display_LFT.setFixedWidth(100)
            event_display_LFT.setReadOnly(True)

            event_counter_frame_LFT.layout().addWidget(QLabel("Total events"))
            event_counter_frame_LFT.layout().addWidget(event_display_LFT)

            reset_event_frame_LFT = QFrame()
            reset_event_frame_LFT.setLayout(QVBoxLayout())
            reset_button = QPushButton("Reset")

            reset_event_frame_LFT.layout().addWidget(QLabel("Reset total events"))
            reset_event_frame_LFT.layout().addWidget(reset_button)

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
            display_LFT = pg.PlotWidget()
            display_LFT.setLabel("left", "Counts")
            display_LFT.setLabel("bottom", "Time (us)")

            plot_frame_LFT.layout().addWidget(left_frame_LFT)
            plot_frame_LFT.layout().addWidget(display_LFT)

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

            # start/stop dT measuring
            start_stop_frame_DT = QFrame()
            start_stop_frame_DT.setLayout(QHBoxLayout())

            start_frame_DT = QFrame()
            start_frame_DT.setLayout(QVBoxLayout())
            start_button_DT = QPushButton("Start")
            start_frame_DT.layout().addWidget(QLabel("Record data"))
            start_frame_DT.layout().addWidget(start_button_DT)

            stop_frame_DT = QFrame()
            stop_frame_DT.setLayout(QVBoxLayout())
            stop_button_DT = QPushButton("Stop")
            stop_frame_DT.layout().addWidget(QLabel("   "))
            stop_frame_DT.layout().addWidget(stop_button_DT)

            start_button_DT = QPushButton("Start")
            stop_button_DT = QPushButton("Stop")
            status_frame_DT = QFrame()
            status_frame_DT.setLayout(QVBoxLayout())
            status_display_DT = QLineEdit()
            status_display_DT.setFixedWidth(100)
            status_display_DT.setReadOnly(True)

            status_frame_DT.layout().addWidget(QLabel("Status"))
            status_frame_DT.layout().addWidget(status_display_DT)

            start_stop_frame_DT.layout().addWidget(start_frame_DT)
            start_stop_frame_DT.layout().addWidget(stop_frame_DT)
            start_stop_frame_DT.layout().addWidget(status_frame_DT)

            left_settings_DT.layout().addWidget(start_stop_frame_DT)

            # reset display
            reset_frame_DT = QFrame()
            reset_frame_DT.setLayout(QVBoxLayout())
            reset_button_DT = QPushButton("Reset")

            reset_frame_DT.layout().addWidget(QLabel("Reset Display"))
            reset_frame_DT.layout().addWidget(reset_button_DT)

            left_settings_DT.layout().addWidget(reset_frame_DT)

            left_frame_DT.layout().addWidget(QLabel("                   "))
            left_frame_DT.layout().addWidget(left_settings_DT)
            left_frame_DT.layout().addWidget(QLabel("                   "))

            # display/plotting widget
            plot_frame_DT = QFrame()
            plot_frame_DT.setLayout(QVBoxLayout())
            plot_frame_DT.setFrameShape(QFrame.StyledPanel)
            display_DT = pg.PlotWidget()
            display_DT.setLabel("left", "Counts")
            display_DT.setLabel("bottom", "Time (us)")

            plot_frame_DT.layout().addWidget(display_DT)
            
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
            start_button_WF = QPushButton("Start")
            start_frame_WF.layout().addWidget(QLabel("Record data"))
            start_frame_WF.layout().addWidget(start_button_WF)

            stop_frame_WF = QFrame()
            stop_frame_WF.setLayout(QVBoxLayout())
            stop_button_WF = QPushButton("Stop")
            stop_frame_WF.layout().addWidget(QLabel("   "))
            stop_frame_WF.layout().addWidget(stop_button_WF)

            start_button_WF = QPushButton("Start")
            stop_button_WF = QPushButton("Stop")
            status_frame_WF = QFrame()
            status_frame_WF.setLayout(QVBoxLayout())
            status_display_WF = QLineEdit()
            status_display_WF.setFixedWidth(100)
            status_display_WF.setReadOnly(True)

            status_frame_WF.layout().addWidget(QLabel("Status"))
            status_frame_WF.layout().addWidget(status_display_WF)

            start_stop_frame_WF.layout().addWidget(start_frame_WF)
            start_stop_frame_WF.layout().addWidget(stop_frame_WF)
            start_stop_frame_WF.layout().addWidget(status_frame_WF)

            # pre-trigger time, time displayed
            times_frame_WF = QFrame()
            times_frame_WF.setLayout(QHBoxLayout())

            pre_trigger_frame_WF = QFrame()
            pre_trigger_frame_WF.setLayout(QVBoxLayout())
            pre_trigger_slider_WF = QSlider(Qt.Horizontal)
            pre_trigger_slider_WF.setTickPosition(QSlider.TicksBelow)
            pre_trigger_frame_WF.layout().addWidget(QLabel("Pre-trigger time(ns)"))
            pre_trigger_frame_WF.layout().addWidget(pre_trigger_slider_WF)

            time_disp_frame_WF = QFrame()
            time_disp_frame_WF.setLayout(QVBoxLayout())
            time_slider_WF = QSlider(Qt.Horizontal)
            time_slider_WF.setTickPosition(QSlider.TicksBelow)
            time_disp_frame_WF.layout().addWidget(QLabel("Time (ns)"))
            time_disp_frame_WF.layout().addWidget(time_slider_WF)

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
            display_WF = pg.PlotWidget()
            display_WF.setLabel("left", "Amplitude (mV)")
            display_WF.setLabel("bottom", "Time (ns)")

            plot_frame_WF.layout().addWidget(display_WF)

            tab_WF_layout.addWidget(left_frame_WF)
            tab_WF_layout.addWidget(plot_frame_WF)

            tab_WF.setLayout(tab_WF_layout)

            tabs.addTab(tab_WF, "Waveform Channel 1")

        # TAB 6: HIT & COINCIDENCE RATE
        ##### TODO
        self.plot_widget_HC = pg.PlotWidget()
        tabs.addTab(self.plot_widget_HC, "Hit & Coincidence rate")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = user_interface()
    ui.show()
    sys.exit(app.exec())

