#!/usr/bin/env python
# -*- coding: utf-8 -*-
#bug: Repeated File
#feature: QListViewModel-> WholeModel PartView, Successful Tip, Debug Sys
#study: Command Pattern. ThreadWorker Pattern
from __future__ import unicode_literals
from PySide.QtCore import *
from PySide.QtGui import *
import os
import re
import shutil
import time

class ThreadFileMover(QThread):
    one_moved = Signal(int)
    one_failed = Signal(object)
    
    MOVE = 0
    COPY = 1
    def __init__(self, items, action):
	QThread.__init__(self)
	self.items = items
	self.des = os.path.normpath(FoundFile.find_onedrive())
	self.action = action
    def run(self):
	for item in self.items:
	    try:
		if self.action == self.MOVE:
		    shutil.move(item, self.des)
		elif self.action == self.COPY:
		    if os.path.exists(os.path.join(self.des, os.path.basename(item))):
			raise shutil.Error(os.path.join(self.des, os.path.basename(item)) + ' already exists')
		    shutil.copy(item, self.des)
		self.one_moved.emit(self.action)
	    except shutil.Error as e:
		self.one_failed.emit(e)
		
class FoundFile(QObject):
    found = Signal(list)
    visited = Signal(str)
    one_found = Signal(str)
    
    file_r = []
    
    def get_media_files(self):
	if self.file_r:
	    return [f for f in self.file_r if re.findall(r'[.](mp4|rmvb|avi|mkv|wmv|wma|mp3)$', f)]
    
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
	minor_name_pattern = re.compile(r'[.](pdf|doc|docx|ppt|pptx|mp4|avi|rmvb|mkv|wmv|mp3|wma|xls|xls)$')
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
	#~ self.thread = QThread()
	#~ self.moveToThread(self.thread)
	#~ self.found.connect(self.thread.quit)
	#~ self.thread.started.connect(self.find2)
	#~ self.thread.start()
	
    @staticmethod
    def find_onedrive():
	if TESTING:
	    return "D:\\"
	if os.path.isdir(os.path.expanduser("~\\SkyDrive")):
	    return os.path.expanduser("~\\SkyDrive")
	elif os.path.isdir(os.path.expanduser("~\\OneDrive")):
	    return os.path.expanduser("~\\OneDrive")
		    
class MainTemplate(QWidget):
    
    def __init__(self):
	super(MainTemplate, self).__init__()
	self.setFixedSize(800, 600)
	self.setWindowTitle('File Dustman')
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
	self.search_btn = QPushButton('   Search Files...   ', self)
	self.list_box = QListWidget(self)
	#~ self.list_box.setSelectionMode(QAbstractItemView.ExtendedSelection)
	self.file_label = QLabel(self)
	
	self.dropboxfolder_btn = QPushButton(self)
	self.dropboxfolder_btn.setEnabled(False)
	
	self.cloudfolder_copy_btn = QPushButton(self)
	self.cloudfolder_copy_btn.setEnabled(False)
	self.file_operation_gp = QButtonGroup()
	self.search_toolbar = QToolBar(self)
	self.toolbar = QToolBar(self)
	
	self.create_driver_radio_btns()
	
	self.toolbar.addWidget(self.allfiles_btn)
	self.toolbar.addWidget(self.media_btn)
	self.toolbar.addWidget(self.doc_btn)
	self.toolbar.addWidget(self.xls_btn)
	self.toolbar.addSeparator()

	self.mlo.addWidget(self.search_toolbar)
	self.mlo.addWidget(self.toolbar)
	#~ self.mlo.addWidget(self.allfiles_btn)
	#~ self.mlo.addWidget(self.media_btn)
	#~ self.mlo.addWidget(self.doc_btn)
	#~ self.mlo.addWidget(self.xls_btn)
	self.mlo.addWidget(self.list_box)
	self.mlo.addWidget(self.file_label)
	self.toolbar.addWidget(self.dropboxfolder_btn)
	self.toolbar.addWidget(self.cloudfolder_copy_btn)
	
	
	
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
		self.search_toolbar.addWidget(disk_btn)
	    else:
		break
	self.search_toolbar.addSeparator()
	self.search_toolbar.addWidget(self.search_btn)
