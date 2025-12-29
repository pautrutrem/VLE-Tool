import pandas as pd
import numpy as np

#Primer paso: Carga y preparación de los datos de la base de datos en Excel

def load_unifac_data():

    #Cargar archivos Excel

    filename = "UNIFAC_database.xlsx"
    groups_df = pd.read_excel(filename, sheet_name="UNIFAC_Groups", engine="openpyxl")
    interaction_df = pd.read_excel(filename, sheet_name="Param_amn", engine="openpyxl")
    compounds_df = pd.read_excel(filename, sheet_name="Groups_compounds", engine="openpyxl")

    #Crear diccionario de propiedades -> {Grupo, Rk, Qk}
    group_props = groups_df.set_index('Symbol')[['Group_No', 'Rk', 'Qk']].to_dict('index')

    #Crear diccionario de interacciones: (Grupo_m, Grupo_n) -> Parámetro a_mn
    interactions = {}
    for _, row in interaction_df.iterrows():
        interactions[(int(row['Group_m']), int(row['Group_n']))] = row['Param']

    #Definir grupos de cada compuesto -> {Grupo: Cantidad}
    molecule_defs = {}
    for _, row in compounds_df.iterrows():
        substance = row['Substance']
        groups = {}
        for col in compounds_df.columns:
            if 'Group' in col and pd.notna(row[col]):
                g_sym = row[col]
                groups[g_sym] = groups.get(g_sym, 0) + 1
        molecule_defs[substance] = groups

    #Obtener resultados
    return group_props, interactions, molecule_defs

#Segundo paso: Diseño de funciones propias de UNIFAC

#1. Calcular Psi = exp(-a_mn / T)
def get_psi(group1_id, group2_id, T, interactions):

    #Si el grupo es el mismo, devuelve 1
    if group1_id == group2_id:
        return 1.0
    
    #Obtener el parámetro a_mn
    a_mn = interactions.get((group1_id, group2_id))
    
    #Si la interacción no se encuentra, se asume 1
    if a_mn is None:
        return 1.0 
    
    #Devolver el valor de Psi
    return np.exp(-a_mn / T)

#2. Calcular los parámetros de superfície (Qk) y volumen (Rk) totales de una molécula
def get_molecule_r_q(substance, molecule_defs, group_props):
    groups = molecule_defs[substance]
    r = 0.0
    q = 0.0
    for sym, count in groups.items():
        props = group_props[sym]
        r += count * props['Rk']
        q += count * props['Qk']
    return r, q

#3. Cálculo del modelo combinatorio y residual
def calculate_combinatorial(substances, x, molecule_defs, group_props, z=10.0):

    #Calcular la parte combinatoria (medida y forma): ln(gamma_i)^C
    r_vals = []
    q_vals = []
    
    #Obtener Rk y Qk para cada componente
    for sub in substances:
        r, q = get_molecule_r_q(sub, molecule_defs, group_props)
        r_vals.append(r)
        q_vals.append(q)

    #Sumatorios totales de Rk y Qk de la mezcla
    total_r = sum(x[i] * r_vals[i] for i in range(len(x)))
    total_q = sum(x[i] * q_vals[i] for i in range(len(x)))

    #Determinación de ln(gamma_c)
    lng_c = []
    for i in range(len(x)):

        #Fracciones de segmento (phi) y área (theta)
        phi_i = (x[i] * r_vals[i]) / total_r
        theta_i = (x[i] * q_vals[i]) / total_q
        
        #Parámetro l_i
        l_i = (z / 2) * (r_vals[i] - q_vals[i]) - (r_vals[i] - 1)
        
        #Término sumatorio de l_j
        sum_x_l = sum(x[j] * ((z / 2) * (r_vals[j] - q_vals[j]) - (r_vals[j] - 1)) for j in range(len(x)))

        #Fórmula final
        term = np.log(phi_i / x[i]) + (z/2) * q_vals[i] * np.log(theta_i / phi_i) + l_i - (phi_i / x[i]) * sum_x_l
        lng_c.append(term)
        
    return lng_c

