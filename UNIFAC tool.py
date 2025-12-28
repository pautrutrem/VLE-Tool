import pandas as pd
import numpy as np

#Primer paso: Carga y preparación de los datos de la base de datos en Excel

def carregar_dades():

    #Cargar archivos Excel
    compostos = pd.read_csv("UNIFAC_database.xlsx - Groups_compounds.csv")
    grups = pd.read_csv("UNIFAC_database.xlsx - UNIFAC_Groups.csv")
    int_param_mn = pd.read_csv("UNIFAC_database.xlsx - Param_amn.csv")

    
