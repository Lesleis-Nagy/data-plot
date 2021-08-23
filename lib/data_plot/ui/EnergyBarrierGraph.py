import mpmath as mp
import numpy

import pyqtgraph

from PyQt5 import QtCore


class EnergyBarrierGraph(pyqtgraph.PlotWidget):

    # Signals
    signal_region_updated = QtCore.pyqtSignal()

    def __init__(self, parent=None, **kwargs):
        pyqtgraph.PlotWidget.__init__(self, **kwargs)

        self.setParent(parent)

        self.setBackground('w')

        self.left_scatter = pyqtgraph.ScatterPlotItem(brush=pyqtgraph.mkBrush(color=(255, 0, 0)))
        self.right_scatter = pyqtgraph.ScatterPlotItem(brush=pyqtgraph.mkBrush(color=(0, 0, 255)))
        self.setLabel("bottom", "Temperature (C)")
        self.setLabel("left", "Relaxation time (log s)")
        self.addItem(self.left_scatter)
        self.addItem(self.right_scatter)

        self.roi = pyqtgraph.RectROI([1, 1], [3, 3], pen=(0, 8))
        self.roi.sigRegionChangeFinished.connect(self.roi_region_change_finished)
        self.addItem(self.roi)

        self.left_temperatures = []
        self.left_relaxation_times = []
        self.left_visible = []

        self.right_temperatures = []
        self.right_relaxation_times = []
        self.right_visible = []

        self.temperatures = []
        self.relaxation_times = []

        self.selected_left_indices = []
        self.selected_right_indices = []

    def roi_region_change_finished(self):
        r"""
        When the region of interest is finished, calculate highlighted points.
        :return:
        """
        lx, ly = self.roi.pos().x(), self.roi.pos().y()
        ux, uy = lx + self.roi.size().x(), ly + self.roi.size().y()

        self.selected_left_indices, self.selected_right_indices = self._find_roi_indices_relaxation_time(lx, ly, ux, uy)

        self.signal_region_updated.emit()

    def set_data(self, left_temperatures, left_relaxation_times, right_temperatures, right_relaxation_times):
        if len(left_temperatures) != len(left_relaxation_times):
            raise ValueError("Left temperatures and relaxation times are different lengths")
        if len(right_temperatures) != len(right_relaxation_times):
            raise ValueError("Right temperatures and relaxation times are different lengths")

        self.left_temperatures = left_temperatures
        self.left_relaxation_times = left_relaxation_times
        self.left_visible = [True]*len(self.left_temperatures)

        self.right_temperatures = right_temperatures
        self.right_relaxation_times = right_relaxation_times
        self.right_visible = [True]*len(self.right_temperatures)

        self.temperatures = self.left_temperatures + self.right_temperatures
        self.relaxation_times = self.left_relaxation_times + self.right_relaxation_times

        self._plot_relaxation_times()

        self.roi_region_change_finished()

    def mask_selected_data(self):
        for index in self.selected_left_indices:
            self.left_visible[index] = False
        for index in self.selected_right_indices:
            self.right_visible[index] = False

        self._plot_relaxation_times()

    def get_masked_data(self):
        left_temperatures = [tvpair[0] for tvpair in zip(self.left_temperatures, self.left_visible) if tvpair[1] is True]
        left_relaxation_times = [tvpair[0] for tvpair in zip(self.left_relaxation_times, self.left_visible) if tvpair[1] is True]
        right_temperatures = [tvpair[0] for tvpair in zip(self.right_temperatures, self.right_visible) if tvpair[1] is True]
        right_relaxation_times = [tvpair[0] for tvpair in zip(self.right_relaxation_times, self.right_visible) if tvpair[1] is True]

        return left_temperatures, left_relaxation_times, right_temperatures, right_relaxation_times

    def _plot_relaxation_times(self):

        self.left_scatter.clear()
        self.right_scatter.clear()

        left_temperatures, left_relaxation_times, right_temperatures, right_relaxation_times = self.get_masked_data()

        self.left_scatter.setData(left_temperatures, left_relaxation_times)
        self.right_scatter.setData(right_temperatures, right_relaxation_times)

    def _find_roi_indices_relaxation_time(self, lx, ly, ux, uy):
        selected_left_indices = []
        selected_right_indices = []

        for index, temp_time_pair in enumerate(zip(self.left_temperatures, self.left_relaxation_times)):
            temperature = temp_time_pair[0]
            relaxation_time = temp_time_pair[1]
            if lx <= temperature <= ux and ly <= relaxation_time <= uy:
                # print(" {} {} is in {} {}, {} {}".format(temperature, energy, lx, ly, ux, uy))
                selected_left_indices.append(index)

        for index, temp_time_pair in enumerate(zip(self.right_temperatures, self.right_relaxation_times)):
            temperature = temp_time_pair[0]
            relaxation_time = temp_time_pair[1]
            if lx <= temperature <= ux and ly <= relaxation_time <= uy:
                # print(" {} {} is in {} {}, {} {}".format(temperature, energy, lx, ly, ux, uy))
                selected_right_indices.append(index)

        return selected_left_indices, selected_right_indices
