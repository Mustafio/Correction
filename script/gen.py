#!/usr/bin/python
import os
import glob
import pickle
import subprocess
from threading import Timer

def create_class(path_files,path_grille,path_correcteur):
    students = get_students_info(path_files,path_correcteur)
    bareme = get_grille(path_grille)
    grille = Grille(bareme,path_grille)
    classe = Classe(students,grille)
    return classe
    
def get_students_info(path,path_correcteur):
    print("get student from {}".format(path))
    #get all student folders paths
    folders = [f for f in glob.glob(path + "/*")]
    students = []

    stop = False
    #t = Timer(5,stop)
    #t.start()
    for folder in folders:
        #remove spaces from folders
        new_folder = folder.replace(" ","")
        if( folder != new_folder):
            os.rename(folder,new_folder)
        #get student info
        info = os.path.basename(new_folder).split("_")
        student_name = info[0]
        student_code = info[1]

        condition = 0
        try:
            #get all student files
            files = [f for f in glob.glob(new_folder + "/*.js")]
            if len(files) == 0:
                files = None
            elif len(files) == 1:
                print("nom: {}".format(student_name))
                #Remove spaces from student files
                new_file = files[0].replace(" ","").replace("(","").replace(")","")
                if( files[0] != new_file):
                    os.rename(files[0],new_file)
                #print("{} {} {} {}".format(path_correcteur,files[0],'>',new_folder + '/correction.txt'))
                os.system("{} {} {} {}".format(path_correcteur,new_file,'>',new_folder + '/resultat.txt'))
               # if stop:
               #     stop = False
               #     continue
                #subprocess.run([path_correcteur, files[0],'>', new_folder + '/correction.txt'])
        except:
            condition = 2

        etudiant = Etudiant(student_code,student_name, condition)
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
    def __init__(self,code,nom, condition):
        self.code = code
        self.nom = nom
        self.condition = condition
        
        self.correction = None
        self.fichier = None
        self.grille = None
        self.note = None
        
class Grille:
    def __init__(self, bareme,path):
        self.bareme = bareme
        self.path = path
