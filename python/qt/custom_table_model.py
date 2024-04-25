"""
File: custom_table_model.py
Author: Chuncheng Zhang
Date: 2024-04-25
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Amazing things

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-04-25 ------------------------
# Requirements and constants

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex


class CustomTableModel(QAbstractTableModel):
    def __init__(self, df):
        QAbstractTableModel.__init__(self)
        self.load_dataFrame(df)

    def load_dataFrame(self, df):
        self.df = df.copy()
        self.column_count = len(df.columns)
        self.row_count = len(df)

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.df.columns.tolist()[section]
        else:
            return f"{section}"

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            column = index.column()
            row = index.row()
            col = self.df.columns[column]
            value = self.df.iloc[row][col]
            return str(value)
        elif role == Qt.BackgroundRole:
            return QColor(Qt.white)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        return None

    def bind_tableView(self, tableView):
        tableView.setModel(self)
        tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        tableView.viewport().update()
        self.tableView = tableView

    def on_select(self, selected):
        selected_row = selected.toList()[0].top()
        se = self.df.iloc[selected_row]
        print(selected_row)
        print(se)
        print(selected.toList())


# %% ---- 2024-04-25 ------------------------
# Function and class

# %% ---- 2024-04-25 ------------------------
# Play ground


# %% ---- 2024-04-25 ------------------------
# Pending


# %% ---- 2024-04-25 ------------------------
# Pending
