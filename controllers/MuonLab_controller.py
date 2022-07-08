# author: Wolf Gautier wolf.gautier@nikhef.nl
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
from pathlib import Path


class MuonLab_III:
    """
    Class to communicate with NIKHEF's MuonLab III, change settings and receive data.
    """

    def __init__(self, port="COM3"):
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
                "Device port not found. Available ports: {}".format(available_ports)
            )

        ##### TODO: make settings adjustable from class init #####
        # set initial settings of setup. see "Message Protocol MuonLab III.pdf" on wiki
        self.device.write(
            b"\x99\x14\xFA\x66"
        )  # (SET AS FA FOR 250(near max voltage)) # Set HV on PMT of CH1. HV = 300+((nBit/255)*1200); x6A=d106 > 800V
        self.device.write(
            b"\x99\x15\xFA\x66"
        )  # Set HV on PMT of CH2. HV = 300+((nBit/255)*1200); x6A=d106 > 800V
        self.device.write(
            b"\x99\x16\x65\x66"
        )  # SET TO 65 = 101(150mV) # Set threshold voltage of PMT on CH1. TV = (nBit/255)*380mV; x22=d34 > 50mV
        self.device.write(
            b"\x99\x17\x65\x66"
        )  # Set threshold voltage of PMT on CH2. TV = (nBit/255)*380mV; x22=d34 > 50mV
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

        if m == 0 and m == 0 and s == 0:
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

        if m == 0 and m == 0 and s == 0:
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

        if m == 0 and m == 0 and s == 0:
            s = 5
        start_time = datetime.now()
        dT_max = timedelta(seconds=s, minutes=m, hours=h)
        dT = timedelta(seconds=0.001)
        hits_ch1 = []
        hits_ch2 = []

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

        if m == 0 and m == 0 and s == 0:
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
        # set device to measure coincidences
        self.device.write(b"\x99\x20\x0A\x66")
        ##### TODO: consider signal received and build function #####

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

        print("")
        print("Saved data at: {}".format(path))
        print("")


if __name__ == "__main__":
    # test run
    ml = MuonLab_III()
    lifetimes = True
    coincidences = True
    hits = True
    delta_time = True
    save = True

    if lifetimes:
        lifetimes = ml.get_lifetimes(s=20)
        if len(lifetimes) != 0:
            print("average lifetime: {} ns".format(np.mean(lifetimes)))
            plt.hist(lifetimes, edgecolor="black")
            plt.grid()
            plt.xlabel("lifetime (ns)")
            plt.show()
        else:
            print("No decays measured")

    if coincidences:
        coin = ml.get_coincidences(s=20, print_coincidence=True)
        print("Total found coincidences: {}".format(coin))

    if hits:
        hits_ch1, hits_ch2 = ml.get_hit_rates(s=1, print_hits=True)
        print(
            "avg hits/s ch1: {} avg hits/s ch2: {}".format(
                round(np.mean(hits_ch1), 2), round(np.mean(hits_ch2))
            )
        )

    if delta_time:
        times = ml.get_delta_time(s=20, print_time=True)
        # plot should be normally distributed around 0 if detectors
        # are not spaced vertically
        if len(times) != 0:
            plt.hist(times, edgecolor="black")
            plt.grid()
            plt.xlabel("Delta time (ns)")
            plt.show()

    if save:
        ml.save_data()

