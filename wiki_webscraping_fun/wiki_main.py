# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 23:43:40 2021

@author: amaur
"""


#==============================================================================================
# Modules/Packages à importer =================================================================
#==============================================================================================

import requests
from bs4 import BeautifulSoup
import random
import sys
import re

#==============================================================================================
# WEB SCRAPING SIMPLE, page accessible et sans javascript =====================================
#==============================================================================================

# fonction qui récupère tout les liens d'une page wiki dans son bodyContent et en choisi un au hasard
def shuffleWikiLink(page_web):
    # on récupère tous les liens dans le bodyContent (sinon on a les liens vers l'aide, etc)
    allLinks = page_web.find('div', {'id':"bodyContent"}).find_all("a")
    list_url = []
    for link in allLinks:
        url = str(link.get('href'))
        motif = re.compile('/wiki/')
        url_test = motif.match(url)
        if url_test:
            # double point = pas bien
            motif = re.compile(":")
            double_point = motif.findall(url)
            # mais "Portail:" = bien
            motif = re.compile("Portail:")
            portail = motif.findall(url)
            # on test les conditions
            if (double_point == []) or (double_point != [] and portail != []):
                if url not in list_url:
                    list_url.append(url)
    
     # on mélange tout ça
    random.shuffle(list_url)
     
    # on prend un lien vers une page wikiau hasard (inutile car shuffle avant mais ça fait double aléatoire et voilà)
    nb_url = len(list_url)
    nb_alea =  random.randrange(0, nb_url)
    next_url = str(list_url[nb_alea])

    # on construit l'url finale
    url_wiki = "https://fr.wikipedia.org" + next_url  
 
    # on retourne 2 infos
    return list_url, url_wiki



# nombre de page à visiter
nb_visite = 20

# Le jeu consiste à partir d'une page web :
url_wiki = "https://fr.wikipedia.org/wiki/Agriculture"

# on test le premier lien
page_wiki = requests.get(url_wiki)
print(page_wiki.status_code)
script_issue = "ok"

if (page_wiki.status_code!=200):
    print("Le lien de départ n'est pas bon")
    script_issue = 'stop'

if script_issue=='ok':

    for i in range(nb_visite):
        print(i)
        print(url_wiki)
        # On va sur le lien choisi    
        page_wiki = requests.get(url_wiki) # , timeout=2
        print(page_wiki.status_code)
        
        soup_wiki = BeautifulSoup(page_wiki.content, 'html.parser')
        # titre de la page
        title = soup_wiki.find('h1', {'id':"firstHeading"}).getText()
        print(title)
            
        # on récupère la liste des liens et u lien wiki choisi au hasard
        result = shuffleWikiLink(soup_wiki)
        list_url = result[0]
        url_wiki = result[1]
        
        while requests.get(url_wiki).status_code!=200:
            result = shuffleWikiLink(soup_wiki)
            list_url = list(result[0])
            url_wiki = str(result[1])


# HTTPSConnectionPool(host='fr.wikipedia.org', port=443): 
# Max retries exceeded with url: /wiki/Portail:France_au_XIXe_si%C3%A8cle/Index_th%C3%A9matique 
# (Caused by ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x0000023C31AF7370>,
# 'Connection to fr.wikipedia.org timed out. (connect timeout=2)'))


    