from PyQt5.QtWidgets import (QApplication, QDialog, QDialogButtonBox,
  QFormLayout, QGroupBox, QLabel, QLineEdit, QMenu, QVBoxLayout,
  QSystemTrayIcon, QAction, QMessageBox)
from PyQt5.QtGui import (QIcon, QRegExpValidator)
from PyQt5.QtCore import (QRegExp)

import sys
import requests
import json
import re

from Upload import Upload

class Dialog(QDialog):

  def __init__(self):

    super(Dialog, self).__init__()
    self.create_form_group_box()
    
    # create button box
    button_box = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.button(QDialogButtonBox.Ok).setText(self.tr("Sign in"))
    button_box.button(QDialogButtonBox.Apply).setText(self.tr("Sign up"))
    button_box.button(QDialogButtonBox.Ok).clicked.connect(self.login)
    button_box.button(QDialogButtonBox.Apply).clicked.connect(self.register)
    button_box.rejected.connect(self.reject)
    
    # set layout
    main_layout = QVBoxLayout()
    main_layout.addWidget(self.form_group_box)
    main_layout.addWidget(button_box)
    self.setLayout(main_layout)
    
    # window options
    self.setWindowTitle("Upload")
    self.setWindowIcon(QIcon('./src/upload.svg'))
      
  def create_form_group_box(self):

    # set user inputs layout
    self.form_group_box = QGroupBox('User')
    layout = QFormLayout()

    # email input
    self.le_email = QLineEdit()
    reg_ex = QRegExp(r"[a-zA-Z0-9]+@[a-zA-Z0-9\.]+")
    email_validator = QRegExpValidator(reg_ex, self.le_email)
    self.le_email.setValidator(email_validator)
    
    # password input
    self.le_pw = QLineEdit()
    self.le_pw.setEchoMode(QLineEdit.Password)

    # add inputs in layout
    layout.addRow(QLabel("Email:"), self.le_email)
    layout.addRow(QLabel("Password:"), self.le_pw)
    self.form_group_box.setLayout(layout)

  def login(self):

    # get inputs text
    email = self.le_email.text()
    pw = self.le_pw.text()

    # verify email or password input empty
    if not email or not pw:
      QMessageBox.about(self, 'Fail', 'Email or password invalid')
      return

    # request
    payload = {'email': email, 'password': pw}
    headers = {'content-type': 'application/json'}
    r = requests.post("http://localhost:5000/login", data=json.dumps(payload), headers=headers)

    # response
    resp = json.loads(r.text)
    if resp["status"] == 200:
      self.token = resp['message']
      upload = Upload(self.token)
      upload.exec_()
    else:
      QMessageBox.about(self, 'Fail', 'Email or password invalid')

  def register(self):

    # get inputs text
    email = self.le_email.text()
    pw = self.le_pw.text()

    # validate email or password input empty
    if not email or not pw:
      QMessageBox.about(self, 'Fail', 'Email or password invalid')
      return

    # request
    payload = {'email': email, 'password': pw}
    headers = {'content-type': 'application/json'}
    r = requests.post("http://localhost:5000/register", data=json.dumps(payload), headers=headers)

    # response
    resp = json.loads(r.text)
    if resp['status'] == 200:
      QMessageBox.about(self, 'Success', 'User registered')
      self.token = resp['message']
      upload = Upload(self.token)
      upload.exec_()
    else:
      QMessageBox.about(self, 'Fail', 'Email or password invalid')

if __name__ == '__main__':

  # start app
  app = QApplication(sys.argv)
  app.setQuitOnLastWindowClosed(False)

  # create tray icon
  trayIcon = QSystemTrayIcon(QIcon('./src/upload.svg'), app)
  trayIcon.show()

  # new menu
  menu = QMenu()
  action = QAction("A menu item")
  menu.addAction(action)

  # exec
  window = Dialog()
  trayIcon.setContextMenu(menu)
  window.exec_()