import pandas as pd
import numpy as np

#Primer paso: Carga y preparación de los datos de la base de datos en Excel

def carregar_dades():

    #Cargar archivos Excel
    compostos = pd.read_csv("UNIFAC_database.xlsx - Groups_compounds.csv")
    grups = pd.read_csv("UNIFAC_database.xlsx - UNIFAC_Groups.csv")
    int_param_mn = pd.read_csv("UNIFAC_database.xlsx - Param_amn.csv")

    #Crear diccionario de propiedades -> {Grupo, Rk, Qk}
    prop_grups = grups.set_index("Symbol")[["Group_No","Rk","Qk"]].to_dict("index")
    
    #Crear diccionario de interacciones: (Grupo_m, Grupo_n) -> Parámetro a_mn
    interaccions = {}
    for _, row in int_param_mn.iterrows():
        interaccions[(int(row["Group_m"]),int(row["Group_n"]))] = row["a_mn"]
    
    #Definir grupos de cada compuesto -> {Grupo: Cantidad}
    molecules = {}
    for _, row in compostos.iterrows():
        substancia = row["Substance"]
        grups_subs = {}
        for col in compostos.columns:
            if "Groups" in col and pd.notna(row[col]):
                g_sym = row[col]
                grups_subs[g_sym] = grups_subs.get(g_sym, 0) + 1
        molecules[substancia] = grups_subs

    #Obtener resultados
    return prop_grups, interaccions, molecules

#Segundo paso: Diseño de funciones propias de UNIFAC

def psi(grup_1, grup_2, T, interaccions): #Calcular Psi = exp(-a_mn / T)
    
    #Si el grupo es el mismo, devuelve 1.0
    if grup_1 == grup_2:
        return 1.0
    
    #Obtener el parámetro a_mn
    a_mn = interaccions.get((grup_1, grup_2))

    #Si la interacción no se encuentra, se asume 0
    if a_mn is None:
        return 0.0
    
    #Devolver el valor de Psi
    return np.exp(-a_mn / T)
