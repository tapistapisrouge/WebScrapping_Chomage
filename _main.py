# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 16:19:45 2021

@author: amaur

Objectifs :
    - récupérer les offres sur différentes pages web (infos basiques : titre, cdd/cdi, date de début)
    - Mettre en forme les données
    - Comparer les offres aux offres attrappées du dernier lancement de script
    - Extraire les nouvelles offres du jour ! :)
"""

#==============================================================================================
# Modules/Packages à importer =================================================================
#==============================================================================================

import re
import pandas as pd
import pathlib # pour gérer les chemins
import datetime
import time

# requests ==> lancer une requête web type "GET une page web" ou un POST
# requests ==> pour faire les requêtes web et chopper les pages sont format html
import requests
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession # gestion javascript

# bs4 ==> transformer les pages en objet soup et chercher rapidement les infos voulues des différentes balises
from bs4 import BeautifulSoup

# Selenium : permet de lancer un navigateur headless, intéragir avec la page (cliquer sur un boutou etc)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# pour mdp et identifiant
import tkinter as tk
from tkinter import ttk


#==============================================================================================
# Chemin absolu à modifier si changement de dossier ou de pc===================================
#==============================================================================================
path_project='C:/Users/amaur/Documents/GitHub/WebScrapping_chomage'

path_pdf=pathlib.Path(path_project, 'arvalis_pdf')
print(path_pdf)

path_csv = pathlib.Path(path_project, 'tableaux_recap')
print(path_csv)

path_webdriver = pathlib.Path(path_project, 'webdriver')
print(path_webdriver)
path_firefox=pathlib.Path(path_webdriver, 'geckodriver.exe')
path_chrome=pathlib.Path(path_webdriver, 'chromedriver.exe')

path_tkinter = pathlib.Path(path_project, 'tkinter/index.ico')
print(path_tkinter)



#==============================================================================================
# Dataframe de base ===========================================================================
#==============================================================================================

# créer dataframe qui stockera les données du script lancé un jour X
offres_emploi = pd.DataFrame(columns=['ID',
                                      'Organisme',
                                      'Titre',
                                      'Lieu',
                                      'Type_contrat',
                                      'Debut_emploi',
                                      'Limite_date_cv',
                                      'Date_depot_offre',
                                      'Synthese',
                                      'URL_offre'])


#==============================================================================================
# Config des webdriver ========================================================================
#==============================================================================================

# configure Chrome Webdriver
def configure_chrome_driver():
    # Add additional Options to the webdriver
    chrome_options = ChromeOptions()
    # add the argument and make the browser Headless.
    chrome_options.add_argument("--headless")
    # Mettre une taille de fenêtre : technique pour ne pas être considéré comme un bot ?
    chrome_options.add_argument("--window-size=1920,1200")
    # Instantiate the Webdriver: Mention the executable path of the webdriver you have downloaded
    # if driver is in PATH, no need to provide executable_path
    driver = webdriver.Chrome(executable_path=path_chrome, options = chrome_options)
    return driver

# configure Firefox Driver
def configure_firefox_driver():
    # Add additional Options to the webdriver
    firefox_options = FirefoxOptions()
    # add the argument and make the browser Headless.
    firefox_options.add_argument("--headless")
    # Mettre une taille de fenêtre : technique pour ne pas être considéré comme un bot ?
    firefox_options.add_argument("--window-size=1920,1200")
    # Instantiate the Webdriver: Mention the executable path of the webdriver you have downloaded
    # if driver is in PATH, no need to provide executable_path
    driver = webdriver.Firefox(executable_path = path_firefox, options = firefox_options)
    return driver



#==============================================================================================
# WEB SCRAPING SIMPLE, page accessible et sans javascript =====================================
#==============================================================================================

#==============================================================================================
# Exemple 1 ==> ARVALIS
organisme='Arvalis'

# Possibilité de lancer une requests.get ou request.post directement
# La session n'est pas obligatoire (bonne pratique quand même)
# Intérêt de la session :
# 1. Garde les cookies de session à chaque requête
# 2. On peut mettre des headers en paramètre qui seront affectés tout le long de la session
# Ex : header user agent = permet de ne pas passer pour un bot et de se faire bloquer dans certains cas


with requests.Session() as arvalis_session:
    # l'url voulu
    urlpage ='https://www.arvalisinstitutduvegetal.fr/emplois-et-stages-@/view-1319-category.html'
    # on choppe la page (différentes méthodes sur l'objet page_arvalis : cookies, headers, url, text, content, etc)   
    page_arvalis=arvalis_session.get(urlpage)
    # en tête envoyée sans le headers 
    print(page_arvalis.request.headers)
    # {'User-Agent': 'python-requests/2.26.0',
    #'Accept-Encoding': 'gzip, deflate, br', 
    #'Accept': '*/*', 'Connection': 'keep-alive'}
    
    # headers modifiés si blocage de bot : 
    # pb pour mettre le headers dans la session donc uniquement dans les requetes 
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'}
    PARAMS = {'header':headers} 
    # on lance le get avec headers : user agent modifié
    urlpage ='https://www.arvalisinstitutduvegetal.fr/emplois-et-stages-@/view-1319-category.html'
    # on choppe la page (différentes méthodes sur l'objet page_arvalis : cookies, headers, url, text, content, etc)   
    page_arvalis=arvalis_session.get(urlpage, headers=headers)
    # en tête envoyée avec notre headers modifié 
    print(page_arvalis.request.headers) 
    # {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0', 
    #'Accept-Encoding': 'gzip, deflate, br', 'Accept': '*/*', 
    #'Connection': 'keep-alive', 
    #'Cookie': 'JSESSIONID=3E859509B0D337CF2FF055279E51D4E6.tomcat1'}
    
    # Le code de statut de réponse HTTP 200 OK indique la réussite d'une requête
    if page_arvalis.status_code==200:       
        # objet BeautifulSoup, page html complète
        soup_arvalis=BeautifulSoup(page_arvalis.text,'html.parser')
        print(soup_arvalis)   
    
        # lister les éléments des balises div de class:"offre row", 1 élément = une offre
        offres=soup_arvalis.find_all('div', {'class':'offre row'})
    
        for offre in offres:
            # on récupère le titre
            titre = offre.find("h2", recursive=False).getText()
            print(titre)
            # on récupère les infos intéressantes
            infos = offre.find_all('div', {'class':'col-lg-6 col-md-6 col-sm-12 col-xs-12 details-offre'})
            # Lieu et contrat
            lieu_contrat=infos[0].find('ul').find_all('li')
            lieu=lieu_contrat[0].getText()
            contrat=lieu_contrat[1].getText()
            motif = re.compile('\n|Type du contrat :| ')
            contrat=re.sub(motif, "", contrat)
            # debut emploi
            debut_emploi=lieu_contrat[2].getText()
            motif = re.compile('Date de début du contrat : ')
            debut_emploi=re.sub(motif, "", debut_emploi) 
            # date dépôt offre
            date_depot_offre=infos[1].find('ul').find('li').getText()
            motif = re.compile("\n|Date de dépot de l'offre : | ")
            date_depot_offre=re.sub(motif, "", date_depot_offre)
            # resume
            #synthese = offres[1].find_all('div', {'class':'col-lg-12 col-md-12 col-sm-12 col-xs-12 details-offre'})
    
            # téléchargement du pdf de l'offre et enregistrement sur le pc
            # titre sans espace pour le nom du pdf qu'on va télécharger et enregistrer
            motif = re.compile("\\W")
            titres=str(re.sub(motif, "", titre)) 
            # récup de l'url de l'offre en pdf 
            href_offre = offre.find('a', {'class':'btn btn-default btn2 pull-left'}).get('href')
            href_finale = 'https://www.arvalisinstitutduvegetal.fr' + href_offre
            #offre_finale=urllib.request.urlretrieve(href_finale, "st-intro.pdf")                                           
            r = arvalis_session.get(href_finale, stream=True)
            #chemin absolu du stockage des pdf
            #path_pdf = 'C:/Users/amaur/Documents/GitHub/JunkiesMessenger/web_scrapping/arvalis_pdf'
            name_pdf = titres + '.pdf'
            path_pdf_temp=pathlib.Path(path_pdf, name_pdf)
            print(path_pdf_temp)
            # mettre le chemin en str
            #path_str=str(path_input)
            #path_str=path_str.replace('\\','/')   
            # voir si le pdf a déjà été enregistrer, si non, on enregistre
            # chunk méthode = permet de faire pas à pas si pdf trop long évite les pb    
            if pathlib.Path.is_file(path_pdf_temp)==False:
                with open(path_pdf_temp, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=1024):
                        fd.write(chunk)
            # ID
            ID = organisme+"_"+titre
            ID= ' '.join(ID.split())
            motif = re.compile(' ')
            ID = str(re.sub(motif, "_", ID)) 
            # on met les info dans la dataframe
            offres_emploi = offres_emploi.append({'ID':ID,
                                                  'Organisme':organisme,
                                                  'Titre':titre,
                                                  'Lieu':lieu,
                                                  'Type_contrat':contrat,
                                                  'Debut_emploi':debut_emploi,
                                                  'Limite_date_cv' : '',
                                                  'Date_depot_offre':date_depot_offre,
                                                  'Synthese' : '',
                                                  'URL_offre': href_finale}, 
                                                  ignore_index=True
                                                    )
        else:
            print("La page n'a pu être récupérée, voici le code d'erreur :")   
            print(page_arvalis.status_code)
                

#==============================================================================================
# Exemple 2 ==> TERRES INOVIA, comme ARVALIS, pas de souis particulier
organisme='Terres Inovia'


# Session
with requests.Session() as inovia_session:
    urlpage ='https://www.terresinovia.fr/web/institutionnel/recrutement'  
    page_inovia = inovia_session.get(urlpage)
    
    if page_inovia.status_code==200: 
        # objet BeautifulSoup, page html complète
        soup_inovia=BeautifulSoup(page_inovia.text,'html.parser')
        print(soup_inovia) 
        
        # lister les éléments "offre row"
        offres=soup_inovia.find_all('div', {'class':'col-1-2'})
        
        for offre in offres:
            #offre=offre.find('div',{'class':'clearfix journal-content-article'})
            offre=offre.find('div',{'class':'offre-vignette'})
            # on récupère le titre
            titre = offre.find("h2", recursive=False).getText()
            print(titre)
            # date dépôt offre
            date_depot_offre= offre.find("small", recursive=False).getText()
            motif = re.compile('Date :')
            date_depot_offre=re.sub(motif, "", date_depot_offre)
            # Lieu date type
            infos=offre.find('div', {'class':'offre-infos'}).find_all("p")
            #lieu
            lieu=infos[0].getText()
            motif = re.compile('Lieu : ')
            lieu = re.sub(motif, "", lieu)   
            contrat=infos[1].getText()
            motif = re.compile(' ')
            contrat = re.sub(motif, "", contrat)     
            # href infos supp
            href_offre=offre.find('div', {'class':'lien'}) 
            url_offre = href_offre.find('a').get('href')
            page_offre = inovia_session.get(url_offre)
            soup_offre=BeautifulSoup(page_offre.text,'html.parser')
            infos=soup_offre.find('div', {'class':'offre-detail'})
            # limite depot cv
            limite_depot_cv=infos.find('div', {'class':'offre-infos'}).find_all("p")
            limite_depot_cv=limite_depot_cv[1].getText()
            motif = re.compile('Date limite de dépôt de candidature : ')
            limite_depot_cv = re.sub(motif, "", limite_depot_cv)    
            # resume
            synthese=infos.find('div', {'class':'offre-contenu'}).find_all("p")
            synthese=synthese[1].getText()
            # ID
            ID = organisme+"_"+titre
            ID= ' '.join(ID.split())
            motif = re.compile(' ')
            ID = str(re.sub(motif, "_", ID))             
            #synthese = offres[1].find_all('div', {'class':'col-lg-12 col-md-12 col-sm-12 col-xs-12 details-offre'})
            # on met les info dans la dataframe
            offres_emploi = offres_emploi.append({'ID':ID,
                                                  'Organisme': organisme,
                                                  'Titre': titre,
                                                  'Lieu': lieu,
                                                  'Type_contrat': contrat,
                                                  'Debut_emploi': '',
                                                  'Limite_date_cv' : limite_depot_cv,
                                                  'Date_depot_offre':date_depot_offre,
                                                  'Synthese' : synthese,
                                                  'URL_offre' : url_offre}, 
                                                  ignore_index=True
                                                 )
    else:
        print("La page n'a pu être récupérée, voici le code d'erreur :")   
        print(page_inovia.status_code)


#==============================================================================================
# Exemple 3 ==> Chambres d'Agriculture, page simple

# Session ca
with requests.Session() as ca_session:
    urlpage ='https://chambres-agriculture.fr/chambres-dagriculture/nous-rejoindre/offres-demploi/'  
    page_ca = ca_session.get(urlpage)
    
    if page_ca.status_code==200: 
        # objet BeautifulSoup, page html complète
        soup_ca = BeautifulSoup(page_ca.text,'html.parser')
        print(soup_ca) 
        
        # lister les éléments "offre row"
        regions = soup_ca.find_all('div', {'class':'liste_emploi'})
        # region bougogne franche comté = 2 (3ème élément)
        # Centre-Val de Loire : 4 (5ème élément)
        # Grand Est : 6
        # Hauts de France : 7
        # Ile de France : 8 (why not...)
        organisme = "Chambre Agriculture"
        
        for i in [2, 4, 6, 7, 8]:
            region = regions[i]
            #region = regions[0]
            # organisme
            #organisme = region.find('div', {'class':'offreemploi_titre_item'}).getText()
            # on récupère les offres de la région en cours
            offres = region.find_all('li', {'class':'display liste_annu'})
            # on fait une boucle pour chaque offre
            for offre in offres:
                #offre = offres[0]
                # récupérer l'url de l'offre en détail
                href_offre = offre.find('p', {'class':'link-puce'}).find('a').get('href')
                href_totale = 'https://chambres-agriculture.fr' + href_offre
                page_offre = ca_session.get(href_totale)
                # objet BeautifulSoup, page html complète
                soup_offre_ca = BeautifulSoup(page_offre.text,'html.parser')
                print(soup_offre_ca)
                # titre
                titre = soup_offre_ca.find('div', {'class':'title_page'}).find('h1').getText()
                # lieu
                lieu = soup_offre_ca.find('div', {'class':'detail_infos_basique_item detail_infos_basique_emetteur'}).find_all('p')[1].getText()
                motif = re.compile('[\n\t]')
                lieu = re.sub(motif, "", lieu)
                # date de publication de l'offre
                Date_depot_offre = soup_offre_ca.find('p', {'class':'detail_date_publication'}).getText()
                Date_depot_offre = re.split(":", Date_depot_offre)
                Date_depot_offre = Date_depot_offre[1]
                # contrat type
                contrat = soup_offre_ca.find('div', {'class':'detail_infos_basique_item detail_infos_basique_type_contrat'}).find_all('p')[1].getText()
                motif = re.compile('[\n\t]')
                contrat = re.sub(motif, "", contrat)
                # Debut emploi
                Debut_emploi = soup_offre_ca.find('div', {'class':'detail_infos_basique_item detail_infos_basique_date_start'}).find_all('p')[1].getText()
                motif = re.compile('[\n\t]')
                Debut_emploi = re.sub(motif, "", Debut_emploi)
                # synthese
                synthese = soup_offre_ca.find('div', {'class':'detail_infos_precise_mission'}).getText()            
                # ID
                ID = organisme+"_"+titre
                ID= ' '.join(ID.split())
                motif = re.compile(' ')
                ID = str(re.sub(motif, "_", ID))                 
                # on met les info dans la dataframe
                offres_emploi = offres_emploi.append({'ID':ID,
                                                      'Organisme': organisme,
                                                      'Titre': titre,
                                                      'Lieu': lieu,
                                                      'Type_contrat': contrat,
                                                      'Debut_emploi': Debut_emploi,
                                                      'Limite_date_cv' : '',
                                                      'Date_depot_offre': Date_depot_offre,
                                                      'Synthese' : synthese,
                                                      'URL_offre' : href_totale}, 
                                                      ignore_index=True
                                                      )

    else:
        print("La page n'a pu être récupérée, voici le code d'erreur :")   
        print(page_ca.status_code)


#==============================================================================================
# WEB SCRAPING JAVASCRIPT =====================================================================
#==============================================================================================

#=================================================================
# IDELE PROBLEME JAVASCRIPT : résolu avec selenium

# on lance le driver
driver = configure_firefox_driver()

# infos url
organisme='Idele'
urlpage ='https://idele.fr' 
urlpage_offres ='https://idele.fr/recrutement' 

# le driver headless va sur la page de recrutement
idele_offres = driver.get(urlpage_offres)

# charger jusq'à ce que la partie javascript soit lisible
# attente de l'élément
try:
    myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//article[@class='article-vertical sectionAllEmplois-article']")))
    print ("Page is ready!")
except TimeoutException:
    print("Loading took too much time!")

# inutile :
# time.sleep(5)

print(driver.page_source)

# on passe le code html en un objet beautifulsoup pour le traiter facilement
soup_idele = BeautifulSoup(driver.page_source,'html.parser')
# lister les éléments des balises article de class:"article-vertical sectionAllEmplois-article", 1 élément = une offre
offres=soup_idele.find_all('article', {'class':'article-vertical sectionAllEmplois-article'})


# ya plus qu'à, maintenant c'est facile
for offre in offres:
    titre = offre.find('div', {'class':'article-vertical__title sectionAllEmplois-article__title'}).getText()
    contrat = offre.find('div', {'class':'article-vertical__contrat sectionAllEmplois-article__contrat'}).getText()
    motif = re.compile("\\n|  ")
    contrat = str(re.sub(motif, "", contrat))   
    synthese = offre.find('div', {'class':'article-vertical__resume sectionAllEmplois-article__resume'}).getText()
    motif = re.compile("\\n|  ")
    synthese = str(re.sub(motif, "", synthese))
    # lien pour aller sur l'offre
    href_offre = offre.find('a').get('href')
    href_finale = 'https://idele.fr' + href_offre
    # on va sur le lien prendre le lieu du poste
    lieu_page = requests.get(href_finale)
    # objet BeautifulSoup, page html complète
    soup_lieu=BeautifulSoup(lieu_page.text,'html.parser')
    lieu = soup_lieu.find('div', {'class':'recrutement-item__lieu'}).getText()
    motif = re.compile("\\n|  ")
    lieu = str(re.sub(motif, "", lieu)) 
    # date où l'offre à été posté
    date_depot_offre = soup_lieu.find('span', {'class':'page-publication__date'}).find('time').getText()
    motif = re.compile("\\n|  ")
    date_depot_offre = str(re.sub(motif, "", date_depot_offre))     
    # debut emploi   
    try:
        debut_emploi = soup_lieu.find('div', {'class':'recrutement-item__debut'}).getText()
    except:
        debut_emploi='' 
    # ID
    ID = organisme+"_"+titre
    ID= ' '.join(ID.split())
    motif = re.compile(' ')
    ID = str(re.sub(motif, "_", ID)) 
    # on enregistre les infos
    offres_emploi = offres_emploi.append({'ID':ID,
                                          'Organisme':organisme,
                                          'Titre':titre,
                                          'Lieu':lieu,
                                          'Type_contrat':contrat,
                                          'Debut_emploi':debut_emploi,
                                          'Limite_date_cv' : '',
                                          'Date_depot_offre': date_depot_offre,
                                          'Synthese' : synthese,
                                          'URL_offre' : href_finale}, 
                                          ignore_index=True
                                          )    


driver.quit()


#==============================================================================================
# WEB SCRAPING CONNEXION ID MDP================================================================
#==============================================================================================

# organisme
organisme='APECITA'

# on lance le driver
driver = configure_firefox_driver()

# authentification sur la page de connexion
#url = 'https://emploi.apecita.com/front-identifier.html'
#apecita_auth = driver.get(url)

#==================================================================================================
# Tkinter demande identifiant et mdp
# on entre les 2 infos et la boîte se ferme si ça marche

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
    # on récupère les infos
    username_info = username_entry.get()
    print(username_info)
    password_info = password_entry.get()
    print(password_info) 
    
    # exécuter selenium
    url = 'https://emploi.apecita.com/front-identifier.html'
    apecita_auth = driver.get(url)
    
    # voir si pas déjà connecté
    try:
        driver.find_element_by_xpath("//i[@class='fas fa-power-off']")
        connexion_apecita = 'already_log_in'
    except:
        connexion_apecita = 'not_logged_in'
    print(connexion_apecita)
    
    if connexion_apecita == 'already_log_in':
        infos='Déjà connecté, cliquer sur le bouton Quit'
    else:
        # XPATH RELATIF
        login = driver.find_element_by_xpath("//input[@class='form-control' and @name='pseudo']").send_keys(username_info)
        password = driver.find_element_by_xpath("//input[@name='mot_de_passe']").send_keys(password_info)
        submit = driver.find_element_by_xpath("//input[@class='btn btn-lg btn-apecita']").click()
        # page des offres
        url_offres = 'https://emploi.apecita.com/front-offres.html'
        apecita_offres = driver.get(url_offres)
        print(driver.page_source)
        # on test si ça marche
        try:
            driver.find_element_by_xpath("//span[@class='select2-selection__arrow']").click()
            print('connexion réussie')
            connexion = 'ok'
        except:
            print('mdp erroné, try again...')
            connexion = 'error'
        
        if connexion=='ok':
            infos='Connexion établie, cliquer sur le bouton Quit'
    #        global var_glob
    #        var_glob=username_entry.get()
    
        else:
            infos='Mdp erroné'
    
    # texte à afficher dans la console graphique
    infos_label['text'] = infos  


def action_quit_button():
    global var_glob
    var_glob='ok'
    root.destroy()

def action_quit_button_no_pwd():
    global var_glob
    var_glob='pass'
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
infos_label = ttk.Label(root, text = "En attente de vos identifiants...\nSi pas d'identifiant cliquez sur le bouton Quit_no_pwd")
infos_label.grid(column=0, row=3, columnspan=2, sticky=tk.W, padx=5, pady=5)

# Quit 
quit_button = ttk.Button(root, text="Quit", command=action_quit_button)
quit_button.grid(column=1, row=4, sticky=tk.E, padx=5, pady=5)

# Quit no pwd 
quit_button = ttk.Button(root, text="Quit_no_pwd", command=action_quit_button_no_pwd)
quit_button.grid(column=0, row=4, sticky=tk.E, padx=5, pady=5)

root.mainloop()
#print(var_glob)

# fin de Tkinter
#=================================================================================================

# test
# exécuter selenium
# driver = configure_firefox_driver()
# url = 'https://emploi.apecita.com/front-identifier.html'
# apecita_auth = driver.get(url)
# print(driver.page_source)

# try:
#     driver.find_element_by_xpath("//i[@class='fas fa-power-off']")
#     connexion_apecita = 'already_log_in'
# except:
#     connexion_apecita = 'not_logged_in'
# print(connexion_apecita)
# username_info = 'amaurypaget@gmail.com'
# password_info = ''
# login = driver.find_element_by_xpath("//input[@class='form-control' and @name='pseudo']").send_keys(username_info)
# password = driver.find_element_by_xpath("//input[@name='mot_de_passe']").send_keys(password_info)
# submit = driver.find_element_by_xpath("//input[@class='btn btn-lg btn-apecita']").click()


# XPATH RELATIF
print(var_glob)

if var_glob!='pass':
    print('on continue !')
else:
    print('Pas de connexion pour l\'Apecita')


if var_glob!='pass':
    # page des offres
    url_offres = 'https://emploi.apecita.com/front-offres.html'
    driver.get(url_offres)
    print(driver.page_source)
    
    try:
        element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='afficher-plus']"))
        )
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")

    
#==============================================================================       
    # SI BESOIN DE SELECTIONNER UNE REGION UN JOUR

    # cliquer sur le bouton du menu déroulant (1er élément de class 'select2-selection__arrow')
    # driver.find_element_by_xpath("(//span[@class='select2-selection__arrow'])[1]").click()

    # menu déroulant
    # <li class="select2-results__option" id="select2-id_localisation_1-result-noh8-49" title="Hauts-De-France" role="treeitem" aria-selected="false">Hauts-De-France</li>
    # <li class="select2-results__option" id="select2-id_localisation_1-result-n1y6-14" title="Bourgogne-Franche-Comté" role="treeitem" aria-selected="false">Bourgogne-Franche-Comté</li>
    # <li class="select2-results__option" id="select2-id_localisation_1-result-k7w1-38" title="Grand-Est" role="treeitem" aria-selected="false">Grand-Est</li>
    # <li class="select2-results__option" id="select2-id_localisation_1-result-yobd-28" title="Centre-Val-de-Loire" role="treeitem" aria-selected="false">Centre-Val-de-Loire</li>   
    
    # choisir la région et lancer la recherche
    # driver.find_element_by_xpath("//li[@class='select2-results__option' and @title='Hauts-De-France']").click()
    # driver.find_element_by_xpath("//button[@class='btn btn-primary']").click()
    
    # print(driver.page_source)
    
#==============================================================================    
    
    # filtre des offres
    # cliquer sur le bouton du menu déroulant
    #driver.find_element_by_xpath("//span[@class='select2-selection__arrow']").click()
    # mot_cle = driver.find_element_by_xpath("//input[@id='mots_cles']").send_keys("expérimentation")
    # mots clés + cliquer sur "afficher plus"
    driver.find_element_by_xpath("//div[@id='afficher-plus']").click()
    
    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[1]/div/div/div/div[1]/form/div[5]/div[1]/div/span/span[1]/span/span[2]"))
        )
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")
        
    
    # on clique sur le plus de "Métiers"
    driver.find_element_by_xpath("(//span[@class='select2-selection__arrow'])[4]").click()    
    # moins intéressant ==> driver.find_element_by_xpath("/html/body/div/div[1]/div/div/div/div[1]/form/div[5]/div[1]/div/span/span[1]/span/span[2]").click()
      
    # on clique sur "RECHERCHER"
    # driver.find_element_by_xpath("//input[@class='select2-search__field' and @type='search']").send_keys("METIERS DE LA RECHERCHE, DE L'EXPERIMENTATION, DE L'ETUDE ET DE LA CONCEPTION")    
    # bof : driver.find_element_by_xpath('/html/body/span/span/span[1]/input').send_keys("METIERS DE LA RECHERCHE, DE L'EXPERIMENTATION, DE L'ETUDE ET DE LA CONCEPTION")
    # marche pas, pas normal, driver.find_element_by_xpath("//*[@title=\"'METIERS DE LA RECHERCHE, DE L'EXPERIMENTATION, DE L'ETUDE ET DE LA CONCEPTION'\"]")
    driver.find_element_by_xpath("(//li[@class='select2-results__option'])[9]").click()
    driver.find_element_by_xpath("//button[@class='btn btn-primary']").click()
    print(driver.page_source)     
    
    # print(driver.page_source)
    
    # on attend 5 secondes, page parfois longue à charger
    time.sleep(2)
    
    # list des offres
    # offers = driver.find_element_by_xpath("//div[@class='job-item-main']")
    # offers_bis=driver.find_element_by_class_name("job-item-main")
    # offers_ter=driver.find_element_by_class_name("job-item")
    
    # on récupère le contenu html et on décortique les offres
    soup_apecita = BeautifulSoup(driver.page_source,'html.parser')
    # lister les éléments des balises div de class:"offre row", 1 élément = une offre
    offres = soup_apecita.find_all('div', {'class':['job-item ','job-item','job-item job-item-perso','job-item job-item-premium']})
    
    for offre in offres:
        # offre=offres[1]
        # on récupère le titre
        titre = offre.find('p', {'class':'job-item-title'}).getText()
        motif = re.compile("^ \\W")
        titre = str(re.sub(motif, "", titre)) 
        print(titre)
        # on récupère le lieu
        lieu = offre.find('span', {'class':'job-location'}).getText()
        motif = re.compile("[^\w ]")
        lieu = str(re.sub(motif, "", lieu))
        print(lieu)
        # type de contrat
        contrat = offre.find('span', {'class':'label'}).getText()
        motif = re.compile("[^\w ]")
        contrat = str(re.sub(motif, "", contrat))
        print(contrat) 
        # date de publi de l'offre
        Date_depot_offre = offre.find('time', {'class':'date'}).getText()
        motif = re.compile("[^\w -]")
        Date_depot_offre = str(re.sub(motif, "", Date_depot_offre))
        print(Date_depot_offre)
        # trouver l'organisme dans le logo
        try:
            organisme=offre.find('div', {'class':'offers-list-item-logo'})
            organisme=organisme.find('img').get('alt')
        except:
            organisme='APECITA'
        # aller sur le lien
        href_offre = offre.find('a').get('href')    
        href_finale = 'https://emploi.apecita.com/' + href_offre
        print(href_finale)
        # on y va !
        offre_detail = driver.get(href_finale)
        soup_offre_temp = BeautifulSoup(driver.page_source,'html.parser')
        # entreprise
        try:
            organisme = soup_offre_temp.find('p', {'class':'job-detail-enterprise-name'}).getText()
        except:
            print("nom de l'organisme non trouvable")
        if organisme==None:
            organisme='APECITA'
        synthese = soup_offre_temp.find('div', {'class':'col-md-8'}).find('p').getText()
        motif = re.compile("[^\w -/]")
        synthese = str(re.sub(motif, "", synthese))
        print(synthese)
        # ID
        ID = organisme+"_"+titre
        ID= ' '.join(ID.split())
        motif = re.compile(' ')
        ID = str(re.sub(motif, "_", ID)) 
        # on enregistre les infos
        offres_emploi = offres_emploi.append({'ID':ID,
                                              'Organisme':organisme,
                                              'Titre':titre,
                                              'Lieu':lieu,
                                              'Type_contrat':contrat,
                                              'Debut_emploi':'',
                                              'Limite_date_cv' : '',
                                              'Date_depot_offre': Date_depot_offre ,
                                              'Synthese' : synthese,
                                              'URL_offre' : href_finale}, 
                                              ignore_index=True
                                              ) 

driver.quit()

#======================================================================================
# VIVESCIA
# https://www.vivescia.com/envie-de-nous-rejoindre/nous-rejoindre

# organisme
organisme='VIVESCIA'


urlpage ='https://www.vivescia.com/envie-de-nous-rejoindre/nous-rejoindre'
page_vivescia = requests.get(urlpage, headers=headers)

if page_vivescia.status_code==200:  
    
    # on lance le driver
    driver = configure_firefox_driver()
    
    # authentification sur la page de connexion
    url = 'https://www.vivescia.com/envie-de-nous-rejoindre/nous-rejoindre'
    driver.get(url)
    
    #print(driver.page_source)
    
    try:
        myElem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/section/div[1]/section/div/div[3]/div/div[2]/div[1]/div/div/div/form/div/div[1]/div/div[1]/div[1]')))
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")
    
    driver.find_element_by_xpath("/html/body/div[2]/div/section/div[1]/section/div/div[3]/div/div[2]/div[1]/div/div/div/form/div/div[1]/div/div[1]/div[1]").click()
    
    
    try:
        myElem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/section/div[1]/section/div/div[3]/div/div[2]/div[1]/div/div/div/form/div/div[1]/div/div[2]/ul/li[2]')))
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")
    
    # filtre des offres
    driver.find_element_by_xpath("/html/body/div[2]/div/section/div[1]/section/div/div[3]/div/div[2]/div[1]/div/div/div/form/div/div[1]/div/div[2]/ul/li[2]").click()
    
    # on attend 5 secondes
    time.sleep(5)
    # on vérifie que le filtre soit bon
    filtre = str(driver.find_element_by_xpath("/html/body/div[2]/div/section/div[1]/section/div/div[3]/div/div[2]/div[1]/div/div/div/form/div/div[1]/div/div[1]/div[1]").text)
    
    if filtre=='2 SEMAINES':
        print('Filtre : ok !')
    else:
        print('Filtre non pris en compte')
    
    time.sleep(5)
    
    soup_vivescia = BeautifulSoup(driver.page_source,'html.parser')
    # lister les éléments des balises div de class:"offre row", 1 élément = une offre
    offres = soup_vivescia.find('tbody').find_all('tr')
    
    for offre in offres:
        details=offre.find_all('td')
        # date de pot offre
        date_publication = str(details[0].getText())
        # titre de l'offre
        titre = str(details[2].getText())
        print(titre)
        # type de contrat : CDD CDI etc
        contrat = str(details[3].getText())
        # lieu de l'offre
        lieu = str(details[4].getText())
        # url de l'offre en détails
        href_offre = str(details[5].find('a').get('href'))
        href_finale = 'https://www.vivescia.com' + href_offre
        # on change de page
        lieu_page = requests.get(href_finale)
        # objet BeautifulSoup, page html complète
        soup_lieu=BeautifulSoup(lieu_page.text,'html.parser')
        try:
            synthese = soup_lieu.find('div', {'class':'field-name-field-description field-type-text-long'}).find_all('div')[1].find('p').getText()
        except:
            synthese = 'pas de synthese'
        # ID
        ID = organisme+"_"+titre
        ID= ' '.join(ID.split())
        motif = re.compile(' ')
        ID = str(re.sub(motif, "_", ID)) 
        # on enregistre les infos
        offres_emploi = offres_emploi.append({'ID':ID,
                                              'Organisme':organisme,
                                              'Titre':titre,
                                              'Lieu':lieu,
                                              'Type_contrat':contrat,
                                              'Debut_emploi':'',
                                              'Limite_date_cv' : '',
                                              'Date_depot_offre': date_publication,
                                              'Synthese' : synthese,
                                              'URL_offre' : href_finale}, 
                                              ignore_index=True
                                              ) 
    
    driver.quit()

else:
        print('Le code de statut d\'erreur de réponse HTTP est : ', page_vivescia.status_code)

#=================================================================
# IN VIVO
# https://www.invivo-group.com/fr/candidats

#==============================================================================================
# Gestion du csv ==============================================================================
#==============================================================================================

#chemin absolu
#path_csv = 'C:/Users/amaur/Documents/GitHub/JunkiesMessenger/web_scrapping/tableaux_recap'

# initialiser un csv vide si première fois que le script est lancé ===========================
offres_emploi_init = pd.DataFrame(columns=['ID',
                                           'Organisme',
                                           'Titre',
                                           'Lieu',
                                           'Type_contrat',
                                           'Debut_emploi',
                                           'Limite_date_cv',
                                           'Date_depot_offre',
                                           'Synthese',
                                           'URL_offre']
                                      )

# path fichier de synthese
csv_synthese = '_offres_emploi_synthese.csv'
path_csv_synthese = pathlib.Path(path_csv, csv_synthese)

# verif son existence
if pathlib.Path.is_file(path_csv_synthese)==False:
    offres_emploi_init.to_csv(path_csv_synthese, encoding='utf-8-sig', sep=';', decimal='.', index=False)


# ouvrir le fichier de synthèse (vide si 1ère fois, sinon csv non vide des dernières fois) ====
offres_emploi_synthese = pd.read_csv(path_csv_synthese, sep=';', decimal='.')
# lister les colonnes
list_colonnes=list(offres_emploi_synthese.columns)

# 2 actions à faire :
#    1. comparer le fichier ouvert avec le dataframe créer par le script et voir s'il y a des
#       différences : si oui il y a de nouvelles offres !
#    2. fusionner les 2 fichiers (lignes en communs + nouvelles lignes) et l'enregistrer à 
#       nouveau (à jour donc)

# nettoyage dtypes ==============================================================================
for colonne in list_colonnes:
    if offres_emploi_synthese[colonne].dtypes!='object':
        offres_emploi_synthese=offres_emploi_synthese.astype({colonne : 'object'})


# concaténation pour la mise à jour =============================================================
# on vérifie si ya pas doublon même si normalement non
offres_emploi.drop_duplicates(subset="ID", keep='first', inplace=True)

offres_emploi_synthese_concat = pd.merge(offres_emploi_synthese, offres_emploi,
                                         on=list_colonnes,
                                         how='outer')
# elimination des doublons
offres_emploi_synthese_concat.drop_duplicates(subset="ID", keep='first', inplace=True)
# enregistrement du fichier
offres_emploi_synthese_concat.to_csv(path_csv_synthese, encoding='utf-8-sig', sep=';', decimal='.', index=False)




    

#test = offres_emploi.merge(offres_emploi_synthese,
#                           on=list_colonnes,
#                           how='outer',
#                           suffixes=['', '_'],
#                           indicator=True)
# ne garder que les lignes nouvelles (offres jamais parues avant) ==========================
# si besoin de prendre les lignes uniques aux 2 dataframes :
# unique_vals = df1[~df1.Star_ID.isin(df2.Star_ID)].append(df2[~df2.Star_ID.isin(df1.Star_ID)], ignore_index=True)    
offres_du_jour = offres_emploi[~offres_emploi.ID.isin(offres_emploi_synthese.ID)].dropna()
# nouvelle 


# chaine de texte avec la date du jour pour personnaliser le fichier de nouvelles offres
date = datetime.datetime.now()
list_date=[]
list_date.append(str(date.year))
list_date.append(str(date.month))
list_date.append(str(date.day))
date_csv = "-".join(list_date)

csv_du_jour=date_csv+'_offres_emploi.csv'

path_csv_offre_jour = pathlib.Path(path_csv, csv_du_jour)
offres_du_jour.to_csv(path_csv_offre_jour, encoding='utf-8-sig', sep=';', decimal='.', index=False)



