import threading
import serial
import serial.tools.list_ports
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


class MuonLab_experiment:
    """
    Class to communicate with NIKHEF's MuonLab III experiment through a GUI
    (see: nikhef.nl/muonlab). Message protocol available on wiki
    
    """

    def __init__(self, port):
        self.device = serial.Serial(port)

        # set initial settings of setup. see "Message Protocol MuonLab III.pdf" on wiki
        self.device.write(
            b"\x99\x14\x00\x66"
        )  # Set HV on PMT of CH1. HV = 300+((nBit/255)*1500); 00 -> 300V
        self.device.write(
            b"\x99\x15\x00\x66"
        )  # Set HV on PMT of CH2. HV = 300+((nBit/255)*1200); x6A=d106 > 800V
        self.device.write(
            b"\x99\x16\x97\x66"
        )  # Set threshold voltage of PMT on CH1. TV = (nBit/255)*380mV; x22=d34 > 50mV
        self.device.write(
            b"\x99\x17\x97\x66"
        )  # Set threshold voltage of PMT on CH2. TV = (nBit/255)*380mV; x22=d34 > 50mV
        self.device.write(
            b"\x99\x10\x55\x66"
        )  # Set offset ADC CH1 offset = (nBit/255)*380mV x55=d85 = 126 mV
        self.device.write(b"\x99\x20\x08\x66")  # Enable USB for data reception
        # flush buffer to avoid overflowing
        self.flush_input()

        # set saving data to true
        self.start_save = False
        self.filename = None

        # set all possible measurements to inactive initially
        self.measure_lifetime = 0
        self.measure_delta_time = 0
        self.measure_analog_input = 0
        self.measure_coincidences = 0
        self.run_measurements = True

        ##### DATA LISTS #####

        # lifetime data
        self.lifetimes = []

        # delta time data
        self.delta_times = []

        # digitised input signal
        self.input_signal = []

        # hit rate data
        # counter to help with calculating average while saving
        self.hit_byte_counter = 0
        self.hits_ch1_total = 0
        self.hits_ch1_last_10 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.hits_ch1_avg = 0

        self.hits_ch2_total = 0
        self.hits_ch2_last_10 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.hits_ch2_avg = 0

        # coincident data
        self.coincidences = 0

        ##### TOTAL DATA FOR SAVING #####
        # total data objects are created to prevent accidental data loss
        # when for example resetting a measurement in the GUI

        # lifetime data
        self.total_lifetimes = []

        # delta time data
        self.total_delta_times = []

        # hit rate data
        # counter to help with calculating average while saving
        self.hit_byte_counter_total = 0
        self.hits_ch1_total_all_time = 0
        self.hits_ch1_avg_total = 0

        self.hits_ch2_total_all_time = 0
        self.hits_ch2_avg_total = 0

        # coincident data
        self.coincidences_total = 0

    def set_value_PMT_1(self, value):
        """
        Changes voltage over PMT 1. Value provided should be in range(0,254), 254 
        corresponding to the maximum voltage allowed
        
        """

        self.flush_input()

        message = b"\x99" + b"\x14" + bytes([value]) + b"\x66"
        self.device.write(message)

    def set_value_PMT_2(self, value):
        """
        Changes voltage over PMT 1. Value provided should be in range(0,254), 254 
        corresponding to the maximum voltage allowed
        
        """

        self.flush_input()

        message = b"\x99" + b"\x15" + bytes([value]) + b"\x66"
        self.device.write(message)

    def set_threshold_ch_1(self, value):
        """
        Changes threshold voltage over ch1. Value provided should be in 
        range(0,254)
        
        """

        self.flush_input()

        message = b"\x99" + b"\x16" + bytes([value]) + b"\x66"
        self.device.write(message)

    def set_threshold_ch_2(self, value):
        """
        Changes threshold voltage over ch1. Value provided should be in 
        range(0,254)
        
        """

        self.flush_input()

        message = b"\x99" + b"\x17" + bytes([value]) + b"\x66"
        self.device.write(message)

    def set_measurement(
        self, lifetime=None, delta_time=None, waveform=None, coincidence=None
    ):
        """
        Select which measurements the MuonLab will perform by setting desired 
        measurement(s) to True or False. 
        Available experiments are:
            - life-time of Muons
            - delta time between distances
            - digitised values of analog input signal of channel 1
            - coincident measurements
        
        Communication follows Message Protocol MuonLab III (available on wiki, p.3)
        
        """

        # calculate decimal value of selection message byte, leave as is if not specified
        if lifetime == True:
            self.measure_lifetime = 1
        if lifetime == False:
            self.measure_lifetime = 0

        if delta_time == True:
            self.measure_delta_time = 2
        if delta_time == False:
            self.measure_delta_time = 0

        if waveform == True:
            self.measure_analog_input = 4
        if waveform == False:
            self.measure_analog_input = 0

        if coincidence == True:
            self.measure_coincidences = 16
        if coincidence == False:
            self.measure_coincidences = 0

        # + 8 is to always enable USB
        selection_byte_value_decimal = (
            self.measure_lifetime
            + self.measure_delta_time
            + self.measure_analog_input
            + self.measure_coincidences
            + 8
        )

        # write message to MuonLab III
        message = b"\x99" + b"\x20" + bytes([selection_byte_value_decimal]) + b"\x66"
        self.device.write(message)

    def data_acquisition(self):
        """
        Infinite loop taking and reading data. Data messages are sent in the following format:
        
            header  identifier  data(length can vary)   end
            0x99    0x??        0x??                    0x66

        For explicit communication protocol see Message Protocol MuonLab III (available on wiki)
        
        """

        # flush input if too many bytes are queued to avoid overflow
        self.flush_input()

        # save time for saving intervals
        self.start_time_measurements = datetime.now()
        self.start_time_interval = datetime.now()
        self.save_interval = timedelta(seconds=30)

        # runs continuously
        while self.run_measurements == True:
            # check for beginning of a data message
            byte_1 = self.device.read(1)
            if byte_1 == b"\x99":

                ##### DATA TYPES #####
                # check identifier of running data message to determine data type
                byte_2 = self.device.read(1)

                # DIGITISED INPUT SIGNAL
                if byte_2 == b"\xC5":

                    # true data is 2000 bytes but signal is located in first 100
                    data_bytes = self.device.read(100)
                    self.input_signal = list(data_bytes)

                # HIT RATES(always active)
                if byte_2 == b"\x35":

                    self.hit_byte_counter += 1
                    self.hit_byte_counter_total += 1

                    bytes_ch2 = self.device.read(2)
                    hit_ch2 = int.from_bytes(bytes_ch2, byteorder="big")
                    bytes_ch1 = self.device.read(2)
                    hit_ch1 = int.from_bytes(bytes_ch1, byteorder="big")

                    # ch1
                    self.hits_ch1_last_10.append(hit_ch1)
                    del self.hits_ch1_last_10[0]
                    # use previous average and total values counted to avoid creating large list
                    self.hits_ch1_avg = (
                        self.hits_ch1_avg * (self.hit_byte_counter - 1) + hit_ch1
                    ) / self.hit_byte_counter
                    self.hits_ch1_total += hit_ch1

                    self.hits_ch1_avg_total = (
                        self.hits_ch1_avg_total * (self.hit_byte_counter_total - 1)
                        + hit_ch1
                    ) / self.hit_byte_counter_total
                    self.hits_ch1_total_all_time += hit_ch1

                    # ch2
                    self.hits_ch2_last_10.append(hit_ch2)
                    del self.hits_ch2_last_10[0]
                    self.hits_ch2_avg = (
                        self.hits_ch2_avg * (self.hit_byte_counter - 1) + hit_ch2
                    ) / self.hit_byte_counter
                    self.hits_ch2_total += hit_ch2

                    self.hits_ch2_avg_total = (
                        self.hits_ch2_avg_total * (self.hit_byte_counter_total - 1)
                        + hit_ch2
                    ) / self.hit_byte_counter_total
                    self.hits_ch2_total_all_time += hit_ch2

                # COINCIDENT HITS
                if byte_2 == b"\x55":

                    self.coincidences += 1

                    self.coincidences_total += 1

                # LIFETIME
                # TODO: A7 is ch2
                if byte_2 == b"\xA5":

                    # read and convert next 2 bytes corresponding to time
                    bytes_value = self.device.read(2)
                    int_value = int.from_bytes(bytes_value, byteorder="big")
                    # step size = 10 ns
                    time_value = int_value * 10
                    self.lifetimes.append(time_value)
                    self.total_lifetimes.append(time_value)

                # DELTA TIME
                if byte_2 == b"\xB5" or byte_2 == b"\xB7":

                    bytes_time = self.device.read(2)
                    value_time = int.from_bytes(bytes_time, byteorder="big") * 0.5
                    # if identifier == b\'xB7' detector 2 was hit first so time should be reversed
                    if byte_2 == b"\xB7":
                        value_time *= -1
                    self.delta_times.append(value_time)
                    self.total_delta_times.append(value_time)

            # save data every set time interval if measuring
            if self.start_save == True:
                self.current_time = datetime.now()
                if (self.current_time - self.start_time_interval) > self.save_interval:
                    try:
                        self.save_data()
                    except:
                        pass

                    # reset interval timer
                    self.start_time_interval = datetime.now()

    def flush_input(self):
        """ 
        Flush device if buffer is too full to avoid overfilling

        """

        if self.device.inWaiting() > 65000:
            self.device.flushInput()

    def save_data(self):
        """
        Saves measured lifetimes, coincidences, hit rates and delta 
        times in a .csv file.
        
        """

        total_runtime = datetime.now() - self.start_time_measurements
        total_runtime_seconds = total_runtime.total_seconds()

        # make dataframes of all data
        df_runtime = pd.DataFrame({"Total runtime (s)": [total_runtime_seconds]})
        df_hits_ch1 = pd.DataFrame({"Hits channel 1": [self.hits_ch1_total_all_time]})
        df_hits_ch2 = pd.DataFrame({"Hits channel 2": [self.hits_ch2_total_all_time]})
        df_lifetime = pd.DataFrame({"Lifetimes (ns)": self.total_lifetimes})
        df_delta_time = pd.DataFrame({"Delta times (ns)": self.total_delta_times})
        df_coincidence = pd.DataFrame({"Total coincidences": [self.coincidences_total]})

        df_total = pd.concat(
            [
                df_runtime,
                df_hits_ch1,
                df_hits_ch2,
                df_lifetime,
                df_delta_time,
                df_coincidence,
            ],
            axis=1,
        )

        path = f"{self.filename}"

        df_total.to_csv(f"{path}", index=False)


def list_devices():
    """
    Returns list of all currently connected devices.

    """

    available_ports = []
    ports = serial.tools.list_ports.comports()

    for port, _, _ in sorted(ports):
        available_ports.append(port)

    return available_ports

