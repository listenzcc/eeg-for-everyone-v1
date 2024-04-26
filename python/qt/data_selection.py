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
from PySide6.QtWidgets import QRadioButton, QButtonGroup

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


class ProtocolRatioButton(QRadioButton):
    protocol = None

    def __init__(self, protocol: str, parent):
        super().__init__(protocol, parent)
        self.protocol = protocol
        self.clicked.connect(self.on_click)

    def on_click(self):
        print(self.protocol)
        return self.protocol


class DataSelectionWindow(BaseWindow):
    layout_path = project_root.joinpath('layout/data_selection.ui')

    # Known components
    lineEdit_pathFilter = None
    scrollArea_detailDisplay = None
    scrollArea_invalidDataSelection = None
    tableView_validDataSelection = None
    horizontalLayout_protocolSelection = None
    label_totalFiles = None

    # The table of found files
    files_table = load_files_table()

    # variables
    selected_files = []
    protocol = None

    def __init__(self):
        super().__init__(loader.load(self.layout_path, None))
        self.assign_children()
        self.setup_protocols()
        self.connect_functions()

    def setup_protocols(self):
        protocols = sorted(set(self.files_table['protocol'].to_list()))
        logger.debug(f'Found protocols: {protocols}')

        group = QButtonGroup(self.window)

        def _select_protocol():
            protocol = group.checkedButton().text()
            self.protocol = protocol
            self.connect_functions()
            logger.debug(f'Selected protocol: {protocol}')

        for protocol in protocols:
            button = QRadioButton(protocol, self.window)
            group.addButton(button)
            button.clicked.connect(_select_protocol)
            self.horizontalLayout_protocolSelection.addWidget(button)
            logger.debug(f'Set protocol button: {protocol}')

        button.click()

    def connect_functions(self):
        # --------------------
        model = CustomTableModel()
        display_columns = ['protocol', 'path', 'status', 'format']

        # --------------------
        # Path filter

        def _textChanged(text):
            logger.debug(f'Changed pathFilter text: {text}')

            df = self.files_table.copy()
            df = df[df['protocol'] == self.protocol]
            df = df[df['path'].map(
                lambda e: text.upper() in str(e).upper())]
            self.label_totalFiles.setText(f'Total files: {len(df)}')

            model.load_dataFrame(df, display_columns=display_columns)
            model.bind_tableView(self.tableView_validDataSelection)
            model.tableView.selectionModel().selectionChanged.connect(_selectionChanged)
            logger.debug('Updated tableView')

        self.lineEdit_pathFilter.setText('')
        self.lineEdit_pathFilter.textChanged.connect(_textChanged)

        # --------------------
        # Files table
        def _selectionChanged(selected):
            se = model.on_select(selected)
            self.selected_files.append(se)
            logger.debug(f'Selected file: {se}')

        df = self.files_table.copy()
        df = df[df['protocol'] == self.protocol]
        self.label_totalFiles.setText(f'Total files: {len(df)}')

        model.load_dataFrame(df, display_columns=display_columns)
        model.bind_tableView(self.tableView_validDataSelection)
        model.tableView.selectionModel().selectionChanged.connect(_selectionChanged)
        self.tableView_validDataSelection.setColumnWidth(1, 400)


# %% ---- 2024-04-25 ------------------------
# Play ground


# %% ---- 2024-04-25 ------------------------
# Pending


# %% ---- 2024-04-25 ------------------------
# Pending
