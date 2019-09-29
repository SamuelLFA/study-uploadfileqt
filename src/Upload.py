from PyQt5.QtWidgets import (QWidget, QDialog, QDialogButtonBox, QFormLayout,
  QGroupBox, QLabel, QPushButton, QVBoxLayout, QFileDialog,
  QMessageBox, QListWidget, QProgressBar, QGridLayout)

from PyQt5.QtGui import (QIcon)

import sys
import requests
import json
import os

from functools import partial

# upload class
class Upload(QDialog):
  NumGridRows = 2
  NumButtons = 2

  def __init__(self, token):
    super(Upload, self).__init__()

    # set token
    self.token = token
    
    # set widgets
    self.create_list_items()
    self.create_form_group_box()
    
    # button
    button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
    button_box.rejected.connect(self.reject)
    
    # layout
    self.main_layout = QVBoxLayout()
    self.main_layout.addWidget(self.form_group_box)
    self.main_layout.addWidget(self.list_uploads)
    self.main_layout.addWidget(button_box)
    self.setLayout(self.main_layout)
    self.setWindowTitle('Files')
    self.setWindowIcon(QIcon('./src/upload.svg'))
      
  def create_form_group_box(self):

    # form
    self.form_group_box = QGroupBox('Upload')
    layout = QFormLayout()
    self.bt = QPushButton('Seach')
    self.bt.clicked.connect(self.on_click)
    layout.addRow(QLabel('Files:'), self.bt)
    self.form_group_box.setLayout(layout)

  def open_file_name_dialog(self):

    # get namefile
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filename, _ = QFileDialog.getOpenFileName(self, 'Search', '', 'All Files (*)', options=options)
    if filename:
      self.list_uploads.add(filename, True)

  def on_click(self):
    self.open_file_name_dialog()

  def upload_file(self, filename, progress_bar):

    # upload file
    if not filename:
      QMessageBox.about(self, 'Failed', 'File not found')
      return

    params = {'filename': filename}
    headers = {'Authorization': 'Bearer ' + self.token}
    data = UploadInChunks(filename, progress_bar, chunk_size=4096)
    self.r = requests.post("http://localhost:5000/upload", data=data, params=params, headers=headers)
    
  def cancel_upload(self):
    self.r.__exit__()

  def create_list_items(self):

    # list files uploaded recently by user
    self.list_uploads = ListUploads(self)
    headers = {'Authorization': 'Bearer ' + self.token} 
    r = requests.get("http://localhost:5000/getFileList", headers=headers)
    resp = json.loads(r.text)
    
    if(resp['status'] == 200):
      for filename in resp["message"]:
        self.list_uploads.add(filename, False)
    else:
      QMessageBox.about(self, 'Failed', 'File list unavailable')

class ListUploads(QWidget):

  # widget list files
  def __init__(self, parent):
    super().__init__()
    self.parent = parent
    self.size = 1
    self.grid_layout = QGridLayout()
    self.setLayout(self.grid_layout)

  def add(self, filename, availabe):
    title = QLabel(filename)
    btn_upl = QPushButton('Upload')
    btn_canc = QPushButton('Cancel')
    if not availabe:
      btn_upl.setEnabled(False)
      btn_canc.setEnabled(False)
    progress_bar = QProgressBar()
    btn_upl.clicked.connect(partial(self.parent.upload_file, filename, progress_bar))
    btn_canc.clicked.connect(self.parent.cancel_upload)
    self.grid_layout.addWidget(title, self.size, 0)
    self.grid_layout.addWidget(btn_upl, self.size, 1)
    self.grid_layout.addWidget(btn_canc, self.size, 2)
    self.grid_layout.addWidget(progress_bar, self.size, 3)
    self.size += 1

class UploadInChunks(object):

  # upload file in chunks
  def __init__(self, filename, progress_bar, chunk_size=4096):
    self.filename = filename
    self.chunk_size = chunk_size
    self.file_size = os.path.getsize(filename)
    self.current = 0
    self.progress = progress_bar

  def __iter__(self):
    with open(self.filename, 'rb') as file:
      while True:
        data = file.read(self.chunk_size)
        if not data:
          break
        self.current += len(data)
        self.progress.setValue((self.current * 100) / self.file_size)
        yield data

  def __len__(self):
    return self.file_size