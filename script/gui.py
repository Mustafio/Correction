#!/usr/bin/python
import pafy
import os.path
import random
import pickle
import os
import sys
import glob
from tkinter import Tk
import copy
import traceback

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeySequence, QPalette, QColor, QIcon, QPixmap, QMovie, QColor
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist

from gen import *

player = ""

window = None

class MyWindow(QMainWindow):

    #Initial settings-----------------------------------------------------------

    index = 0
    classe = None

    current_grades = []

    def __init__(self, parent=None):
        print("init")
        super(MyWindow, self).__init__(parent)

    def closeEvent(self, e):
         print("exit")

    def set_menu(self):
        global window
        #top menu
        mainMenu = self.menuBar()
        #Window menu
        windowmenu = mainMenu.addMenu("Window")

        #Class menu
        classmenu = mainMenu.addMenu("Classes");

        generate_class_action = QAction("&Generer",self)
        generate_class_action.triggered.connect(self.generer)

        save_class_action = QAction("&Save",self)
        save_class_action.triggered.connect(self.save)

        load_class_action = QAction("&Load",self)
        load_class_action.triggered.connect(self.load)

        classmenu.addAction(generate_class_action)
        classmenu.addAction(save_class_action)
        classmenu.addAction(load_class_action)

        self.show()

    def setup_objects_and_events(self):
        print("setup")
        self.screen_size()
        self.setMaximumHeight(self.height)
        self.setMaximumWidth(self.width)


        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.main_layout = QHBoxLayout()

        self.main_splitter = QSplitter(Qt.Horizontal)

        self.left_layout = QSplitter(Qt.Vertical)
        self.central_layout = QSplitter(Qt.Vertical)
        self.right_layout = QSplitter(Qt.Vertical)

        self.widget.setLayout(self.main_layout)

        #set the left box-------------------------------------------------------

        #Student list

        self.media_list_stack = QStackedWidget(self)
        self.media_list_stack.setMinimumWidth(200)
        self.media_list = QTableWidget(self)
        self.media_list.itemClicked.connect(self.select)
        self.media_list.itemDoubleClicked.connect(self.change_media_list)
        self.media_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.media_list.setTabKeyNavigation(True)
        self.media_list_stack.addWidget(self.media_list)
        self.media_list.setMinimumWidth(200)

        #Search bar
        self.search_box = QWidget(self)
        self.search_box_layout = QHBoxLayout()
        self.search_box.setMinimumWidth(200)
        self.search_box.setMaximumHeight(50)
        self.search_bar = QLineEdit(self)
        self.search_bar.textChanged.connect(self.search)
        self.up_search_button = QPushButton("^")
        self.up_search_button.setMaximumWidth(50)
        self.up_search_button.clicked.connect(self.navigate_search_up)
        self.down_search_button = QPushButton("v")
        self.down_search_button.setMaximumWidth(50)
        self.down_search_button.clicked.connect(self.navigate_search_down)
        self.search_box_layout.addWidget(self.search_bar)
        self.search_box_layout.addWidget(self.up_search_button)
        self.search_box_layout.addWidget(self.down_search_button)
        self.search_box.setLayout(self.search_box_layout)

        self.left_layout.addWidget(self.media_list_stack)
        self.left_layout.addWidget(self.search_box)

        #Set the center box-----------------------------------------------------

        #Title box
        self.titleFrame = QScrollArea()
        self.titleFrame.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.titleFrame.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.titleFrame.setWidgetResizable(True)
        self.title = QLabel()
        self.title.setFixedHeight(50)
        self.titleFrame.setFixedHeight(50)
        self.titleFrame.setWidget(self.title)

        # Main Correction Window
        self.main_media_stack = QStackedWidget(self)
        self.correction_window = QLabel()
        self.correction_layout = QVBoxLayout()
        self.correction_window.setLayout(self.correction_layout)
        self.main_media_stack.addWidget(self.correction_window)

        #Buttons for navigation controls
        self.bottom_buttons_box = QWidget()
        self.bottom_buttons_layout = QHBoxLayout()

        self.previous_button = QPushButton("Previous", self)
        self.previous_button.clicked.connect(self.previous)

        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.playNext)

        self.bottom_buttons_layout.addWidget(self.previous_button)
        self.bottom_buttons_layout.addWidget(self.next_button)

        self.bottom_buttons_box.setLayout(self.bottom_buttons_layout)
        self.bottom_buttons_box.setFixedHeight(50)

        #Add everything in the central window
        self.central_layout.addWidget(self.titleFrame)
        self.central_layout.addWidget(self.main_media_stack)
        self.central_layout.addWidget(self.bottom_buttons_box)

        #Set the right box------------------------------------------------------

        # Set the vote buttons for the owners
        self.table_widget_right = QTabWidget()

        self.vote_tab = QWidget()
        self.stats_tab = QWidget()
        self.color_tab = QWidget()

        self.table_widget_right.addTab(self.vote_tab,"Votes")
        self.table_widget_right.addTab(self.stats_tab,"Stats")

        self.vote_layout = QVBoxLayout()
        self.stats_layout = QVBoxLayout()
        self.color_layout = QVBoxLayout()

        verticalSpacer = QSpacerItem(200, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.stats_tab.setMinimumWidth(200)
        self.stats_tab.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.vote_tab.setLayout(self.vote_layout)
        self.stats_tab.setLayout(self.stats_layout)
        self.color_tab.setLayout(self.color_layout)

        #Put everything in the main window

        self.main_splitter.addWidget(self.left_layout)
        self.main_splitter.addWidget(self.central_layout)
        self.main_splitter.addWidget(self.right_layout)

        self.main_splitter.setStretchFactor(1,3)

        self.main_layout.addWidget(self.main_splitter)

        self.set_keyboard_shortcut()
        #self.setLayout(self.main_layout)
        self.showMaximized()
        self.setFocus()

    def set_keyboard_shortcut(self):
        #Pause
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.save_current)

    def playNext(self, widget):
        print("next")
        self.input_votes()
        self.index += 1
        self.playMedia()

    def previous(self,widget):
        print("previous")
        self.input_votes()
        if (self.index != 0):
            self.index -= 1
        self.playMedia()

    def file_path(self, pathName=None):
        dirname=os.path.dirname
        if pathName == None:
            pathName = ""
        path = os.path.join(dirname(dirname(__file__)),
                        os.path.join(pathName))
        return path

    def screen_size(self):
        root = Tk()
        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()

    def save_current(self, widget=None):
        path = QFileDialog.getSaveFileName(self, "Open File",self.file_path())[0]
        if path:
            self.input_votes()
            self.current_file = path
            self.save_current_playlist()

    #Settings-------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_D or event.key() == Qt.Key_Right:
            self.playNext(None)
        elif event.key() == Qt.Key_A or event.key() == Qt.Key_Left:
            self.previous(None)
        elif event.key() == Qt.Key_Up:
            self.change_volume_manual(10)
        elif event.key() == Qt.Key_Down:
            self.change_volume_manual(-10)
        elif event.key() == 16777220:
            self.change_focus(None)
    #List-----------------------------------------------------------------------
    def set_student_list(self):
        if self.classe != None:
            self.media_list.setRowCount(len(self.get_etudiants()))
            self.media_list.setColumnCount(1)
            self.media_list.horizontalHeader().setDefaultSectionSize(155)

            for i, etudiant in enumerate(self.get_etudiants()):
                self.media_list.setItem(i,0,QTableWidgetItem(etudiant.nom))
                if etudiant.condition == 0:
                    color = "green"
                elif etudiant.condition == 2:
                    color = "red"
                self.media_list.item(i,0).setBackground(QColor(color))
                
    #Correction window----------------------------------------------------------
    def generate_correction(self,student):
        if self.current_grades != []:
            for i,grade in enumerate(self.current_grades):
                for j,info in enumerate(self.current_grades[i]):
                    self.correction_layout.removeWidget(info)
                    self.correction_layout.removeWidget(info)
                    info.deleteLater()
                    info = None
        self.current_grades = []
        for i, notation in enumerate(self.get_grille().bareme):
            self.current_grades.append([])
            bloc = QLabel()
            bloc_layout = QHBoxLayout()
            bloc.setLayout(bloc_layout)

            self.set_spinner(int(notation[0]),notation[1],bloc_layout,i)
            description = QLabel(notation[1])
            self.current_grades[i].append(description)
            bloc_layout.addWidget(description)
            self.correction_layout.addWidget(bloc)

    def set_spinner(self,value,name,layout,i):
        self.timer_spinner = QSpinBox()
        self.timer_spinner.setSingleStep(1)
        self.timer_spinner.setMaximum(value);
        self.timer_spinner.setValue(value);
        self.current_grades[i].append(self.timer_spinner)
        layout.addWidget(self.timer_spinner)


    #Menu actions---------------------------------------------------------------

    def generer(self, widget):
        folder_student = QFileDialog.getExistingDirectory(self, "Selectionner Dossier travaux")
        file_grille    = QFileDialog.getOpenFileName(self, "Selectionner Fichier grille")[0]
        path_corrector    = QFileDialog.getOpenFileName(self, "Selectionner Fichier correcteur")[0]
        if folder_student != "" and file_grille != "" and path_corrector != "":
            self.classe = create_class(folder_student,file_grille,path_corrector)
            self.set_student_list()

    def load(self, widget):
        path = QFileDialog.getOpenFileName(self, "Selectionner la fichier")[0]
        if path != "":
            self.classe = load_classe(path)
            self.set_student_list()

    def save(self, widget):
        path = QFileDialog.getSaveFileName(self, "Selectionner le fichier")[0]
        if path != "":
            save_classe(self.classe, path)
            self.set_student_list()

    def select(self, row):
        index = row.row()
        print(self.get_etudiants()[index].nom)
        self.generate_correction(self.get_etudiants()[index])

    def change_media_list(self, row):
        print("going to: " + str(row.row()))
        self.index = row.row()

    def search(self, widget):
        media = self.media_list.findItems(self.search_bar.text(),Qt.MatchContains)
        #self.media_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.media_list.clearSelection()
        if len(media) <= 50 and len(media) > 0:
            self.search_list = media
            self.search_current = 0
            for row in media:
                self.media_list.selectRow(row.row())
        else:
            self.seach_list = None
            self.search_current = 0

    def navigate_search_up(self,widget):
        self.navigate_search("up")

    def navigate_search_down(self,widget):
        self.navigate_search("down")
    #Reference------------------------------------------------------------------
    def get_etudiants(self):
        if self.classe != None:
            return self.classe.etudiants
    def get_grille(self):
        if self.classe != None:
            return self.classe.grille
        
    def set_title(self, text):
         self.title.setText(text)

def get_window():
    return window

def mainReader():
    global window
    global parent_dir
    #to display error messages
    sys._excepthook = sys.excepthook
    def exception_hook(exctype, value, traceback):
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = exception_hook

    app = QApplication([])
    app.setApplicationName("Correction")

    window = MyWindow()

    window.set_menu()
    window.setup_objects_and_events()
    app.exec_()

mainReader()
