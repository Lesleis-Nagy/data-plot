import pandas as pd

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow

from data_plot.ui.MainWindowBase import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, args):
        super(self.__class__, self).__init__()

        # Set the user interface from Designer.
        self.setupUi(self)

        # Command line arguments
        self.args = args

        # Events
        self.energy_barrier_graph.signal_region_updated.connect(self.energy_barrier_graph_region_updated)
        self.btn_save.clicked.connect(self.btn_save_clicked)
        self.btn_delete.clicked.connect(self.btn_delete_clicked)

        lTs, lEs, lts, luids, rTs, rEs, rts, ruids = self.read_data()

        self.energy_barrier_graph.set_data(lTs, lts, rTs, rts)

    @QtCore.pyqtSlot()
    def energy_barrier_graph_region_updated(self):
        pass

    @QtCore.pyqtSlot()
    def btn_save_clicked(self):
        left_temperatures, left_relaxation_times, right_temperatures, right_relaxation_times = self.energy_barrier_graph.get_masked_data()

        if len(left_temperatures) != len(left_relaxation_times):
            raise ValueError("Attempting to save cleaned data - left temperatures and relaxation times should be of same value")
        if len(right_temperatures) != len(right_relaxation_times):
            raise ValueError("Attempting to save cleaned data - right temperatures and relaxation times should be of same value")

        left_text = ["left"]*len(left_temperatures)
        right_text = ["right"]*len(right_temperatures)

        temperatures = left_temperatures + right_temperatures
        relaxation_times = left_relaxation_times + right_relaxation_times
        left_right_text = left_text + right_text

        df = pd.DataFrame.from_dict(
            {"Temperature (C)": temperatures,
             "Relaxation times (log s)": relaxation_times,
             "Barrier type": left_right_text})

        print("Saving '{}'".format(self.args.output_file))
        df.to_csv(self.args.output_file)

    @QtCore.pyqtSlot()
    def btn_delete_clicked(self):
        self.energy_barrier_graph.mask_selected_data()

    def read_data(self):
        df = pd.read_csv(self.args.input_file)

        left_temperatures = df.iloc[:, 1].tolist()
        left_energies = df.iloc[:, 2].tolist()
        left_log_relaxation_times = df.iloc[:, 3].tolist()
        left_unique_ids = df.iloc[:, 4].tolist()

        right_temperatures = df.iloc[:, 5].tolist()
        right_energies = df.iloc[:, 6].tolist()
        right_log_relaxation_times = df.iloc[:, 7].tolist()
        right_unique_ids = df.iloc[:, 8].tolist()

        return left_temperatures, left_energies, left_log_relaxation_times, left_unique_ids, \
               right_temperatures, right_energies, right_log_relaxation_times, right_unique_ids
