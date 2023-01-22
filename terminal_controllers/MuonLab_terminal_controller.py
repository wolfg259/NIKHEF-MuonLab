# author: Wolf Gautier wolf.gautier@nikhef.nl
# coauthor: Rowen Hersche rowen.hersche@student.uva.nl
# 05/07/2022
# this file contains a controlling class for the NIKHEF MuonLab III
# device (see https://www.nikhef.nl/muonlab/)

from logging import raiseExceptions
import serial
import serial.tools.list_ports
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import argparse
from pathlib import Path


class MuonLab_III:
    """
    Class to communicate with NIKHEF's MuonLab III, change settings and receive data.
    """

    def __init__(self, filename, port="COM3"):
        # try to find device or list available devices if device can't be found
        try:
            self.device = serial.Serial(port)
        except:
            self.device = None
            ports = serial.tools.list_ports.comports()
            available_ports = []
            for port, _, _ in sorted(ports):
                available_ports.append(port)

            raise Exception(
                "Device port {} not found. Available ports: {}. If working with linux, please ensure rwx permissions are set correctly by running sudo chmod 777 {}".format(port, available_ports, port)
            )

        self.filename = filename


        # make bytes from terminal commands for initial settings. see "Message Protocol MuonLab III.pdf" on wiki 
        if 300 <= args.voltage <= 1700:
        	voltage_value = int(((args.voltage-300)/1400)*255) # HV = 300+((nBit/255)*1400); x6A=d106 > 800V; Default = 1673V = 250bit
        	if voltage_value > 255: 
        		voltage_value = 255 
        else:
        	voltage_value = 0
        	raise OSError(
                "Give voltage value between 300V and 1700V")   
        voltage_pmt1 = b"\x99" + b"\x14" + bytes([voltage_value]) + b"\x66"
        voltage_pmt2 = b"\x99" + b"\x15" + bytes([voltage_value]) + b"\x66"
        
        if args.threshold <= 380:
        	threshold_value = int((args.threshold/380)*255) # TV = (nBit/255)*380mV; x22=d34 > 50mV; Default = 151mV = 101bit 
        else:
        	threshold_value = 0
        	raise OSError(
                "Give threshold value between 0mV and 380mV") 
        threshold_pmt1 = b"\x99" + b"\x16" + bytes([threshold_value]) + b"\x66"
        threshold_pmt2 = b"\x99" + b"\x17" + bytes([threshold_value]) + b"\x66"

	# set initial settings of setup
        self.device.write(
            voltage_pmt1
        ) # Set HV on PMT of CH1
        self.device.write(
            voltage_pmt2
        )  # Set HV on PMT of CH2.
        self.device.write(
            threshold_pmt1
        ) # Set threshold voltage of PMT on CH1.
        self.device.write(
            threshold_pmt2
        )  # Set threshold voltage of PMT on CH2. 
        self.device.write(
            b"\x99\x10\x55\x66"
        )  # Set offset ADC CH1 offset = (nBit/255)*380mV x55=d85 = 126 mV
        self.device.write(b"\x99\x20\x08\x66")  # Enable USB for data reception

        # create lists to save all measurement data
        self.lifetimes = []
        self.coincidences = 0
        self.hit_rate_ch1 = []
        self.hit_rate_ch2 = []
        self.delta_times = []

    def get_lifetimes(self, s=0, m=0, h=0, print_lifetime=False):
        """
        Measures lifetimes of muons detected for set time duration.
        
        Arguments:
            s: seconds
            m: minutes
            h: hours
            print_lifetime: print lifetime to screen each time one is measured
        
        Returns:
            lifetimes: list of measured lifetimes in ns

        """
        # set device to measure lifetime
        self.device.write(b"\x99\x20\x09\x66")

        if h == 0 and m == 0 and s == 0:
            s = 5
        start_time = datetime.now()
        dT_max = timedelta(seconds=s, minutes=m, hours=h)
        dT = timedelta(seconds=0.001)
        lifetimes = []

        print("")
        print(
            "Started lifetime measurement at {}. Set duration: {}".format(
                datetime.now(), dT_max
            )
        )

        # loop running while time difference < dT
        while dT < dT_max:
            # flush input buffer if  more than 65000 bytes are queued
            if self.device.inWaiting() > 65000:
                self.device.flushInput()
            else:
                dT = datetime.now() - start_time

                # check for beginning of a data message
                byte_1 = self.device.read(1)
                if byte_1 == b"\x99":
                    # check for life-time data message
                    byte_2 = self.device.read(1)
                    if byte_2 == b"\xA5":

                        # read and convert next 2 bytes corresponding to time
                        bytes_value = self.device.read(2)
                        int_value = int.from_bytes(bytes_value, byteorder="big")
                        # step size = 10 ns
                        time_value = int_value * 10
                        lifetimes.append(time_value)

                        self.save_data(self.filename)

                        if print_lifetime:
                            print("     measured lifetime: {} ns".format(time_value))

        # add to total
        self.lifetimes.extend(lifetimes)
        print("Finished lifetime measurement.")
        print("")

        return lifetimes

    def get_coincidences(self, s=0, m=0, h=0, print_coincidence=False):
        """
        Measures total amount of coincident hits in set time duration.

        Arguments:
            s: seconds
            m: minutes
            h: hours
            print_lifetime: print lifetime to screen each time one is measured
        
        Returns:
            lifetimes: list of measured lifetimes in ns

        """
        # set device to measure coincidences
        self.device.write(b"\x99\x20\x09\x66")

        if h == 0 and m == 0 and s == 0:
            s = 5
        start_time = datetime.now()
        dT_max = timedelta(seconds=s, minutes=m, hours=h)
        dT = timedelta(seconds=0.001)
        coincidences = 0

        print("")
        print(
            "Started coincidence measurement at {}. Set duration: {}".format(
                datetime.now(), dT_max
            )
        )

        # loop running while time difference < dT
        while dT < dT_max:
            # flush input buffer if  more than 65000 bytes are queued
            if self.device.inWaiting() > 65000:
                self.device.flushInput()
            else:
                dT = datetime.now() - start_time

                # check for beginning of a data message
                byte_1 = self.device.read(1)
                if byte_1 == b"\x99":
                    # check for coincidence data message
                    byte_2 = self.device.read(1)
                    if byte_2 == b"\x55":

                        coincidences += 1
                        if print_coincidence:

                            self.save_data(self.filename)

                            print(
                                "     measured coincidence. total: {}".format(
                                    coincidences
                                )
                            )

        # add to total
        self.coincidences += coincidences
        print("Finished coincidence measurement.")
        print("")

        return coincidences

    def get_hit_rates(self, s=0, m=0, h=0, print_hits=False):
        """
        Measures total amount of coincident hits for a set time duration.

        Arguments:
            s: seconds
            m: minutes
            h: hours
            print_lifetime: print lifetime to screen each time one is measured
        
        Returns:
            hits_ch1: hits registered on ch1 in the last second
            hits_ch2: hits registered on ch2 in the last second
        """
        # note: no need to change device settings, hit rates always returned

        if h == 0 and m == 0 and s == 0:
            s = 5
        start_time = datetime.now()
        dT_max = timedelta(seconds=s, minutes=m, hours=h)
        dT = timedelta(seconds=0.001)
        hits_ch1 = []
        hits_ch2 = []
        self.a = "xFA" 

        print("")
        print(
            "Started hit rate collection at {}. Set duration: {}".format(
                datetime.now(), dT_max
            )
        )

        # loop running while time difference < dT
        while dT < dT_max:
            # flush input buffer if  more than 65000 bytes are queued
            if self.device.inWaiting() > 65000:
                self.device.flushInput()
            else:
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
                        hits_ch1.append(hit_ch1)
                        hits_ch2.append(hit_ch2)

                        self.save_data(self.filename)

                        if print_hits:
                            print("     ch1: {} ch2: {}".format(hit_ch1, hit_ch2))

        # add to total
        self.hit_rate_ch1.extend(hits_ch1)
        self.hit_rate_ch2.extend(hits_ch2)
        print("Finished hit rate collection.")
        print("")

        return hits_ch1, hits_ch2

    def get_delta_time(self, s=0, m=0, h=0, print_time=False):
        """ 
        Measures time between hits on detectors for a set time duration.
        The detectors shoul be set up with a vertical distance, otherwise
        the delta times will be normally distributed.

        Arguments:
            s: seconds
            m: minutes
            h: hours
            print_lifetime: print lifetime to screen each time one is measured
        
        Returns:
            delta_times: list of all measured delta times

        """

        # set device to measure coincidences
        self.device.write(b"\x99\x20\x0A\x66")

        if h == 0 and m == 0 and s == 0:
            s = 5
        start_time = datetime.now()
        dT_max = timedelta(seconds=s, minutes=m, hours=h)
        dT = timedelta(seconds=0.001)
        delta_times = []

        print("")
        print(
            "Started delta time measurement at {}. Set duration: {}".format(
                datetime.now(), dT_max
            )
        )

        while dT < dT_max:

            # flush input buffer if  more than 65000 bytes are queued
            if self.device.inWaiting() > 65000:
                self.device.flushInput()
            else:
                dT = datetime.now() - start_time

                # check for beginning of a data message
                value = self.device.read(1)
                if value == b"\x99":
                    # check for delta time message
                    byte_2 = self.device.read(1)
                    if byte_2 == b"\xB5" or byte_2 == b"\xB7":

                        bytes_time = self.device.read(2)
                        value_time = int.from_bytes(bytes_time, byteorder="big") * 0.5
                        # if identifier == b\'xB7' detector 2 was hit first so time should be reversed
                        if byte_2 == b"\xB7":
                            value_time *= -1
                        delta_times.append(value_time)

                        self.save_data(self.filename)

                        if print_time:
                            print("     measured delta time: {}".format(value_time))

        # add to total
        self.delta_times.extend(delta_times)
        print("Finished delta time measurement")
        print("")

        return delta_times

    def get_signal(self):
        """
        Get the analog input signal of channel 1 as digitised values.
        
        Returns:
            signal: list of digitised values

        """        
        #### TODO: make signal list and plot available from terminal ####
        #set device to measure coincidences
        self.device.write(b"\x99\x20\x0A\x66")
        
        data_bytes = self.device.read(100) # get first 100 signals from photomultiplier 1
        input_signal = list(data_bytes) # signal values are seperated by 5 ns; total signal time = 2 microseconds
        
        return input_signal
	
    def save_data(self, name="unnamed"):
        """
        Saves measured lifetimes, coincidences, hit rates and delta 
        times in a .csv file.

        """

        if len(self.lifetimes) == 0:
            self.lifetimes.append("None measured")
        if len(self.hit_rate_ch1) == 0:
            self.hit_rate_ch1.append("None measured")
        if len(self.hit_rate_ch2) == 0:
            self.hit_rate_ch2.append("None measured")
        if len(self.delta_times) == 0:
            self.delta_times.append("None measured")

        # make dataframes of all data
        df_coincidence = pd.DataFrame({"Total coincidences": [self.coincidences]})
        df_lifetime = pd.DataFrame({"Lifetimes": self.lifetimes})
        df_hits_ch1 = pd.DataFrame({"Hits channel 1": self.hit_rate_ch1})
        df_hits_ch2 = pd.DataFrame({"Hits channel 2": self.hit_rate_ch2})
        df_delta_time = pd.DataFrame({"Delta times": self.delta_times})

        df_total = pd.concat(
            [df_hits_ch1, df_hits_ch2, df_lifetime, df_delta_time, df_coincidence],
            axis=1,
        )

        Path("./data").mkdir(parents=True, exist_ok=True)
        path = f"./data/{name}.csv"

        df_total.to_csv(f"{path}", index=False)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Control the NIKHEF MuonLab setup.")
    parser.add_argument(
        "port",
        type=str,
        default=None,
        help="choose which connected USB device to run. (on linux: usually /dev/ttyUSB0 )"
    )
    parser.add_argument(
        "experiment",
        type=str,
        default=None,
        help="choose which experiment to run. options: lifetimes, coincidences, hits, delta_times",
    )
    parser.add_argument(
        "--seconds",
        "-s",
        type=int,
        default=0,
        help="number of seconds to run experiment for",
    )
    parser.add_argument(
        "--minutes",
        "-m",
        type=int,
        default=0,
        help="number of minutes to run experiment for",
    )
    parser.add_argument(
        "--hours",
        "-hrs",
        type=int,
        default=0,
        help="number of hours to run experiment for",
    )
    parser.add_argument(
        "--filename",
        "-f",
        type=str,
        default="unnamed",
        help="filename under which data is saved",
    )
    parser.add_argument(
        "--print",
        "-p",
        type=bool,
        default=True,
        help="print values to screen during measurement",
    )
    parser.add_argument(
    	"--voltage",
    	"-v",
    	type=int,
    	default=1645,
    	help="set voltage of photomultiplier Channel 1 and 2",
    )
    parser.add_argument(
    	"--threshold",
    	"-t",
    	type=int,
    	default=151,
    	help="set threshold value of Channel 1 and 2",
    )
    args = parser.parse_args()
    experiments = ["lifetimes", "coincidences", "hits", "delta_times"]

    if args.experiment in experiments:
        ml = MuonLab_III(port=args.port, filename=args.filename)
        lifetimes = False
        coincidences = False
        hits = False
        delta_times = False
        signal = False

        print("")
        print("Saving data at: ./data/{}".format(args.filename))

        if args.experiment == "lifetimes":
            lifetimes = True
        if args.experiment == "coincidences":
            coincidences = True
        if args.experiment == "hits":
            hits = True
        if args.experiment == "delta_times":
            delta_times = True

        if lifetimes:
            lifetimes = ml.get_lifetimes(
                s=args.seconds, m=args.minutes, h=args.hours, print_lifetime=args.print,
            )
            if len(lifetimes) != 0:
                print("average lifetime: {} ns".format(np.mean(lifetimes)))
                plt.hist(lifetimes, edgecolor="black")
                plt.grid()
                plt.xlabel("lifetime (ns)")
                plt.show()
            else:
                print("No decays measured")

        if coincidences:
            coin = ml.get_coincidences(
                s=args.seconds,
                m=args.minutes,
                h=args.hours,
                print_coincidence=args.print,
            )
            print("Total found coincidences: {}".format(coin))

        if hits:
            hits_ch1, hits_ch2 = ml.get_hit_rates(
                s=args.seconds, m=args.minutes, h=args.hours, print_hits=args.print,
            )
            print(
                "avg hits/s ch1: {} avg hits/s ch2: {}".format(
                    round(np.mean(hits_ch1), 2), round(np.mean(hits_ch2))
                )
            )

        if delta_times:
            times = ml.get_delta_time(
                s=args.seconds, m=args.minutes, h=args.hours, print_time=args.print,
            )
            # plot should be normally distributed around 0 if detectors
            # are not spaced vertically
            if len(times) != 0:
                plt.hist(times, edgecolor="black")
                plt.grid()
                plt.xlabel("Delta time (ns)")
                plt.show()
                
        ml.save_data(args.filename)
        print("")

    else:
        print(
            "\nThe specified experiment was not recognised. execute MuonLab_terminal_controller.py -h for available options.\n"
        )

