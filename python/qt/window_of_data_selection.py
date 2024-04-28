"""
File: window_of_data_selection.py
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
from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QRadioButton, QButtonGroup

from .load_window import BaseWindow
from .custom_table_model import CustomTableModel
from . import logger, project_root, cache_path

# --------------------
loader = QUiLoader()

# %% ---- 2024-04-25 ------------------------
# Function and class


def load_files_table(map):
    found_files = pd.read_pickle(cache_path.joinpath('found_files'))
    check_results = pd.read_pickle(cache_path.joinpath('check_results'))
    df = pd.merge(check_results, found_files, on='path')

    df = df[df.apply(map, axis=1)]

    logger.debug(f'Loaded files table:\n{df}')
    return df


class DataSelectionWindow(BaseWindow):
    layout_path = project_root.joinpath('layout/data_selection.ui')

    # Known components
    # --
    comboBox_protocolSelection = None
    # --
    lineEdit_pathFilter = None
    label_filteredFiles = None
    tableView_validDataSelection = None
    pushButton_chooseAllFiles = None
    textBrowser_candidateFileDetail = None
    pushButton_chooseFile = None
    pushButton_clearChosenFiles = None
    listWidget_chosenFiles = None
    # --
    listWidget_failedFiles = None
    textBrowser_failedFiles = None

    # The table of found files
    files_table = load_files_table(lambda se: se['status'] != 'failed')
    failed_files_table = load_files_table(lambda se: se['status'] == 'failed')

    # variables
    protocol = None
    candidate_file = None
    chosen_files = []
    filtered_files = []

    def __init__(self):
        super().__init__(loader.load(self.layout_path, None))
        self.connect_choose_file_functions()
        self.setup_protocols()

    def setup_protocols(self):
        """
        Sets up the protocols for selection and connects the protocol selection event.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        protocols = sorted(set(self.files_table['protocol'].to_list()))
        logger.debug(f'Found protocols: {protocols}')

        self.comboBox_protocolSelection.addItems(protocols)

        def _select_protocol(protocol: str):
            self.protocol = protocol
            self.refresh_with_current_protocol()
            self.refresh_failed_files_with_current_protocol()
            logger.debug(f'Selected protocol: {protocol}')

        self.comboBox_protocolSelection.currentTextChanged.connect(
            _select_protocol)
        _select_protocol(self.comboBox_protocolSelection.currentText())

    def connect_choose_file_functions(self):
        """
        Connects the choose file and discard clicked file functions to their respective UI elements.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        # --------------------
        # Launch choose file operation and related functions

        def _choose_candidate_file():
            if self.candidate_file is None:
                return
            if self.candidate_file not in self.chosen_files:
                self.chosen_files.append(self.candidate_file)
            self.update_listWidget_chosenFiles()

        self.pushButton_chooseFile.clicked.connect(_choose_candidate_file)

        def _choose_all_filtered_files():
            for file in self.filtered_files:
                if file not in self.chosen_files:
                    self.chosen_files.append(file)
            self.update_listWidget_chosenFiles()

        self.pushButton_chooseAllFiles.clicked.connect(
            _choose_all_filtered_files)

        def _discard_clicked_file():
            idx = self.listWidget_chosenFiles.currentRow()
            file = self.chosen_files.pop(idx)
            self.update_candidate_file(file)
            logger.debug(f'Discard file: {file}')
            self.update_listWidget_chosenFiles()

        self.listWidget_chosenFiles.itemDoubleClicked.connect(
            _discard_clicked_file)

        def _only_update_candidate_file():
            idx = self.listWidget_chosenFiles.currentRow()
            file = self.chosen_files[idx]
            self.update_candidate_file(file)

        self.listWidget_chosenFiles.itemClicked.connect(
            _only_update_candidate_file)

        def _clear_all_chosen_files():
            self.chosen_files = []
            self.update_listWidget_chosenFiles()
            logger.debug('Clear all the chosen files')

        self.pushButton_clearChosenFiles.clicked.connect(
            _clear_all_chosen_files)

    def refresh_failed_files_with_current_protocol(self):
        df = self.failed_files_table.copy()
        df = df[df['protocol'] == self.protocol]
        files = sorted(
            [e for i, e in df.iterrows()],
            key=lambda se: se['path'])

        logger.debug(f'Found failed files: {files}')

        def _select_failed_file():
            idx = self.listWidget_failedFiles.currentRow()
            file = files[idx]
            text = '\n'.join(f'{k}: \t{v}' for k, v in file.items())
            self.textBrowser_failedFiles.setText(text)

        self.listWidget_failedFiles.clear()
        self.listWidget_failedFiles.addItems(
            [f"{i}: {e['path']}" for i, e in enumerate(files)])
        self.listWidget_failedFiles.clicked.disconnect()
        self.listWidget_failedFiles.clicked.connect(_select_failed_file)
        self.textBrowser_failedFiles.setText('')

    def refresh_with_current_protocol(self):
        """
        Refreshes the data based on the current protocol selected, including clearing variables and updating the displayed data.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        # --------------------
        # Clear necessary variables
        self.candidate_file = None
        self.chosen_files = []
        self.update_listWidget_chosenFiles()
        self.update_candidate_file()

        # --------------------
        model = CustomTableModel()
        display_columns = ['protocol', 'path', 'status', 'format']

        # --------------------
        # Path filter

        def _path_filter_text_changed(text):
            logger.debug(f'Changed pathFilter text: {text}')

            df = self.files_table.copy()
            df = df[df['protocol'] == self.protocol]
            df = df[df['path'].map(
                lambda e: text.upper() in str(e).upper())]
            self.label_filteredFiles.setText(f'{len(df): 4d}')
            self.filtered_files = [dict(se) for i, se in df.iterrows()]

            model.load_dataFrame(df, display_columns=display_columns)
            model.bind_tableView(self.tableView_validDataSelection)
            model.tableView.selectionModel().selectionChanged.disconnect()
            model.tableView.selectionModel().selectionChanged.connect(_on_select_file)
            logger.debug('Updated tableView')

        self.lineEdit_pathFilter.setText('')
        self.lineEdit_pathFilter.textChanged.disconnect()
        self.lineEdit_pathFilter.textChanged.connect(_path_filter_text_changed)

        # --------------------
        # Files table
        def _on_select_file(selected):
            se = model.on_select(selected)
            file = dict(se)
            self.update_candidate_file(file)

        df = self.files_table.copy()
        df = df[df['protocol'] == self.protocol]
        self.label_filteredFiles.setText(f'{len(df): 4d}')
        self.filtered_files = [dict(se) for i, se in df.iterrows()]

        model.load_dataFrame(df, display_columns=display_columns)
        model.bind_tableView(self.tableView_validDataSelection)
        model.tableView.selectionModel().selectionChanged.disconnect()
        model.tableView.selectionModel().selectionChanged.connect(_on_select_file)
        self.tableView_validDataSelection.setColumnWidth(1, 400)

    def update_candidate_file(self, file: dict = None):
        """
        Updates the candidate file details in the text browser.

        Args:
            file (dict): The candidate file to update.

        Returns:
            None
        """

        self.candidate_file = file
        text = ''
        if file is not None:
            text = '\n'.join(f'{k}: \t{v}' for k, v in file.items())
        self.textBrowser_candidateFileDetail.setText(text)
        logger.debug(f'Changed candidate file: {file}')

    def update_listWidget_chosenFiles(self):
        """
        Updates the list widget with the chosen files.

        ! It makes sure the same size and order between the chosen_files and listWidget_chosenFiles

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        self.chosen_files.sort(key=lambda x: x['path'])
        self.listWidget_chosenFiles.clear()
        self.listWidget_chosenFiles.addItems(
            [
                f"{i + 1}: {e['path'].as_posix()}"
                for i, e in enumerate(self.chosen_files)
            ]
        )

# %% ---- 2024-04-25 ------------------------
# Play ground


# %% ---- 2024-04-25 ------------------------
# Pending


# %% ---- 2024-04-25 ------------------------
# Pending
