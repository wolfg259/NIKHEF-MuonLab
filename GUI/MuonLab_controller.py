import threading
import serial
import serial.tools.list_ports
from datetime import datetime, timedelta


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

        ##### DATA LISTS #####
        # hit rate data
        # counter to help with calculating average while saving 
        self.hits_ch1_total = 0
        self.hits_ch1_last_10 = [0,0,0,0,0,0,0,0,0,0]
        self.hits_ch1_avg = 0

        self.hits_ch2_total = 0
        self.hits_ch2_last_10 = [0,0,0,0,0,0,0,0,0,0]
        self.hits_ch2_avg = 0


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

    def data_acquisition(self, x):
        """
        Infinite loop taking and reading data.
        
        """

        self.flush_input()

        while True:
            # check for beginning of a data message
            byte_1 = self.device.read(1)
            if byte_1 == b"\x99":

                ##### DATA TYPES #####
                # COINCIDENCES
                # check for coincidence data message
                byte_2 = self.device.read(1)
                if byte_2 == b"\x35":

                    bytes_ch2 = self.device.read(2)
                    hit_ch2 = int.from_bytes(bytes_ch2, byteorder="big")
                    bytes_ch1 = self.device.read(2)
                    hit_ch1 = int.from_bytes(bytes_ch1, byteorder="big")
                    # add value and remove last
                    self.hits_ch1_last_10.append(hit_ch1)
                    del self.hits_ch1_last_10[0]
                    self.hits_ch2_last_10.append(hit_ch2)
                    del self.hits_ch2_last_10[0]

                    #hits_ch2.append(hit_ch2)
    
    def test(self, x):
        """ 
        TEST FUNCTION to display taken values
        
        """
        z = x
        start_time = datetime.now()
        dT_max = timedelta(seconds=9, minutes=0, hours=0)
        dT = timedelta(seconds=0.001)
        hits_ch2 = []   

        while dT < dT_max:
            # flush input buffer if  more than 65000 bytes are queued
            self.flush_input()

            dT = datetime.now() - start_time

            # check for beginning of a data message
            byte_1 = self.device.read(1)
            if byte_1 == b"\x99":
                # check for coincidence data message
                byte_2 = self.device.read(1)
                if byte_2 == b"\x35":

                    bytes_ch2 = self.device.read(2)
                    hit_ch2 = int.from_bytes(bytes_ch2, byteorder="big")
                    bytes_ch1 = self.device.read(2)
                    hit_ch1 = int.from_bytes(bytes_ch1, byteorder="big")
                    self.hits_ch1.append(hit_ch1)
                    hits_ch2.append(hit_ch2)

                    #print("     ch1: {} ch2: {}".format(hit_ch1, hit_ch2))

    def test_change_voltage(self):
        self.device.write(b"\x99\x14\xFA\x66")




    def flush_input(self):
        """ 
        Flush device if buffer is too full to avoid overfilling

        """
        
        if self.device.inWaiting() > 65000:
            self.device.flushInput()






def list_devices():
    """
    Returns list of all currently connected devices.

    """
    
    available_ports = []
    ports = serial.tools.list_ports.comports()
    
    for port, _, _ in sorted(ports):
        available_ports.append(port)

    return available_ports

