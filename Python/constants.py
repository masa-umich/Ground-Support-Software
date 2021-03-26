from PyQt5.QtCore import *
from PyQt5.QtGui import QColor

"""
Class to hold any constant value that is important to the entire program
"""


class Constants:

    # Dict of fluids. Example call: fluid["HE"] -> Returns 0
    # TODO: I'm picky so change to LOX
    fluid = {
        "HE" :  0,
        0: "HE",
        "Fuel": 1,
        1: "Fuel",
        "OX":   2,
        2: "OX",
        "LN2":  3,
        3: "LN2",
        "Exhaust": 4,
        4: "Exhaust"
    }

    boards = ["Engine Controller", "Flight Computer", "Pressurization Controller",
              "Recovery Controller", "GSE Controller"]

    line_width = 2 # This is actually overiden lol

    BG_color = QColor(0, 22, 44)
    Board_color = QColor(24, 156, 12, 255)
    Indicator_Green_color = QColor(35, 136, 35, 255)
    Indicator_Yellow_color = QColor(255, 191, 0, 255)
    Indicator_Red_color = QColor(210, 34, 45, 255)
    MASA_Blue_color = QColor(0, 39, 76)
    MASA_Beige_color = QColor(238, 238, 234)
    MASA_Scarlet_color = QColor(242, 46, 0)
    MASA_Maize_color = QColor(255, 203, 5)  # #ffcb05

    default_font = "Montserrat"
    monospace_font = "Roboto Mono"

    # List of fluids
    fluids = ["HE", "Fuel", "OX", "LN2", "Exhaust"]

    # Dict of fluid colors. Number on left should match value of fluid dict above.
    # Example call: fluidColor[0] -> Returns Qt.white
    fluidColor = {
        "HE": QColor(255,255,255,255),
        0: QColor(255,255,255,255),
        "Fuel": QColor(255,0,0,255),
        1: QColor(255,0,0,255),
        "OX": QColor(0,255,255,255),
        2: QColor(0,255,255,255),
        "LN2": QColor(0,255,0,255),
        3: QColor(0,255,0,255),
        "Exhaust": QColor(255,150,0,255),
        4: QColor(255,150,0,255)
    }
