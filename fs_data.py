from swarm import Swarm
from fs_problem import FsProblem
import pandas as pd
import os, re, time, sys
from rl import QLearning
from solution import Solution
import xlsxwriter

class FSData():

    def __init__(self,typeOfAlgo,location,nbr_exec, method, test_param, param, val, classifier, alpha=None,gamma=None,epsilon=None):

        self.typeOfAlgo = typeOfAlgo
        self.location = location
        self.nb_exec = nbr_exec
        self.dataset_name = re.search('[A-Za-z\-]*.csv',self.location)[0].split('.')[0]
        self.df = pd.read_csv(self.location,header=None)
        self.ql = QLearning(len(self.df.columns),Solution.attributs_to_flip(len(self.df.columns)-1),alpha,gamma,epsilon)
        self.fsd = FsProblem(self.typeOfAlgo,self.df,self.ql)
        
        self.classifier_name = str(type(self.fsd.classifier)).strip('< > \' class ').split('.')[3]
        path = './results/parameters/'+method+'/'+test_param+'/'+param+'/'+val+'/'+classifier+'/'+ self.dataset_name
        if not os.path.exists(path):
          os.makedirs(path + '/logs/')
          os.makedirs(path + '/sheets/')
        self.instance_name = self.dataset_name + '_' +  str(time.strftime("%m-%d-%Y_%H-%M-%S_", time.localtime()) + self.classifier_name)
        log_filename = str(path + '/logs/'+ self.instance_name)
        if not os.path.exists(path):
          os.makedirs(path)
        log_file = open(log_filename + '.txt','w+')
        sys.stdout = log_file
        
        print("[START] Dataset " + self.dataset_name + " description \n")
        print("Shape : " + str(self.df.shape) + "\n")
        print(self.df.describe())
        print("\n[END] Dataset " + self.dataset_name + " description\n")
        print("[START] Ressources specifications\n")
        #os.exec('cat /proc/cpuinfo') # Think of changing this when switching between Windows & Linux
        print("[END] Ressources specifications\n")

        
        sheet_filename = str(path + '/sheets/'+ self.instance_name )
        self.workbook = xlsxwriter.Workbook(sheet_filename + '.xlsx')
        
        self.worksheet = self.workbook.add_worksheet(self.classifier_name)
        self.worksheet.write(0,0,"Iteration")
        self.worksheet.write(0,1,"Accuracy")
        self.worksheet.write(0,2,"N_Features")
        self.worksheet.write(0,3,"Time")
        self.worksheet.write(0,4,"Top_10%_features")
        self.worksheet.write(0,5,"Size_sol_space")
    
    def run(self,flip,max_chance,bees_number,maxIterations,locIterations):
        total_time = 0
        
        for itr in range(1,self.nb_exec+1):
          print ("Execution {0}".format(str(itr)))
          self.fsd = FsProblem(self.typeOfAlgo,self.df,self.ql)
          swarm = Swarm(self.fsd,flip,max_chance,bees_number,maxIterations,locIterations)
          t1 = time.time()
          best = swarm.bso(self.typeOfAlgo,flip)
          t2 = time.time()
          total_time += t2-t1
          print("Time elapsed for execution {0} : {1:.2f} s\n".format(itr,t2-t1))
          self.worksheet.write(itr, 0, itr)
          self.worksheet.write(itr, 1, "{0:.2f}".format(best[0]))
          self.worksheet.write(itr, 2, best[1])
          self.worksheet.write(itr, 3, "{0:.3f}".format(t2-t1))
          self.worksheet.write(itr, 4, "{0}".format(str([j[0] for j in [i for i in swarm.best_features()]])))
          self.worksheet.write(itr, 5, len(Solution.solutions))
          
        print ("Total execution time of {0} executions \nfor dataset \"{1}\" is {2:.2f} s".format(self.nb_exec,self.dataset_name,total_time))
        self.workbook.close()
