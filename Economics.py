import os
import win32com.client as win32
import time
import keyboard
from openpyxl import load_workbook
from openpyxl import Workbook

file='Economics.bkp'

aspen_Path = os.path.abspath(file)
print('path=',aspen_Path)

print('\n Connecting to the Aspen Plus... Please wait ')
Application = win32.Dispatch('Apwn.Document')
print('Connected!')

Application.InitFromArchive2(aspen_Path)
Application.visible = 1

time.sleep(10)
keyboard.press_and_release("alt+tab")

time.sleep(3)
keyboard.press_and_release("alt")
time.sleep(0.5)
keyboard.press_and_release("h")
time.sleep(0.5)
keyboard.press_and_release("r")

time.sleep(10)
keyboard.press_and_release("alt")
time.sleep(0.5)
keyboard.press_and_release("e")
time.sleep(0.5)
keyboard.press_and_release("e")

time.sleep(5)
keyboard.press_and_release("alt")
time.sleep(0.5)
keyboard.press_and_release("e")
time.sleep(0.5)
keyboard.press_and_release("l")
time.sleep(5)
keyboard.press_and_release("enter")
time.sleep(0.5)
keyboard.press_and_release("enter")

time.sleep(10)
keyboard.press_and_release("alt")
time.sleep(0.5)
keyboard.press_and_release("e")
time.sleep(0.5)
keyboard.press_and_release("n")

time.sleep(35)

def trobar_fitxer(nom_fitxer, directori_inici="/"):
    for arrel, carpetes, fitxers in os.walk(directori_inici):
        if nom_fitxer in fitxers:
            return os.path.join(arrel, nom_fitxer)
    return None

ruta = trobar_fitxer("IPEWB1.xls", "C:\\")  # En Windows, comença per C:\
print(ruta)

import pandas as pd

def convertir_xls_a_xlsx(ruta_xls, ruta_xlsx):
    # Llegeix el .xls
    xls = pd.ExcelFile(ruta_xls)

    # Crea un writer per guardar en .xlsx
    with pd.ExcelWriter(ruta_xlsx, engine='openpyxl') as writer:
        for full in xls.sheet_names:
            df = pd.read_excel(ruta_xls, sheet_name=full)
            df.to_excel(writer, sheet_name=full, index=False)

    print("Conversió completada:", ruta_xlsx)

ruta_xlsx = ruta.replace(".xls", ".xlsx")
convertir_xls_a_xlsx(ruta, ruta_xlsx)

llibre_1 = load_workbook(ruta_xlsx)
fulla_individual = llibre_1["Equipment"]

i = 11
n = 4

fulla_final = Workbook()
nom_fulla_final = "Economics.xlsx"
fulla_final.save(nom_fulla_final)

llibre_2 = load_workbook(nom_fulla_final)
fulla_2 = llibre_2.active

fulla_2["B3"].value = "Nom del equip"
fulla_2["B4"].value = "Tipus d'equip"
fulla_2["B5"].value = "Cost directe total [USD]"
fulla_2["B6"].value = "Cost de l'equip [USD]"
fulla_2["B7"].value = "Pes de l'equip [lbs]"
fulla_2["B8"].value = "Pes de l'equip instal·lat [lbs]"

ascii_ref = 67
c = 0

while n > 0:
    if str(fulla_individual["B"+str(i)].value) is None:
        i += 1
    else:
        fulla_2[str(chr(ascii_ref+c))+"3"].value = str(fulla_individual["B"+str(i)].value)
        fulla_2[str(chr(ascii_ref+c))+"4"].value = str(fulla_individual["C"+str(i)].value)
        fulla_2[str(chr(ascii_ref+c))+"5"].value = str(fulla_individual["D"+str(i)].value)
        fulla_2[str(chr(ascii_ref+c))+"6"].value = str(fulla_individual["E"+str(i)].value)
        fulla_2[str(chr(ascii_ref+c))+"7"].value = str(fulla_individual["F"+str(i)].value)
        fulla_2[str(chr(ascii_ref+c))+"8"].value = str(fulla_individual["G"+str(i)].value)
        i += 1
        n -= 1
        c += 1

llibre_2.save(nom_fulla_final)