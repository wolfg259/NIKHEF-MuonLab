# NIKHEF-MuonLabIII
 
The NIKHEF MuonLab III detector is a commercially available particle detector. With this code, it can be used to execute various experiments, including determining the lifetime of Muons and their velocities, either through a GUI or through terminal controls. Additionally, .ipynb notebooks are provided to perform guided data analysis on the measurements performed. They are written to be accessible, and require no previous knowlegde of Python.

For more information on the MuonLab detector, see: https://www.nikhef.nl/muonlab/

## Installing the software
Open a terminal(also possible in Visual Studio Code) and navigate to the folder you would like the software to be installed in. If you have git installed, run the command: 
```
git clone https://github.com/wolfg259/NIKHEF-MuonLab.git
```

Ensure you have the following packages installed: pyqt5, pyserial. If any ModuleNotFoundError is encountered, install the missing module by running the command (without brackets):
```
pip install {module name}
```

## GUI
The GUI allows the user to change all available settings on the MuonLab, run all available experiments and save the results of the experiment(s) in a .csv file. It is designed to be operated without any coding or experimental experience. Simply choose your settings, choose your experiment and click 'run'. When starting an experiment, a file name is asked of the user under which all data will be saved. The program automatically saves data every thirty seconds during measurements.
To run the GUI, run the command:
```
python ./NIKHEF-MuonLab/GUI/MuonLab_GUI.py
```

## Command line interface
The command line interface controls the MuonLab through the command line. It can execute all MuonLab experiments and automatically sets the detector settings to optimal values. For longer lasting measurements it is recommended to use the GUI, as the command line interface only saves the data after the measurement is complete, and not during the measurement like the GUI does.
To run the command line interface, run the following command and add the experiment to run (without brackets):
```
python ./NIKHEF-MuonLab/terminal_controllers/MuonLab_terminal_controller.py {experiment}
```
To read all available options of the command line interface, run the command:
```
python ./terminal_controllers/MuonLab_terminal_controller.py -h
```

## Notebooks
.ipynb notebooks are available for measurement analysis. They are based around data taken using the MuonLab detector, but can also be run using the sample data "Sample data.csv" in the data folder. It is recommended to run the notebooks using Google CoLab, as this does not require any python or Jupyter installation and can thus be done by anybody on any computer. Simply open a CoLab window and upload the .iypnb file and a data file using a Google account.
