# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ecofoci_processing_design.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(459, 765)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.layoutWidget = QtGui.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(80, 460, 193, 141))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout_lower = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout_lower.setObjectName(_fromUtf8("gridLayout_lower"))
        self.btlSummaryButton = QtGui.QPushButton(self.layoutWidget)
        self.btlSummaryButton.setObjectName(_fromUtf8("btlSummaryButton"))
        self.gridLayout_lower.addWidget(self.btlSummaryButton, 4, 0, 1, 1)
        self.exitButton = QtGui.QPushButton(self.layoutWidget)
        self.exitButton.setObjectName(_fromUtf8("exitButton"))
        self.gridLayout_lower.addWidget(self.exitButton, 5, 0, 1, 1)
        self.processButton = QtGui.QPushButton(self.layoutWidget)
        self.processButton.setObjectName(_fromUtf8("processButton"))
        self.gridLayout_lower.addWidget(self.processButton, 1, 0, 1, 1)
        self.addMetaButton = QtGui.QPushButton(self.layoutWidget)
        self.addMetaButton.setObjectName(_fromUtf8("addMetaButton"))
        self.gridLayout_lower.addWidget(self.addMetaButton, 3, 0, 1, 1)
        self.layoutWidget1 = QtGui.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(120, 10, 268, 433))
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.inputButton = QtGui.QPushButton(self.layoutWidget1)
        self.inputButton.setObjectName(_fromUtf8("inputButton"))
        self.verticalLayout.addWidget(self.inputButton)
        self.label_2 = QtGui.QLabel(self.layoutWidget1)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.inputList = QtGui.QListWidget(self.layoutWidget1)
        self.inputList.setObjectName(_fromUtf8("inputList"))
        self.verticalLayout.addWidget(self.inputList)
        self.label = QtGui.QLabel(self.layoutWidget1)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.outputList = QtGui.QListWidget(self.layoutWidget1)
        self.outputList.setObjectName(_fromUtf8("outputList"))
        self.verticalLayout.addWidget(self.outputList)
        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(300, 460, 111, 97))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_2.addWidget(self.label_3)
        self.presscomboBox = QtGui.QComboBox(self.widget)
        self.presscomboBox.setObjectName(_fromUtf8("presscomboBox"))
        self.presscomboBox.addItem(_fromUtf8(""))
        self.presscomboBox.addItem(_fromUtf8(""))
        self.presscomboBox.addItem(_fromUtf8(""))
        self.presscomboBox.addItem(_fromUtf8(""))
        self.verticalLayout_2.addWidget(self.presscomboBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.verticalLayout_2.addItem(spacerItem)
        self.IPHCcheckBox = QtGui.QCheckBox(self.widget)
        self.IPHCcheckBox.setObjectName(_fromUtf8("IPHCcheckBox"))
        self.verticalLayout_2.addWidget(self.IPHCcheckBox)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.btlSummaryButton.setText(_translate("MainWindow", "Generate Bottle Summary", None))
        self.exitButton.setText(_translate("MainWindow", "Exit", None))
        self.processButton.setText(_translate("MainWindow", "Process Files", None))
        self.addMetaButton.setText(_translate("MainWindow", "Add Cruise Meta Data", None))
        self.inputButton.setText(_translate("MainWindow", "Select Cruise Directory", None))
        self.label_2.setText(_translate("MainWindow", "Choose Input Directory", None))
        self.label.setText(_translate("MainWindow", "Choose Output Directory", None))
        self.label_3.setText(_translate("MainWindow", ".cnv press label", None))
        self.presscomboBox.setItemText(0, _translate("MainWindow", "prDM", None))
        self.presscomboBox.setItemText(1, _translate("MainWindow", "prdM", None))
        self.presscomboBox.setItemText(2, _translate("MainWindow", "prdm", None))
        self.presscomboBox.setItemText(3, _translate("MainWindow", "prSM", None))
        self.IPHCcheckBox.setText(_translate("MainWindow", "is IPHC", None))

