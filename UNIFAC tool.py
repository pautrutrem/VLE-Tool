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

#1. Calcular Psi = exp(-a_mn / T)
def psi(grup_1, grup_2, T, interaccions):
    
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

#2. Calcular los parámetros de superfície (Qk) y volumen (Rk) totles de una molécula
def Qk_Rk_mol(substancia, molecules, prop_grups):
    grups_subs = molecules[substancia]
    q = 0.0
    r = 0.0
    for sym, count in grups_subs.items():
        props = prop_grups[sym]
        q += count * props["Qk"]
        r += count * props["Rk"]
    return r, q

#3. Cálculo del modelo combinatorio y residual
def combinatori(substancies, x, molecules, prop_grups, z=10.0):

    #Calcular la parte combinatoria (medida y forma): ln(gamma_i)^C
    r_vals = []
    q_vals = []

    #Obtener Rk y Qk para cada componente
    for sub in substancies:
        r, q = Qk_Rk_mol(sub, molecules, prop_grups)
        r_vals.append(r)
        q_vals.append(q)
    
    #Sumatorios totales de Rk y Qk de la mezcla
    r_total = sum(x[i] * r_vals[i] for i in range(len(x)))
    q_total = sum(x[i] * q_vals[i] for i in range(len(x)))

    #Determinación de ln(gamma_c)
    lng_c = []
    for i in range(len(x)):

        #Fracciones de segmento (phi) y área (theta)
        phi_i = (x[i] * r_vals[i]) / r_total
        theta_i = (x[i] * q_vals[i]) / q_total

        #Parámetro l_i
        l_i = (z / 2) * (r_vals[i] - q_vals[i]) - (r_vals[i] - 1)

        #Término sumatorio de l_j
        suma_x_l = sum(x[j] * ((z / 2) * (r_vals[j] - q_vals[j]) - (r_vals[j] - 1)) for j in range(len(x)))

        #Fórmula final
        res = np.log(phi_i / x[i]) + (z / 2) * q_vals[i] * np.log(theta_i / phi_i) + l_i - (phi_i / x[i]) * suma_x_l
        lng_c.append(res)
    
    return lng_c

def calc_ln_gamma_grups(cont_grups, T, prop_grups, interaccions):

    #Calcula ln(gamma_k) para un conjunto de grupos (mezcla o puro). Es el núcleo matemático de la parte residual
    
    #Fracciones de área de grupo (Theta_m)
    a_total = 0.0
    grups_unics = list(cont_grups.keys())

    for sym, count in cont_grups.items():
        Qk = prop_grups[sym]["Qk"]
        a_total += count * Qk
    
    theta = {}
    for sym in grups_unics:
        theta[sym] = (cont_grups[sym] * prop_grups[sym]["Qk"]) / a_total

    #Calcular ln_gamma para cada grupo k
    ln_gamma = {}
    for k in grups_unics:
        k_num = prop_grups[k]["Group_No"]
        Qk = prop_grups[k]["Qk"]

        #Primer sumatorio: sum(theta_m * Psi_mk)
        sum1 = 0.0
        for m in grups_unics:
            m_num = prop_grups[k]["Group_No"]
            sum1 += theta[m] * psi(m_num, k_num, T, interaccions)
        
        #Segundo sumatorio
        sum2 = 0.0
        for m in grups_unics:
            m_num = prop_grups[k]["Group_No"]

            denom = 0.0
            for n in grups_unics:
                n_num = prop_grups[n]["Group_No"]
                denom += theta[n] * psi(n_num, m_num, T, interaccions)

            sum2 += (theta[m] * psi(k_num, m_num, T, interaccions)) / denom

        ln_gamma[k] = Qk * (1 - np.log(sum1) - sum2)

    return ln_gamma

def calc_residual(substancies, x, T, molecules, prop_grups, interaccions):

    #Calcular la parte residual -> ln_gamma_i^R = sum(v_k * (ln_gamma_k_mezcla - ln_gamma_k_puro))

    #Definir composición grupos de la mezcla total
    grups_mescla = {}
    for i, sub in enumerate(substancies):
        grups_mol = molecules[sub]
        for sym, count in grups_mol.items():
            grups_mescla[sym] = grups_mescla.get(sym, 0) + x[i] * count
    
    #ln_gamma_k en la mezcla
    ln_gamma_mix = calc_ln_gamma_grups(grups_mescla, T, prop_grups, interaccions)

    lng_r = []

    #Calcular para cada compuesto i
    for sub in substancies:

        #ln_gamma_k per al component pur
        grups_pur = molecules[sub]
        ln_gamma_pure = calc_ln_gamma_grups(grups_pur, T, prop_grups, interaccions)

        res = 0.0
        for k, v_k in grups_pur.items():
            res += v_k * (ln_gamma_mix[k] - ln_gamma_pure[k])

        lng_r.append(res)
    
    return lng_r

#Función principal

def coefs_act(substancies, x, T, molecules, prop_grups, interaccions):

    #Opcional: Normalizar fracciones molares
    if abs(sum(x) - 1.0) > 1e-4:
        x = np.array(x) / sum(x)

    #Calcular partes combinatorias y residuales
    lng_c = combinatori(substancies, x, molecules, prop_grups)
    lng_r = calc_residual(substancies, x, T, molecules, prop_grups, interaccions)

    #Sumar y hacer exponencial
    ln_gamma = [c + r for c, r in zip(lng_c, lng_r)]
    return np.exp(ln_gamma)

#Ejemplo
if __name__ == "__main__":
    prop_grups, interaccions, molecules = carregar_dades()
    compostos_sel = ["Ethanol", "Water"]
    x_sel = [0.4, 0.6] #40% en mol de Etanol
    T_sel = 298.15 #K

    try:
        gammas = coefs_act(compostos_sel, x_sel, T_sel, molecules, prop_grups, interaccions)

        print(f"Sistema: {compostos_sel}")
        print(f"Composició x: {x_sel}")
        print(f"Temperatura: {T_sel}")
        print("-" * 30)
        for sub, g in zip(compostos_sel, gammas):
            print(f"Gamma ({sub}): {g:.4f}")
    except Exception as e:
        print(f"Error: {e}")