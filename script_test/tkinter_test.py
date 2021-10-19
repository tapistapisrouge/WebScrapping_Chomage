# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 10:46:11 2021

@author: amaur
"""

suite_code = 'non'

path_tkinter="C:/Users/amaur/Documents/GitHub/WebScrapping_chomage/tkinter/index.ico"


print('coucou')

# Tkinter demande identifiant et mdp
# on entre les 2 infos et la boîte se ferme si ça marche

import tkinter as tk
from tkinter import ttk

def test():
    print('suite du code')


# fenetre principale
root = tk.Tk()
root.geometry("240x200")
root.title('Login Webscrapping')
  
root.iconbitmap(path_tkinter)

root.maxsize(800,600)
root.minsize(240,100)
root.config(bg = "#000000")
#root.resizable(0,0)

# configuration de la grid
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=3)

# fonctions
def action_login_button():
    username = username_entry.get()
    print(username)
    password = password_entry.get()
    print(password) 
    # exécuter selenium 
    if password=='super!':
        infos='Connexion établie'
        global var_glob
        var_glob=password_entry.get()

    else:
        infos='Mdp erroné'
    infos_label['text'] = infos  


def action_quit_button():
    root.destroy()


# username / identifiant
username_label = ttk.Label(root, text = "Username:")
username_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

username_entry = ttk.Entry(root)
username_entry.grid(column=1, row=0, sticky=tk.E, padx=5, pady=5)

# password / mot de passe
password_label = ttk.Label(root, text = "Password:")
password_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

password_entry = ttk.Entry(root)
password_entry.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)

# button 
login_button = ttk.Button(root, text="Login", command=action_login_button)
login_button.grid(column=1, row=2, sticky=tk.E, padx=5, pady=5)

# label infos connexion
infos_label = ttk.Label(root, text = "En attente de vos identifiants...")
infos_label.grid(column=0, row=3, columnspan=2, sticky=tk.W, padx=5, pady=5)

# Quit 
quit_button = ttk.Button(root, text="Quit", command=action_quit_button)
quit_button.grid(column=1, row=4, sticky=tk.E, padx=5, pady=5)

root.mainloop()


print(var_glob)