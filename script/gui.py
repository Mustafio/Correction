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
    loaded = False

    current_grades = []
    search_list = []

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

        #Classe menu
        classmenu = mainMenu.addMenu("Classe");

        generate_class_action = QAction("&Generer",self)
        generate_class_action.triggered.connect(self.generer)

        save_class_action = QAction("&Save",self)
        save_class_action.triggered.connect(self.save)

        load_class_action = QAction("&Load",self)
        load_class_action.triggered.connect(self.load)

        classmenu.addAction(generate_class_action)
        classmenu.addAction(save_class_action)
        classmenu.addAction(load_class_action)

         #Student menu
        studentmenu = mainMenu.addMenu("Etudiants")

        sort_sub_menu = studentmenu.addMenu("Sort")
        sort_alph_menu = QAction("&Alphabetique",self)
        sort_alph_menu.triggered.connect(self.sort_alph)
        sort_grade_menu = QAction("&Note",self)
        sort_grade_menu.triggered.connect(self.sort_grade)
        sort_shuffle_menu = QAction("&Shuffle",self)
        sort_shuffle_menu.triggered.connect(self.sort_shuffle)

        sort_sub_menu.addAction(sort_alph_menu)
        sort_sub_menu.addAction(sort_grade_menu)
        sort_sub_menu.addAction(sort_shuffle_menu)

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
        #Main correction window
        self.main_correction_window = QSplitter(Qt.Horizontal)
        #self.main_correction_window_layout = QHBoxLayout()
        #self.main_correction_window.setLayout(self.main_correction_window_layout)

        #Grille Window
        self.correction_window = QWidget()
        self.correction_window.setMinimumWidth(150)
        self.correction_layout = QVBoxLayout()
        self.correction_layout.setSpacing(0)
        self.correction_layout.setContentsMargins(0,0,0,0)
        self.correction_window.setLayout(self.correction_layout)

        #Reference stack
        self.reference_stack = QTabWidget()
        
        #Result
        self.result_tab = QWidget()
        self.result_tab_layout = QVBoxLayout()
        self.result_tab.setLayout(self.result_tab_layout)

        self.result_zone = QPlainTextEdit()
        self.result_zone.setReadOnly(True)
        #button
        self.result_button = QPushButton("Open Original")
        self.result_button.clicked.connect(self.open_result)
        
        self.result_tab_layout.addWidget(self.result_zone)
        self.result_tab_layout.addWidget(self.result_button)
        #Code
        self.code_tab = QWidget()
        self.code_tab_layout = QVBoxLayout()
        self.code_tab.setLayout(self.code_tab_layout)

        self.code_zone = QPlainTextEdit()
        self.code_zone.setReadOnly(True)
        #button
        self.code_button = QPushButton("Open Original")
        self.code_button.clicked.connect(self.open_code)
        self.result_tab_layout.addWidget(self.result_zone)
        self.result_tab_layout.addWidget(self.result_button)
        
        self.code_tab_layout.addWidget(self.code_zone)
        self.code_tab_layout.addWidget(self.code_button)
        
        self.reference_stack.addTab(self.result_tab, "Resultat")
        self.reference_stack.addTab(self.code_tab, "Code")

        self.main_correction_window.addWidget(self.correction_window)
        self.main_correction_window.addWidget(self.reference_stack)

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
        self.central_layout.addWidget(self.main_correction_window)
        self.central_layout.addWidget(self.bottom_buttons_box)

        #Put everything in the main window

        self.main_splitter.addWidget(self.left_layout)
        self.main_splitter.addWidget(self.central_layout)

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
        #self.index += 1

    def previous(self,widget):
        print("previous")
        #if (self.index != 0):
            #self.index -= 1

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
        path = QFileDialog.getSaveFileName(self, "Open File")[0]
        if path:
            save_classe(self.classe,path)

    #Settings-------------------------------------------------------------------
    #def keyPressEvent(self, event):
       # if event.key() == Qt.Key_D or event.key() == Qt.Key_Right:
       #     self.playNext(None)
       # elif event.key() == Qt.Key_A or event.key() == Qt.Key_Left:
       #     self.previous(None)
    
    #List-----------------------------------------------------------------------
    def set_student_list(self):
        if self.classe != None:
            check_if_graded(self.classe)

            self.media_list.setRowCount(len(self.get_etudiants()))
            self.media_list.setColumnCount(2)
            self.media_list.horizontalHeader().setDefaultSectionSize(100)

            for i, etudiant in enumerate(self.get_etudiants()):
                self.media_list.setItem(i,0,QTableWidgetItem(etudiant.nom))
                if etudiant.note != None:
                     self.media_list.setItem(i,1,QTableWidgetItem(etudiant.note))
                     self.media_list.item(i,1).setBackground(QColor("green"))
                else:
                    self.media_list.setItem(i,1,QTableWidgetItem("NaN"))
                    self.media_list.item(i,1).setBackground(QColor("red"))
                if etudiant.condition == 0:
                    color = "green"
                elif etudiant.condition == 1:
                    color = "yellow"
                elif etudiant.condition == 2:
                    color = "red"
                elif etudiant.condition == 3:
                    if etudiant.note == None:
                        etudiant.note = int(get_grade_from_grille(etudiant))
                    color = "green"
                    
                self.media_list.item(i,0).setBackground(QColor(color))

                if etudiant.note != None:
                     self.media_list.item(i,1).setBackground(QColor("green"))
                     self.media_list.item(i,1).setText(str(etudiant.note))

    #Sorting--------------------------------------------------------------------
    def sort_alph(self,widget):
        if self.classe != None:
            self.classe.etudiants.sort(key=lambda x: x.nom,reverse=False)
            self.set_student_list()

    def sort_grade(self, widget):
        if self.classe != None:
            self.classe.etudiants.sort(key=lambda x: x.note,reverse=False)
            self.set_student_list()

    def sort_shuffle(self, widget):
        if self.classe != None:
            random.shuffle(self.classe.etudiants)
            self.set_student_list()
            
    #Correction window----------------------------------------------------------
    def generate_correction(self,student):
        print(student.nom)
        if self.current_grades != []:
            for i,grade in enumerate(self.current_grades):
                for j,info in enumerate(self.current_grades[i]):
                    self.correction_layout.removeWidget(info)
                    info.deleteLater()
                    info = None
        self.current_grades = []
        for i, notation in enumerate(student.grille.bareme):
            self.current_grades.append([])
            bloc = QLabel()
            bloc_layout = QHBoxLayout()
            bloc.setLayout(bloc_layout)

            self.set_spinner(int(notation[0]),notation[1],notation[2],bloc_layout,i)
            description = QLabel("/{} : {}".format(notation[0],notation[1]))
            self.current_grades[i].append(description)
            bloc_layout.addWidget(description)
            self.correction_layout.addWidget(bloc)
            self.current_grades[i].append(bloc)

        #spacer = QSpacerItem(0,10,QSizePolicy.Expanding,QSizePolicy.Minimum)
        #self.correction_layout.addItem(spacer)
        #Comment zone
        self.comment_zone = QPlainTextEdit(self)
        self.comment_zone.setMaximumHeight(100)
        self.comment_zone.setPlainText(student.grille.commentaires)
        self.correction_layout.addWidget(self.comment_zone)
        self.current_grades.append([self.comment_zone])
        
        #Button
        self.done_button = QPushButton("Terminer")
        self.done_button.setMaximumWidth(100)
        self.done_button.clicked.connect(self.done)
        self.correction_layout.addWidget(self.done_button)
        self.current_grades.append([self.done_button])
        
        #Set Result zone
        self.result_zone.setPlainText(get_result_text(student))
        #Set Code zone
        self.code_zone.setPlainText(get_code_text(student))
        
    def set_spinner(self,value,name,initial,layout,i):
        self.timer_spinner = QSpinBox()
        self.timer_spinner.setFixedWidth(50)
        self.timer_spinner.setSingleStep(1)

        if value >= 0:
            if initial == None:
                initial = value
            self.timer_spinner.setMaximum(value)
        else:
            if initial == None:
                initial = 0
            self.timer_spinner.setMaximum(0)
            self.timer_spinner.setMinimum(value)
        self.timer_spinner.setValue(int(initial))
            
        self.current_grades[i].append(self.timer_spinner)
        layout.addWidget(self.timer_spinner,0,Qt.AlignTop)

    def done(self,widget):
        student = self.get_current_student()
        print(student.nom)
        note = 0
        for i,spinner in enumerate(self.current_grades):
            if i == len(self.current_grades) - 1:
                break
            elif i == len(self.current_grades) - 2:
                student.grille.commentaires = spinner[0].toPlainText()
                continue
            student.grille.bareme[i][2] = int(spinner[0].value())
            note += int(spinner[0].value())
        student.note = note
        #udpade student grade in list
        self.media_list.item(self.index,1).setBackground(QColor("green"))
        self.media_list.item(self.index,1).setText(str(note))

        #output grille in student folder
        output_student_grille(student)
        student.condition = 3
        print(student.note)

    def open_code(self,student):
        if self.loaded:
            open_code_file(self.get_current_student())

    def open_result(self,student):
        if self.loaded:
            open_result_file(self.get_current_student())
    #Menu actions---------------------------------------------------------------

    def generer(self, widget):
        folder_student = QFileDialog.getExistingDirectory(self, "Selectionner Dossier travaux")
        file_grille    = QFileDialog.getOpenFileName(self, "Selectionner Fichier grille")[0]
        path_corrector    = QFileDialog.getOpenFileName(self, "Selectionner Fichier correcteur")[0]
        if folder_student != "" and file_grille != "" and path_corrector != "":
            self.classe = create_class(folder_student,file_grille,path_corrector)
            self.set_student_list()

    def load(self, widget):
        path = QFileDialog.getOpenFileName(self, "Selectionner le fichier")[0]
        if path != "":
            self.classe = load_classe(path)
            self.loaded = True
            self.set_student_list()
            print(get_average(self.classe))

    def save(self, widget):
        path = QFileDialog.getSaveFileName(self, "Selectionner le fichier")[0]
        if path != "":
            save_classe(self.classe, path)
            self.set_student_list()

    def select(self, row):
        self.index = row.row()
        self.set_title(self.get_etudiants()[self.index].nom)
        self.generate_correction(self.get_etudiants()[self.index])

    def change_media_list(self, row):
        print("going to: " + str(row.row()))
        self.index = row.row()
    #Search bar-----------------------------------------------------------------
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

    def navigate_search(self,direction):
        if self.search_list != None and len(self.search_list) > 0:
            if direction == "up":
                if self.search_current == 0:
                    self.search_current = len(self.search_list) - 1
                else:
                    self.search_current -= 1
            else:
                if self.search_current == len(self.search_list) - 1:
                    self.search_current = 0
                else:
                    self.search_current += 1
                
            self.media_list.clearSelection()
            self.media_list.selectRow(self.search_list[self.search_current].row())
    
    #Reference------------------------------------------------------------------
    def get_etudiants(self):
        if self.classe != None:
            return self.classe.etudiants
    def get_grille(self):
        if self.classe != None:
            return self.classe.grille
        
    def set_title(self, text):
         self.title.setText(text)

    def get_current_student(self):
        return self.get_etudiants()[self.index]

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
