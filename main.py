#!/usr/bin/env python
# -*- coding: utf-8 -*-
#bug:
from __future__ import unicode_literals
from PySide.QtCore import *
from PySide.QtGui import *
import os
import re
class FoundFile(QObject):
    found = Signal(list)
    visited = Signal(str)
    one_found = Signal(str)
    
    file_r = []
    
    def get_media_files(self):
	if self.file_r:
	    return [f for f in self.file_r if re.findall(r'[.](mp4|rmvb|avi|mkv)$', f)]
    
    def get_doc_files(self):
	if self.file_r:
	    return [f for f in self.file_r if re.findall(r'[.](pdf|doc|docx|ppt|pptx)$', f)]
	    
    def get_xls_files(self):
	if self.file_r:
	    return [f for f in self.file_r if re.findall(r'[.](xls|xlsx)$', f)]
    
    def find(self):
	self.file_r = []
	key_files = ['pdf', 'png', 'jpg', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx']
	for f in os.listdir('d:\\'):
	    if os.path.isfile('d:\\' + f) and ('.' in f) and (f.split('.')[1] in key_files):
		file_r.append('d:\\' + f)
	    if os.path.isdir('d:\\' + f):
		try:
		    r = os.listdir('d:\\' + f)
		except WindowsError:
		    continue
		for f2 in r:
		    try:
			if os.path.isfile(os.path.join('d:\\', f, f2)) and ('.' in f2) and (f2.split('.')[1] in key_files):
			    #~ print os.path.join(f, f2)
			    #~ print f2
			    file_r.append(os.path.join('d:\\', f, f2))
		    except WindowsError:
			pass
	self.found.emit(file_r)
	
    def find2(self):
	self.file_r = []
	key_files = set(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'])
	key_files = set(['avi', 'rmvb', 'mp4', 'mkv']) | key_files
	minor_name_pattern = re.compile(r'[.](pdf|doc|docx|ppt|pptx|mp4|avi|rmvb|mkv|xls|xls)$')
	for root, directories, files in os.walk(self.local_disk):
	    if ':\\Windows' in root:
		break
	    try:
		self.visited.emit(os.path.join(root, files[0]))
	    except IndexError:
		pass
	    for f in files:
		if minor_name_pattern.findall(f):
		    #~ self.one_found.emit(os.path.join(root, f))
		    self.file_r.append(os.path.join(root, f))
	self.found.emit(self.file_r)
	    
    def long_find2(self, local_disk="c:\\"):
	self.local_disk = local_disk
	self.thread = QThread()
	self.moveToThread(self.thread)
	self.found.connect(self.thread.quit)
	self.thread.started.connect(self.find2)
	self.thread.start()
		    
class MainTemplate(QWidget):
    
    def __init__(self):
	super(MainTemplate, self).__init__()
	self.setFixedSize(640, 480)
	self.setWindowTitle('Important Files Finder')
	self.put_layout()
	self.allfiles_btn = QRadioButton('All', self)
	
	self.media_btn = QRadioButton('Media', self)
	self.media_btn.setEnabled(False)
	self.doc_btn = QRadioButton('Doc', self)
	self.xls_btn = QRadioButton('Excel', self)
	self.file_filter_gp = QButtonGroup(self)
	self.file_filter_gp.addButton(self.allfiles_btn)
	self.file_filter_gp.addButton(self.media_btn)
	self.file_filter_gp.addButton(self.doc_btn)
	self.file_filter_gp.addButton(self.xls_btn)
	self.set_radio_enabled(False)
	self.search_btn = QPushButton('Search Files...', self)
	self.list_box = QListWidget(self)
	self.file_label = QLabel(self)
	self.mlo.addWidget(self.allfiles_btn)
	self.mlo.addWidget(self.media_btn)
	self.mlo.addWidget(self.doc_btn)
	self.mlo.addWidget(self.xls_btn)
	self.mlo.addWidget(self.list_box)
	self.mlo.addWidget(self.search_btn)
	self.mlo.addWidget(self.file_label)
	
	self.create_driver_radio_btns()
	
    def put_layout(self):
	self.mlo = QVBoxLayout()
	self.setLayout(self.mlo)
	
    def set_radio_enabled(self, boolean):
	for btn in self.file_filter_gp.buttons():
	    btn.setEnabled(boolean)
	    
    def create_driver_radio_btns(self):
	self.driver_gp = QButtonGroup(self)
	for disk in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
	    disk_num = disk + ":\\"
	    if os.path.isdir(disk_num):
		disk_btn = QRadioButton(disk_num, self)
		if not self.driver_gp.checkedButton():
		    disk_btn.setChecked(True)
		self.driver_gp.addButton(disk_btn)
		self.mlo.addWidget(disk_btn)
	    else:
		break   
	
class MainView(MainTemplate):
    def __init__(self):
	MainTemplate.__init__(self)
	self.search_btn.clicked.connect(self.search_files)
	self.list_box.itemDoubleClicked.connect(self.app_open)
	#~ self.media_btn.clicked.connect(self.on_media_btn)
	self.file_filter_gp.buttonClicked.connect(self.on_radio_btn)
    def change_btn_words(self):
	pass
	
    def change_widget(self):
	if self.layout.currentIndex() == 0:
	    self.layout.setCurrentIndex(1)
	else:
	    self.layout.setCurrentIndex(0)
	    self.pb.setValue(self.pb.value() - 10)
    
    def search_files(self):
	self.search_btn.setEnabled(False)
	self.list_box.clear()
	self.set_radio_enabled(False)
	self.file_model = FoundFile()
	self.file_model.visited.connect(self.file_label.setText)
	self.file_model.found.connect(self.found_files)
	self.file_model.long_find2(self.driver_gp.checkedButton().text())
	  
    def found_files(self, file_names):
	self.set_radio_enabled(True)
	self.allfiles_btn.setChecked(True)
	self.search_btn.setEnabled(True)
	self.file_label.setText('')
	self.list_box.addItems(file_names)
	  
    def app_open(self, item):
	#~ print item
	#~ print type(item.text())
	#~ print item.text()
	#~ print 'start ' + '"%s"'%item.text()
	#~ command_str = ('start ' + item.text()).encode('gbk')
	#~ print command_str
	os.startfile(item.text(), 'open')
    
    @Slot(int)
    def on_radio_btn(self, btn_sender):
	self.list_box.clear()
	if btn_sender is self.media_btn:
	    self.list_box.addItems(self.file_model.get_media_files())
	elif btn_sender is self.doc_btn:
	    self.list_box.addItems(self.file_model.get_doc_files())
	elif btn_sender is self.allfiles_btn:
	    self.list_box.addItems(self.file_model.file_r)
	elif btn_sender is self.xls_btn:
	    self.list_box.addItems(self.file_model.get_xls_files())
app = QApplication([])
app.setStyle('fusion')
mt = MainView()
mt.show()
app.exec_()

