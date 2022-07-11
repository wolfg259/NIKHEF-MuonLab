from matplotlib.style import available
import serial
import serial.tools.list_ports


class MuonLab_experiment:
    """
    Class to communicate with NIKHEF's MuonLab III experiment (see: nikhef.nl/muonlab).
    Message protocol available on wiki
    
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
            b"\x99\x16\x00\x66"
        )  # SET TO 65 = 101(150mV) # Set threshold voltage of PMT on CH1. TV = (nBit/255)*380mV; x22=d34 > 50mV
        self.device.write(
            b"\x99\x17\x55\x66"
        )  # Set threshold voltage of PMT on CH2. TV = (nBit/255)*380mV; x22=d34 > 50mV
        self.device.write(
            b"\x99\x10\x55\x66"
        )  # Set offset ADC CH1 offset = (nBit/255)*380mV x55=d85 = 126 mV
        self.device.write(b"\x99\x20\x08\x66")  # Enable USB for data reception

        # flush buffer to avoid overflowing
        self.flush_input()

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

