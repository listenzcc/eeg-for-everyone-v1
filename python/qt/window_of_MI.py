"""
File: window_of_MI.py
Author: Chuncheng Zhang
Date: 2024-04-29
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


# %% ---- 2024-04-29 ------------------------
# Requirements and constants
import json
from PySide6.QtUiTools import QUiLoader

from .load_window import BaseWindow
from . import logger, project_root, cache_path

# --------------------
loader = QUiLoader()

# %% ---- 2024-04-29 ------------------------
# Function and class


class MIDefaultOptions:
    channels = ['C3', 'CZ', 'C4']
    eventIds = ['200', '201', '202']
    epochTimes = dict(tmin=-1.0, tmax=5.0)
    freqBand = dict(freq_l=1.0, freq_h=25.0)
    rejects = dict(eeg=1e-6)
    epochsKwargs = dict(baseline=(None, 0), decim=10)


class MIWindow(BaseWindow):
    layout_path = project_root.joinpath('layout/MI.ui')

    # --------------------
    # Known components
    # --
    listWidget_chosenFiles = None
    listWidget_analysisOptions = None

    # --
    plainTextEdit_eventIds = None
    plainTextEdit_epochTimes = None
    plainTextEdit_freqBand = None
    plainTextEdit_channels = None
    plainTextEdit_rejects = None
    plainTextEdit_epochsKwargs = None

    # --
    pushButton_useDefault = None

    # --------------------
    # variables
    protocol = 'MI'
    chosen_files = []
    option_plainTextEdits = {}
    options = {}

    def __init__(self, files: list, parent=None):
        super().__init__(loader.load(self.layout_path, parent))
        self.chosen_files = files
        self.set_options()
        self.load_default()
        self.handle_useDefault_event()
        logger.debug(f'Initialized MI window for {files}')

    def set_options(self):
        self.option_plainTextEdits = dict(
            eventIds=self.plainTextEdit_eventIds,
            epochTimes=self.plainTextEdit_epochTimes,
            freqBand=self.plainTextEdit_freqBand,
            channels=self.plainTextEdit_channels,
            rejects=self.plainTextEdit_rejects,
            epochsKwargs=self.plainTextEdit_epochsKwargs,
        )
        logger.debug(
            f'Set option plainTextEdits: {self.option_plainTextEdits}')

    def handle_useDefault_event(self):
        def on_click():
            self.load_default()

        self.pushButton_useDefault.clicked.connect(on_click)

    def load_default(self):
        # --------------------
        self.listWidget_chosenFiles.clear()
        n = len(self.chosen_files)
        self.listWidget_chosenFiles.addItems(
            [
                f"{i + 1} | {n}: {e['path'].as_posix()}"
                for i, e in enumerate(self.chosen_files)
            ]
        )
        logger.debug('Filled listWidget_chosenFiles')

        # --------------------
        default_options = MIDefaultOptions()

        def option_changed():
            for k, v in self.option_plainTextEdits.items():
                _type = type(default_options.__getattribute__(k))
                _type_name = str(_type).split('\'')[1]
                _text = v.toPlainText()

                option = None
                try:
                    cmd = f'{_type_name}({_text})'
                    option = eval(cmd)
                except Exception:
                    logger.warning(f'Failed convert to {_type}: {_text}')

                if option is None:
                    v.setStyleSheet('color:red;')
                else:
                    v.setStyleSheet('color:black;')

                self.options[k] = option

            self.listWidget_analysisOptions.clear()
            self.listWidget_analysisOptions.addItems(
                [f'{v}:\t{k}' for v, k in self.options.items()]
            )

            logger.debug(f'Changed options: {self.options}')

        for attr in [e for e in dir(default_options) if not e.startswith('_')]:
            value = default_options.__getattribute__(attr)
            self.option_plainTextEdits[attr].setPlainText(f'{value}')
            self.option_plainTextEdits[attr].textChanged.disconnect()
            self.option_plainTextEdits[attr].textChanged.connect(
                option_changed)
            logger.debug(f'Set {attr} to {value}')
        option_changed()


# %% ---- 2024-04-29 ------------------------
# Play ground


# %% ---- 2024-04-29 ------------------------
# Pending


# %% ---- 2024-04-29 ------------------------
# Pending
