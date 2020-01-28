#!/usr/bin/python
import os
import glob
import pickle

def create_class(path_files,path_grille):
    students = get_students_info(path_files)
    bareme = get_grille(path_grille)
    grille = Grille(bareme,path_grille)
    classe = Classe(students,grille)
    return classe
    
def get_students_info(path):
    print("get student from {}".format(path))
    folders = [f for f in glob.glob(path + "/*")]
    students = []

    for folder in folders:
        #folder_files = [f for f in glob.glob(self.path + "/*")]
        info = os.path.basename(folder).split("_")
        student_name = info[0]
        student_code = info[1]
        etudiant = Etudiant(student_code,student_name)
        students.append(etudiant)

    return students

def get_grille(path):
    csvFile = open(path,"r")
    output = csvFile.readlines()
    bareme = []
    for i,line in enumerate(output):
        line = line.replace("\n","")
        bareme.append(line.split(","))
        bareme[i].append("0")
    return bareme

def save_classe(data, path):
    pickle.dump( data, open(path, "wb"),
                 protocol=pickle.HIGHEST_PROTOCOL)

def load_classe(path):

    classe = pickle.load( open(path, "rb"))
    
    return classe

#Objects
class Classe:
    def __init__(self,etudiants,grille):
        self.etudiants = etudiants
        self.grille = grille
        self.path = None
        
class Etudiant:
    def __init__(self,code,nom):
        self.code = code
        self.nom = nom
        self.grille = None
        self.note = None
        
class Grille:
    def __init__(self, bareme,path):
        self.bareme = bareme
        self.path = path
