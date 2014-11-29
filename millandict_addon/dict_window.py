# PyQt library
from aqt.qt import *
import aqt.qt as QtGui
from PyQt4 import QtCore


# windows utilities...

# main dictionary window
class DictWindow(QtGui.QWidget):

	def __init__(self):
		super(DictWindow, self).__init__()
		self.initUI()
		#self.hide()

	def initUI(self):
		# QLineEdit
		# QWebView
		search_input = QLineEdit()
		search_button = QtGui.QPushButton("SEARCH")
		search_input.returnPressed.connect(self.dictSearchEvent)
		search_button.clicked.connect(self.dictSearchEvent)

		self.search_input = search_input

		hbox_head = QtGui.QHBoxLayout()
		#hbox.addStretch(1)
		hbox_head.addWidget(search_input)
		hbox_head.addWidget(search_button)

		vbox = QtGui.QVBoxLayout()
		vbox.addLayout(hbox_head)
		vbox.addStretch(1)
		self.setLayout(vbox)
		#self.setGeometry(300, 300, 300, 150)
		self.resize(800,600)
		self.setWindowTitle('Macmillan Dictionary')
		self.show()

	def closeEvent(self, event):
		event.ignore()
		self.hide()

	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key_Escape:
			# Selecting the search input field
			print "ESC key pressed!"
			self.search_input.setFocus()
			pass

	def dictSearchEvent(self):
		# TODO - working with MacMillan wrapper
		print "dictSearchEvent() called!"
		pass

class SenseWidget(QtGui.QWidget):
    # [TODO] stworzyć widget, który będzie wyświetlany w VBoxLayout pokazujący znaczenie
    pass