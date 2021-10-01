# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 10:57:47 2021

@author: amaur


"""
# tuto
# https://www.pluralsight.com/guides/implementing-web-scraping-with-selenium
# https://www.zyte.com/blog/an-introduction-to-xpath-with-examples/
# location element selenium :
    # https://selenium-python.readthedocs.io/locating-elements.html



#==============================================================================================
# Modules/Packages à importer ===============================================================
#==============================================================================================

import re
import pandas as pd
import pathlib # pour gérer les chemins
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


#==============================================================================================
# Chemin absolu à modifier si changement de dossier ou de pc===================================
#==============================================================================================
path_project='C:/Users/amaur/Documents/GitHub/JunkiesMessenger/web_scrapping'

path_webdriver=pathlib.Path(path_project, 'webdriver')
print(path_webdriver)
path_firefox=pathlib.Path(path_webdriver, 'geckodriver.exe')
path_chrome=pathlib.Path(path_webdriver, 'chromedriver.exe')

path_csv = pathlib.Path(path_project, 'tableaux_recap')
print(path_csv )


#==============================================================================================
# Configuration des web driver ================================================================
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

# on lance le driver
driver = configure_firefox_driver()

# authentification sur la page de connexion
url = 'https://emploi.apecita.com/front-identifier.html'
apecita_auth = driver.get(url)
# user mdp
user='amaurypaget@gmail.com'
mdp='A0mau1ry'
# connexion
# XPATH :
# 1. absolu : /HTML/body/div/div[@ id = 'Email']
# 2. relatif : //img[@class=’logo’]
#              //div[@id='..' and @class='...] ==> double attribut

# XPATH ABSOLU
#login = driver.find_element_by_xpath("/html/body/div/div/div/div[2]/div[1]/form/div/div[1]/div/input").send_keys(user)
#password = driver.find_element_by_xpath("/html/body/div/div/div/div[2]/div[1]/form/div/div[2]/div/input").send_keys(mdp)
#submit = driver.find_element_by_xpath("/html/body/div/div/div/div[2]/div[1]/form/div/div[3]/div/input").click()

# XPATH RELATIF
login = driver.find_element_by_xpath("//input[@class='form-control' and @name='pseudo']").send_keys(user)
password = driver.find_element_by_xpath("//input[@name='mot_de_passe']").send_keys(mdp)
submit = driver.find_element_by_xpath("//input[@class='btn btn-lg btn-apecita']").click()

# page des offres
url_offres = 'https://emploi.apecita.com/front-offres.html'
apecita_offres = driver.get(url_offres)
print(driver.page_source)

# filtre des offres
# cliquer sur le bouton du menu déroulant
driver.find_element_by_xpath("//span[@class='select2-selection__arrow']").click()

# menu déroulant
# <li class="select2-results__option" id="select2-id_localisation_1-result-noh8-49" title="Hauts-De-France" role="treeitem" aria-selected="false">Hauts-De-France</li>
# <li class="select2-results__option" id="select2-id_localisation_1-result-n1y6-14" title="Bourgogne-Franche-Comté" role="treeitem" aria-selected="false">Bourgogne-Franche-Comté</li>
# <li class="select2-results__option" id="select2-id_localisation_1-result-k7w1-38" title="Grand-Est" role="treeitem" aria-selected="false">Grand-Est</li>
# <li class="select2-results__option" id="select2-id_localisation_1-result-yobd-28" title="Centre-Val-de-Loire" role="treeitem" aria-selected="false">Centre-Val-de-Loire</li>

# charger jusq'à ce que jv se fasse
try:
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(By.xpath, "//li[@class='select2-results__option' and @title='Hauts-De-France']")
    )
except:
    print('Element introuvable')
# ElementNotVisibleException
# )



# choisir la région et lancer la recherche
driver.find_element_by_xpath("//li[@class='select2-results__option' and @title='Hauts-De-France']").click()
driver.find_element_by_xpath("//button[@class='btn btn-primary']").click()
print(driver.page_source)


# list des offres
# offers = driver.find_element_by_xpath("//div[@class='job-item-main']")
# offers_bis=driver.find_element_by_class_name("job-item-main")
# offers_ter=driver.find_element_by_class_name("job-item")

soup_apecita = BeautifulSoup(driver.page_source,'html.parser')
# lister les éléments des balises div de class:"offre row", 1 élément = une offre
offres = soup_apecita.find_all('div', {'class':['job-item ','job-item','job-item job-item-perso','job-item job-item-premium']})

for offre in offres:
    offre=offres[1]
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
    organisme = soup_offre_temp.find('p', {'class':'job-detail-enterprise-name'})
    if organisme==None:
        organisme='APECITA'
    synthese = soup_offre_temp.find('div', {'class':'col-md-8'}).find('p').getText()
    motif = re.compile("[^\w -/]")
    synthese = str(re.sub(motif, "", synthese))
    print(synthese)