#4.Calcula ln(gamma_k) para un conjunto de grupos (mezcla o puro). Es el núcleo matemático de la parte residual
def calculate_group_ln_gamma(group_counts, T, group_props, interactions):
    
    #Fracciones de área de grupo (Theta_m)
    total_area = 0.0
    unique_groups = list(group_counts.keys())
    
    for sym, count in group_counts.items():
        Qk = group_props[sym]['Qk']
        total_area += count * Qk
        
    Theta = {}
    for sym in unique_groups:
        Theta[sym] = (group_counts[sym] * group_props[sym]['Qk']) / total_area

    #Calcular ln_gamma para cada grupo k
    ln_Gamma = {}
    for k in unique_groups:
        k_id = group_props[k]['Group_No']
        Qk = group_props[k]['Qk']
        
        #Primer sumatorio: sum(theta_m * Psi_mk)
        sum1 = 0.0
        for m in unique_groups:
            m_id = group_props[m]['Group_No']
            sum1 += Theta[m] * get_psi(m_id, k_id, T, interactions)
        
        #Segundo sumatorio
        sum2 = 0.0
        for m in unique_groups:
            m_id = group_props[m]['Group_No']
            
            denom = 0.0
            for n in unique_groups:
                n_id = group_props[n]['Group_No']
                denom += Theta[n] * get_psi(n_id, m_id, T, interactions)
            
            sum2 += (Theta[m] * get_psi(k_id, m_id, T, interactions)) / denom
        
        ln_Gamma[k] = Qk * (1 - np.log(sum1) - sum2)
        
    return ln_Gamma

#Calcular la parte residual -> ln_gamma_i^R = sum(v_k * (ln_gamma_k_mezcla - ln_gamma_k_puro))
def calculate_residual(substances, x, T, molecule_defs, group_props, interactions):
    
    #Definir composición grupos de la mezcla total
    mixture_groups = {}
    for i, sub in enumerate(substances):
        mol_groups = molecule_defs[sub]
        for sym, count in mol_groups.items():
            mixture_groups[sym] = mixture_groups.get(sym, 0) + x[i] * count
    
    #ln_gamma_k en la mezcla
    ln_Gamma_mix = calculate_group_ln_gamma(mixture_groups, T, group_props, interactions)
    
    lng_r = []
    
    #Calcular para cada compuesto i
    for sub in substances:

        #ln_gamma_k per al component pur
        pure_groups = molecule_defs[sub]
        ln_Gamma_pure = calculate_group_ln_gamma(pure_groups, T, group_props, interactions)
        
        term = 0.0
        for k, v_k in pure_groups.items():
            term += v_k * (ln_Gamma_mix[k] - ln_Gamma_pure[k])
        
        lng_r.append(term)
        
    return lng_r

#Función principal

def get_activity_coefficients(substances, x, T, molecule_defs, group_props, interactions):
    
    #Opcional: Normalizar fracciones molares
    if abs(sum(x) - 1.0) > 1e-4:
        x = np.array(x) / sum(x)

    #Calcular partes combinatorias y residuales
    lng_c = calculate_combinatorial(substances, x, molecule_defs, group_props)
    lng_r = calculate_residual(substances, x, T, molecule_defs, group_props, interactions)
    
    #Sumar y hacer exponencial
    ln_gamma = [c + r for c, r in zip(lng_c, lng_r)]
    return np.exp(ln_gamma)

#Ejemplo
if __name__ == "__main__":
    group_props, interactions, molecule_defs = load_unifac_data()
    my_substances = ["Ethanol", "Water"]
    my_x = [0.4, 0.6] #40% en mol de Etanol
    my_T = 298.15 #K

    gammas = get_activity_coefficients(my_substances, my_x, my_T, molecule_defs, group_props, interactions)

    print(f"Sistema: {my_substances}")
    print(f"Composición molar x: {my_x}")
    print(f"Temperatura: {my_T}")
    print("-" * 30)
    for sub, g in zip(my_substances, gammas):
        print(f"Gamma ({sub}): {g:.4f}")