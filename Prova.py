from openpyxl import load_workbook
import win32com.client as win32
import os
import keyboard
import time
import json
from tkinter import *
from tkinter import messagebox as MessageBox

root = Tk()

x = int(input("Hola, amb qui estic parlant? (1:Hicham, 2:Laura, 3:Pau, altres:jf0) "))

directori_principal = os.path.dirname(os.path.abspath(__file__))

db_1 = os.path.join(directori_principal, "prova.xlsx")

llibre_1 = load_workbook(db_1)
fulla_1 = llibre_1.active

if x == 1:
    MessageBox.showwarning("Alerta",fulla_1["B2"].value)
elif x == 2:
    MessageBox.showwarning("Alerta",fulla_1["B4"].value)
elif x == 3:
    MessageBox.showwarning("Alerta",fulla_1["B6"].value)
else:
    MessageBox.showwarning("Alerta",fulla_1["B8"].value)

root.mainloop()