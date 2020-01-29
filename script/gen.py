#!/usr/bin/python
import os
import glob
import pickle
import subprocess
from threading import Timer
import copy

def create_class(path_files,path_grille,path_correcteur):
    bareme = get_grille(path_grille)
    grille = Grille(bareme,path_grille)
    students = get_students_info(path_files,grille,path_correcteur)
    classe = Classe(students,grille, path_files)
    return classe
    
def get_students_info(path,main_grille, path_correcteur):
    print("get student from {}".format(path))
    #get all student folders paths
    folders = [f for f in glob.glob(path + "/*")]
    students = []
    #stop = False
    #t = Timer(5,stop)
    #t.start()
    for folder in folders:
        grille = copy.deepcopy(main_grille)
        #remove spaces from folders
        new_folder = folder.replace(" ","")
        if( folder != new_folder):
            os.rename(folder,new_folder)
        #get student info
        info = os.path.basename(new_folder).split("_")
        student_name = info[0]
        student_code = info[1]

        condition = 0
        new_file = None
        try:
            #get all student files
            files = [f for f in glob.glob(new_folder + "/*.js")]
            if len(files) == 0:
                files = None
                condition = 1
            elif len(files) == 1:
                print("nom: {}".format(student_name))
                #Remove spaces from student files
                new_file = files[0].replace(" ","").replace("(","").replace(")","")
                if( files[0] != new_file):
                    os.rename(files[0],new_file)
                os.system("{} {} {} {}".format(path_correcteur,new_file,'>',new_folder + '/resultat.txt'))
               # if stop:
               #     stop = False
               #     continue
                #subprocess.run([path_correcteur, files[0],'>', new_folder + '/correction.txt'])
        except:
            condition = 2

        etudiant = Etudiant(student_code,student_name, condition,grille, new_folder,new_file)
        students.append(etudiant)
    return students

def get_grille(path):
    csvFile = open(path,"r")
    output = csvFile.readlines()
    bareme = []
    for i,line in enumerate(output):
        line = line.replace("\n","")
        bareme.append(line.split(","))
        bareme[i].append(None)
    return bareme

def save_classe(data, path):
    pickle.dump( data, open(path, "wb"),
                 protocol=pickle.HIGHEST_PROTOCOL)

def load_classe(path):

    classe = pickle.load( open(path, "rb"))
    
    return classe

def get_result_text(student):
    try:
        text = open(student.path + '/resultat.txt',"r")
        return text.read()
    except:
        return "Erreur, pas de resultat"

def get_code_text(student):
    try:
        text = open(student.code_file,"r")
        return text.read()
    except:
        return "Erreur, pas de resultat"

def output_student_grille(student):
    output = ""
    bareme = student.grille.bareme
    output += "note: {}\n".format(student.note)
    for grade in bareme:
        output += "{}/{} {}\n".format(grade[2],grade[0],grade[1])
    output += student.grille.commentaires

    f = open(student.path + "/{}Grille.md".format(student.nom),"w")
    f.write(output)
    f.close()

def open_code_file(student):
    os.system("emacs {} &".format(student.code_file))

def open_result_file(student):
    os.system("emacs {} &".format(student.path + "/resultat.txt"))

def get_average(classe):
    total = 0
    for etudiant in classe.etudiants:
        if etudiant.note != None:
            total += etudiant.note
    average = total/len(classe.etudiants)

    return average

#Objects
class Classe:
    def __init__(self,etudiants,grille,path):
        self.etudiants = etudiants
        self.grille = grille
        self.path = path
        
class Etudiant:
    def __init__(self,code,nom, condition, grille, path, code_file):
        self.code = code
        self.nom = nom
        self.condition = condition
        self.grille = grille
        
        self.note = None

        self.path = path
        self.code_file = code_file
        
class Grille:
    def __init__(self, bareme,path):
        self.bareme = bareme
        self.path = path
        self.commentaires = ""