class MainView(MainTemplate):
    def __init__(self):
	MainTemplate.__init__(self)
	self.search_btn.clicked.connect(self.search_files)
	self.list_box.itemDoubleClicked.connect(self.app_open)
	#~ self.media_btn.clicked.connect(self.on_media_btn)
	self.file_operation_gp.addButton(self.dropboxfolder_btn, ThreadFileMover.MOVE)
	self.file_operation_gp.addButton(self.cloudfolder_copy_btn, ThreadFileMover.COPY)
	self.file_operation_gp.buttonClicked.connect(self.move_to_box)
	
	self.file_filter_gp.buttonClicked.connect(self.on_radio_btn)
	self.file_model = FoundFile()
	self.file_model.visited.connect(self.file_label.setText)
	self.file_model.found.connect(self.found_files)
	self.dropboxfolder_btn.setText('Move to ' + self.file_model.find_onedrive())
	self.cloudfolder_copy_btn.setText('Copy to ' + self.file_model.find_onedrive())
	
	self.list_box.itemClicked.connect(self.item_clicked)
	self.thread = QThread()
	self.file_model.moveToThread(self.thread)
	self.file_model.found.connect(self.thread.quit)
	self.thread.started.connect(self.file_model.find2)
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
	self.dropboxfolder_btn.setEnabled(False)
	self.cloudfolder_copy_btn.setEnabled(False)
	if TESTING:
	    self.file_model.long_find2("d:\\testpath pa")
	else:
	    self.file_model.long_find2(self.driver_gp.checkedButton().text())
	
	self.thread.start()
	
    def item_clicked(self):
	self.dropboxfolder_btn.setEnabled(True)
	self.cloudfolder_copy_btn.setEnabled(True)
	
    def found_files(self, file_names):
	self.set_radio_enabled(True)
	self.allfiles_btn.setChecked(True)
	self.search_btn.setEnabled(True)
	self.file_label.setText('Total: %d'%len(self.file_model.file_r))
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
	    filtered_files = self.file_model.get_media_files()
	elif btn_sender is self.doc_btn:
	    filtered_files = self.file_model.get_doc_files()
	elif btn_sender is self.allfiles_btn:
	    filtered_files = self.file_model.file_r
	elif btn_sender is self.xls_btn:
	    filtered_files = self.file_model.get_xls_files()
	self.list_box.addItems(filtered_files)
	self.file_label.setText('Total: %d'%len(filtered_files))
	
    def move_to_box(self, btn_sender):
	self.list_box.setEnabled(False)
	self.dropboxfolder_btn.setEnabled(False)
	self.cloudfolder_copy_btn.setEnabled(False)
	btn_sender.setText('Processing >>>')
	self.last_clicked_btn_id = self.file_operation_gp.id(btn_sender)
	self.search_btn.setEnabled(False)
	self.selected_items = self.list_box.selectedItems()
	self.tfile_mover = ThreadFileMover([item.text() for item in self.selected_items], self.file_operation_gp.id(btn_sender))
	self.tfile_mover.finished.connect(self.after_files_moved)
	self.tfile_mover.one_moved.connect(self.after_single_file_moved)
	self.tfile_mover.one_failed.connect(self.single_file_move_failed)
	self.tfile_mover.start()
	
    @Slot(int)
    def after_single_file_moved(self, action_id):
	item = self.selected_items.pop()
	if action_id == ThreadFileMover.MOVE:
	    self.list_box.takeItem(self.list_box.row(item))
	    self.file_model.file_r.remove(item.text())
	elif action_id == ThreadFileMover.COPY:
	    item.setForeground(QBrush(QColor(255, 0, 0)))
	self.file_label.setText('Total: %d'%self.list_box.count())
    
    def after_files_moved(self):
	self.list_box.setEnabled(True)
	self.dropboxfolder_btn.setEnabled(True)
	self.dropboxfolder_btn.setText('Move to ' + self.file_model.find_onedrive())
	self.cloudfolder_copy_btn.setEnabled(True)
	self.cloudfolder_copy_btn.setText('Copy to ' + self.file_model.find_onedrive())
	self.search_btn.setEnabled(True)
	
    def single_file_move_failed(self, err):
	msgbox = QMessageBox(self)
	msgbox.setText(err.message)
	msgbox.exec_()

TESTING = False
app = QApplication([])
app.setStyle('fusion')
mt = MainView()
mt.show()
app.exec_()

