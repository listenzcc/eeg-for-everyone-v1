"""
File: data_selection.py
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
from rich import inspect

import pandas as pd
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QAbstractItemView

from .load_window import BaseWindow
from .custom_table_model import CustomTableModel
from . import logger, project_root, cache_path

# --------------------
loader = QUiLoader()

# %% ---- 2024-04-25 ------------------------
# Function and class


def load_files_table():
    found_files = pd.read_pickle(cache_path.joinpath('found_files'))
    check_results = pd.read_pickle(cache_path.joinpath('check_results'))
    df = pd.merge(check_results, found_files, on='path')
    logger.debug(f'Loaded files table:\n{df}')
    return df


class DataSelectionWindow(BaseWindow):
    layout_path = project_root.joinpath('layout/data_selection.ui')

    # Known components
    lineEdit_pathFilter = None
    scrollArea_detailDisplay = None
    scrollArea_invalidDataSelection = None
    tableView_validDataSelection = None

    # The table of found files
    files_table = load_files_table()

    def __init__(self):
        super().__init__(loader.load(self.layout_path, None))
        self.assign_children()
        self.connect_functions()

    def connect_functions(self):
        # --------------------
        # Path filter
        def foo(text):
            logger.debug(f'Changed pathFilter text: {text}')
            df = self.files_table.copy()
            df = df[df['short_name'].map(
                lambda e: text.upper() in str(e).upper())]
            # model = CustomTableModel(df)
            # self.tableView_validDataSelection.setModel(model)
            model.load_dataFrame(df)
            model.bind_tableView(self.tableView_validDataSelection)
            self.tableView_validDataSelection.viewport().update()
            logger.debug('Updated tableView')

        self.lineEdit_pathFilter.textChanged.connect(foo)

        # --------------------
        # Files table
        model = CustomTableModel(self.files_table)
        model.bind_tableView(self.tableView_validDataSelection)

        def foo(selected):
            selected_row = selected.toList()[0].top()
            print(selected_row)
            print(selected.toList())

        # model.tableView.selectionModel().selectionChanged.connect(foo)
        model.tableView.selectionModel().selectionChanged.connect(model.on_select)

        # self.tableView_validDataSelection.setModel(model)
        # # Select only a single row
        # self.tableView_validDataSelection.setSelectionBehavior(
        #     QAbstractItemView.SelectRows)
        # self.tableView_validDataSelection.setSelectionMode(
        #     QAbstractItemView.SingleSelection)

        # def foo(selected):
        #     selected_row = selected.toList()[0].top()
        #     print(selected_row)
        #     print(selected.toList())

        # model = self.tableView_validDataSelection.selectionModel()
        # model.selectionChanged.connect(foo)
        # # inspect(self.tableView_validDataSelection.selectionChanged, all=True)
        # # print(dir(self.tableView_validDataSelection))


# %% ---- 2024-04-25 ------------------------
# Play ground


# %% ---- 2024-04-25 ------------------------
# Pending


# %% ---- 2024-04-25 ------------------------
# Pending
