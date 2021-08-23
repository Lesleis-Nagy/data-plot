import sys

from argparse import ArgumentParser

from PyQt5.QtWidgets import QApplication

from data_plot.ui.MainWindow import MainWindow


def command_line_parser():
    parser = ArgumentParser()

    parser.add_argument("input_file", help="The input file to process")
    parser.add_argument("output_file", help="The output file to save to")

    return parser


if __name__ == "__main__":
    parser = command_line_parser()
    args = parser.parse_args()

    app = QApplication([])
    window = MainWindow(args)
    window.show()

    sys.exit(app.exec_())
