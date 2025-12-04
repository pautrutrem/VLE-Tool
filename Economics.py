import os
import win32com.client as win32
import time
import keyboard
from openpyxl import load_workbook

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

time.sleep(3)
keyboard.press_and_release("alt")
time.sleep(0.5)
keyboard.press_and_release("e")
time.sleep(0.5)
keyboard.press_and_release("l")
time.sleep(2)
keyboard.press_and_release("enter")
time.sleep(0.5)
keyboard.press_and_release("enter")

time.sleep(5)
keyboard.press_and_release("alt")
time.sleep(0.5)
keyboard.press_and_release("e")
time.sleep(0.5)
keyboard.press_and_release("n")

n = 1

time.sleep(25)

#Cerrar Excel

directori_principal = os.path.dirname(os.path.abspath(__file__))

db_1 = os.path.join(directori_principal, "IPEWB"+str(n)+".xlsx")

llibre_1 = load_workbook(db_1)
fulla_individual = db_1["Equipment"]

i = 4

while i <= 500:
    if fulla_individual["B"+str(i)].Value == "":
        i += 1
    else:
        print("Nom del equip = "+ fulla_individual["B"+str(i)].Value)
        print("")
        print("Tipus d'equip = "+ fulla_individual["C"+str(i)].Value)
        print("")
        print("Cost directe total = "+ fulla_individual["D"+str(i)].Value + "$")
        print("")
        print("Cost de l'equip = "+ fulla_individual["E"+str(i)].Value + "$")
        print("")
        print("Pes de l'equip = "+ fulla_individual["F"+str(i)].Value + "lbs")
        print("")
        print("Pes de l'equip instal·lat = "+ fulla_individual["G"+str(i)].Value + "lbs")