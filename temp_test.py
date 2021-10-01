# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:13:19 2021

@author: amaur

web scrapping
"""

#==============================================================================================
# Modules/Packages à importer ===============================================================
#==============================================================================================

import re
import pandas as pd
import pathlib # pour gérer les chemins

from bs4 import BeautifulSoup
import urllib.request
import requests
from requests_html import HTMLSession

from Selenium import webdriver

# shadow user agent
# github : https://github.com/lobstrio/shadow-useragent
# Installer sur ANACONDA =
# 1. Activate your conda environment source activate myenv
# 2. conda install git pip
# 3. pip install git+git://github.com/lobstrio/shadow-useragent
#import shadow_useragent
#ua = shadow_useragent.ShadowUserAgent()
# selection d'un user agent d'au moins 5% des utilisateurs
#my_user_agent = ua.percent(0.01)
#ua.most_common


#==============================================================================================
# URLOPEN =====================================================================================
#==============================================================================================


# créer dataframe qui stockera les données
offres_emploi = pd.DataFrame(columns=['Organisme',
                                       'Titre',
                                       'Lieu',
                                       'Type_contrat',
                                       'Debut_emploi',
                                       'Limite_date_cv',
                                       'Date_depot_offre',
                                       'Synthese'])


#=================================================================
# ARVALIS
organisme='Arvalis'
#url = "https://fr.wikipedia.org/wiki/Valdoie"
urlpage ='https://www.arvalisinstitutduvegetal.fr/emplois-et-stages-@/view-1319-category.html'

page_arvalis = urllib.request.urlopen(urlpage)
# result = <http.client.HTTPResponse at 0x1e952397790>

# objet BeautifulSoup, page html complète
soup_arvalis=BeautifulSoup(page_arvalis,'html.parser')
print(soup_arvalis)

# check urllib.error


# lister les éléments "offre row"
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
    # on met les info dans la dataframe
    offres_emploi = offres_emploi.append({'Organisme':organisme,
                                            'Titre':titre,
                                            'Lieu':lieu,
                                            'Type_contrat':contrat,
                                            'Debut_emploi':debut_emploi,
                                            'Limite_date_cv' : '',
                                            'Date_depot_offre':date_depot_offre,
                                            'Synthese' : ''}, 
                                            ignore_index=True
                                            )
offre=offres[0]

pdf_test = offre.find('div', {'col-lg-12 col-md-12 col-sm-12 col-xs-12 details-offre boutons'})
href_offre=pdf_test.find('a', {'class':'btn btn-default btn2 pull-left'}).get('href') 
href_finale='https://www.arvalisinstitutduvegetal.fr'+href_offre
offre_finale=urllib.request.urlretrieve(href_finale, "st-intro.pdf")                                           


https://www.arvalisinstitutduvegetal.fr/file/arvoffresdemploi/pj/c9/eb/d8/15/cdd_dv_im_9mois_2022_externe_vlb_vdiff1971616549679910866.pdf

                                            
#=================================================================
# IDELE
organisme='Idele'
#url = "https://fr.wikipedia.org/wiki/Valdoie"
urlpage ='https://idele.fr/recrutement'

page_idele = urllib.request.urlopen(urlpage)
# result = <http.client.HTTPResponse at 0x1e952397790>

# objet BeautifulSoup, page html complète
soup_idele=BeautifulSoup(page_idele,'html.parser')
print(soup_idele)

# lister les éléments "offre row"
offres=soup_idele.find_all('div', {'class':'article-vertical sectionAllEmplois-article'})
offres=soup_idele.find('section', {'sectionEmplois-top'})


offres=soup_idele.find_all('article', {'class':'article-vertical sectionAllEmplois-article'})


#=================================================================
# TERRES INOVIA
organisme='Terres Inovia'
#url = "https://fr.wikipedia.org/wiki/Valdoie"
urlpage ='https://www.terresinovia.fr/web/institutionnel/recrutement'

page_inovia = urllib.request.urlopen(urlpage)
# result = <http.client.HTTPResponse at 0x1e952397790>

# objet BeautifulSoup, page html complète
soup_inovia=BeautifulSoup(page_inovia,'html.parser')
print(soup_inovia)

# lister les éléments "offre row"
offres=soup_inovia.find_all('div', {'class':'col-1-2'})

for offre in offres:
    offre=offres[0]
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
    infos=offres[0].find('div', {'class':'offre-infos'}).find_all("p")
    #lieu
    lieu=infos[0].getText()
    motif = re.compile('Lieu : ')
    lieu = re.sub(motif, "", lieu)   
    contrat=infos[1].getText()
    motif = re.compile(' ')
    contrat = re.sub(motif, "", contrat)     
    # href infos supp
    href_offre=offres[0].find('div', {'class':'lien'}) 
    url_offre = href_offre.find('a').get('href')
    page_offre = urllib.request.urlopen(url_offre)
    soup_offre=BeautifulSoup(page_offre,'html.parser')
    infos=soup_offre.find('div', {'class':'offre-detail'})
    # limite depot cv
    limite_depot_cv=infos.find('div', {'class':'offre-infos'}).find_all("p")
    limite_depot_cv=limite_depot_cv[1].getText()
    motif = re.compile('Date limite de dépôt de candidature : ')
    limite_depot_cv = re.sub(motif, "", limite_depot_cv)    
    # resume
    synthese=infos.find('div', {'class':'offre-contenu'}).find_all("p")
    synthese=synthese[1].getText()
    
    #synthese = offres[1].find_all('div', {'class':'col-lg-12 col-md-12 col-sm-12 col-xs-12 details-offre'})
    # on met les info dans la dataframe
    offres_emploi = offres_emploi.append({'Organisme': organisme,
                                            'Titre': titre,
                                            'Lieu': lieu,
                                            'Type_contrat': contrat,
                                            'Debut_emploi': '',
                                            'Limite_date_cv' : limite_depot_cv,
                                            'Date_depot_offre':date_depot_offre,
                                            'Synthese' : synthese}, 
                                            ignore_index=True
                                            )




#===========================================================================================
# APECITA
organisme='Apecita'

# URL
urlpage ='https://emploi.apecita.com/front-offres.html'

# POST avec mdp et pseudo
username="amaurypaget@gmail.com"
password="A0mau1ry"
data_connexion={
                'pseudo': username,
                'mot_de_passe': password,
                }

#Pour afficher votre agent utilisateur, cliquez sur le bouton de menu de Firefox Fx57Menu 
#puis cliquez sur Aide et choisissez Plus d’informations de dépannage. 
#La page d’adresse about:support s’ouvre. 
#La section Paramètres de base de l’application affiche la version actuelle de votre installation de Firefox 
#et comprend une entrée Agent utilisateur. 
#Par exemple, l’entrée de l’agent utilisateur par défaut de Firefox 83 sur Windows 10 (64 bits) doit apparaître ainsi :
#Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0

user_agent_amaury = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0' 
headers = {
   'User-Agent': user_agent_amaury,
#    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#    'Accept-Language': 'en-US,en;q=0.5',
#    'Connection': 'keep-alive',
#    'Upgrade-Insecure-Requests': '1',
#    'Pragma': 'no-cache',
#    'Cache-Control': 'no-cache',
}


r = requests.post(urlpage, data = data_connexion, headers=headers)


soup_apecita=BeautifulSoup(r.text,'html.parser')
print(soup_apecita)



# lister les éléments "offre row"
offres=soup_apecita.find('ul', {'class':'jobs-list'}).find_all('li')





#===========================================================================================



try:
    file2 = urllib.request.Request('site goes here')
    file2.add_header("User-Agent", 'Opera/9.61 (Windows NT 5.1; U; en) Presto/2.1.1')
    ResponseData = urllib.request.urlopen(file2).read().decode("utf8", 'ignore')




urlpage ='https://emploi.apecita.com/front-identifier.html'
username="amaurypaget@gmail.com"
password="A0mau1ry"
data={
    'pseudo': username,
    'mot_de_passe': password,
}
 
with requests.Session() as s:
    url ='https://emploi.apecita.com/front-identifier.html'
    login_data={
            'pseudo': username,
            'mot_de_passe': password,
            }
    s.post(url, data=login_data)
    r=s.get('https://emploi.apecita.com/front-offres.html?page=1')
    print(r.text)

page = urlopen(url)

html_bytes = page.read()
html = html_bytes.decode("utf-8")


# PROXY
proxy = {"http":"http://username:password@proxy:port"}
r = requests.get("http://linuxfr.org/", proxies = proxy)

# DONNEES MDP PSEUDO
data = {"first_name":"Richard", "second_name":"Stallman"}
r = requests.post("http://linuxfr.org", data = data)

# COOKIES
import requests
url = 'http://www.google.com/doodles/'
r = requests.get(url)
print r.cookies

# JAVASCRIPT 
from Selenium import webdriver
driver = webdriver.PhantomJS()
driver.get(my_url)
p_element = driver.find_element_by_id(id_='intro-text')
print(p_element.text)
# result:
'Yay! Supports javascript'

#==========================================
from requests_html import HTMLSession
session = HTMLSession()

r = session.get('http://python-requests.org/')

r.html.render() # this call executes the js in the page

r.html.search('Python 2 will retire in only {months} months!')['months']

'<time>25</time>' #This is the result.



from requests_html import HTMLSession

session = HTMLSession()

r = session.get('http://www.yourjspage.com')

r.html.render()  




