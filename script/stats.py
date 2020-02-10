from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeySequence, QPalette, QColor, QIcon, QPixmap, QMovie, QColor
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
import pyqtgraph as pg

class StatWindow(QMainWindow):
    def __init__(self, parent):
        print("init options")
        super(StatWindow,self).__init__(parent)
        self.parent = parent
        self.setup()
        self.show()

    def closeEvent(self, e):
         print("exit option")

    def setup(self):
         print("setup stats")

         self.widget = QWidget(self)
         self.setCentralWidget(self.widget)

         self.main_layout = QHBoxLayout()

         self.widget.setLayout(self.main_layout)
         #Reference stack
         self.reference_stack = QTabWidget()
         self.main_layout.addWidget(self.reference_stack)
         
         #Stats
         self.stats_tab = QWidget()
         self.stats_tab_layout = QVBoxLayout()
         self.stats_tab.setLayout(self.stats_tab_layout)
         self.set_stats()
         
         #Graph
         self.graph_tab = QWidget()
         self.graph_tab_layout = QVBoxLayout()
         self.graph_tab.setLayout(self.graph_tab_layout)
         self.make_graph()
         
         self.reference_stack.addTab(self.stats_tab, "Resultat")
         self.reference_stack.addTab(self.graph_tab, "Graph")
         
         self.main_layout.addWidget(self.reference_stack)

    def set_stats(self):
        average = self.parent.get_average()
        print(self.parent.condition_stat)
        output = "number of students: {}\naverage: {}\n".format(len(self.parent.classe.etudiants),average)
        text = QLabel(output)
        self.stats_tab_layout.addWidget(text)

    def make_graph(self):
        self.graphWidget = pg.PlotWidget()
        numbers = self.get_list_numbers()
        grades =  self.get_list_grades()
        pen = pg.mkPen(color=(255, 0, 0), width=15, style=Qt.SolidLine)
        self.graphWidget.plot(numbers,grades,pen=pen,symbol="+",symbolSize=15,symbolBrush=('b'))
        self.graph_tab_layout.addWidget(self.graphWidget)

    def get_list_grades(self):
        grades = []
        for etudiant in self.parent.classe.etudiants:
            grades.append(int(etudiant.note))
        grades.sort()
        return grades

    def get_list_numbers(self):
        numbers = []
        for i in range(len(self.parent.classe.etudiants)):
            numbers.append(i+1)
        return numbers
