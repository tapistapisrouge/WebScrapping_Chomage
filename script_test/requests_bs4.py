# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 14:16:20 2021

@author: amaur
"""


#==============================================================================================
# Modules/Packages à importer ===============================================================
#==============================================================================================

import re
import pandas as pd
import pathlib # pour gérer les chemins
import datetime

# requests ==> pour faire les requêtes web et chopper les pages sont format html
import requests
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession # gestion javascript
# bs4 ==> transformer les pages en objet soup et chercher rapidement les infos voulues des différentes balises
from bs4 import BeautifulSoup



#from Selenium import webdriver

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
# Dataframe de base ===========================================================================
#==============================================================================================

# créer dataframe qui stockera les données du script lancé un jour X
offres_emploi = pd.DataFrame(columns=['Organisme',
                                       'Titre',
                                       'Lieu',
                                       'Type_contrat',
                                       'Debut_emploi',
                                       'Limite_date_cv',
                                       'Date_depot_offre',
                                       'Synthese'])


#==============================================================================================
# Chemin absolu à modifier si changement de dossier ou de pc===================================
#==============================================================================================
path_project='C:/Users/amaur/Documents/GitHub/JunkiesMessenger/web_scrapping'

path_pdf=pathlib.Path(path_project, 'arvalis_pdf')
print(path_pdf)

path_csv = pathlib.Path(path_project, 'tableaux_recap')
print(path_csv )

#==============================================================================================
# WEB SCRAPING SIMPLE, page accessible et sans javascript =====================================
#==============================================================================================

#=================================================================
# Exemple 1 ==> ARVALIS
organisme='Arvalis'

# On crée une session (pas forcément utile ici), ce qui permet d'avoir les cookies de session sur chaque requête
with requests.Session() as arvalis_session:
    # l'url voulu
    urlpage ='https://www.arvalisinstitutduvegetal.fr/emplois-et-stages-@/view-1319-category.html'
    # on choppe la page (différentes méthodes sur l'objet page_arvalis : cookies, headers, url, text, content, etc)   
    page_arvalis=arvalis_session.get(urlpage)
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
        # téléchargement du pdf de l'offre et enregistrement sur le pc
        # titre sans espace pour le nom du pdf qu'on va télécharger et enregistrer
        motif = re.compile("\\W")
        titre=str(re.sub(motif, "", titre)) 
        # récup de l'url de l'offre en pdf 
        href_offre = offre.find('a', {'class':'btn btn-default btn2 pull-left'}).get('href')
        href_finale = 'https://www.arvalisinstitutduvegetal.fr' + href_offre
        #offre_finale=urllib.request.urlretrieve(href_finale, "st-intro.pdf")                                           
        r = arvalis_session.get(href_finale, stream=True)
        #chemin absolu du stockage des pdf
        #path_pdf = 'C:/Users/amaur/Documents/GitHub/JunkiesMessenger/web_scrapping/arvalis_pdf'
        name_pdf = titre + '.pdf'
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


#=================================================================
# Exemple 2 ==> TERRES INOVIA, comme ARVALIS, pas de souis particulier
organisme='Terres Inovia'


# Session
with requests.Session() as inovia_session:
    urlpage ='https://www.terresinovia.fr/web/institutionnel/recrutement'  
    page_inovia = inovia_session.get(urlpage)
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



#==============================================================================================
# WEB SCRAPING JAVASCRIPT =====================================================================
#==============================================================================================

#=================================================================
# IDELE PROBLEME JAVASCRIPT : résolu
organisme='Idele'
urlpage ='https://idele.fr' 
urlpage_offres ='https://idele.fr/recrutement' 

# Session pb = Cannot use HTMLSession within an existing event loop. Use AsyncHTMLSession instead.
#idele_session = HTMLSession()
#page_idele = idele_session.get(urlpage)  
#print(dir(page_idele)) # voir toutes les méthodes applicables
#page_idele.html.render() # this call executes the js in the page
#page_idele_offres = idele_session.get(urlpage_offres)

# solution qui marche pour générer le javascript et chopper le résultat html
asession = AsyncHTMLSession()
# r = await asession.get(urlpage_offres) 
r = await asession.get(urlpage_offres)
#await r.html.arender()
page_idele_offres=r.html.raw_html
page_idele_offres=r.html.html

# objet BeautifulSoup, page html complète
soup_idele=BeautifulSoup(page_idele_offres,'html.parser')
print(soup_idele)   

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
    # debut emploi   
    try:
        debut_emploi = soup_lieu.find('div', {'class':'recrutement-item__debut'}).getText()
    except:
        debut_emploi=''  
    # on enregistre les infos
    offres_emploi = offres_emploi.append({'Organisme':organisme,
                                          'Titre':titre,
                                          'Lieu':lieu,
                                          'Type_contrat':contrat,
                                          'Debut_emploi':debut_emploi,
                                          'Limite_date_cv' : '',
                                          'Date_depot_offre':'',
                                          'Synthese' : synthese}, 
                                          ignore_index=True
                                          )    



#==============================================================================================
# WEB SCRAPING POST METHOD ====================================================================
#============================================================================================== 

#=================================================================
problem='unsolved'
# problem='solved'

if problem=='solved':
    # APECITA ==> méthode post pour injecter demandes
    organisme='APECITA'
    
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
    
    data_filtre = {'filtre':"1",
                   'barre': "0",
                   'id_localisation_1': "0",
                   'id_localisation_2': "0",
                   'id_secteur': "0",
                   'mots_cles': "expérimentation",
                   'famille': "0"
                   }
    
    
    # Session
    with requests.Session() as apecita_session:
        urlpage ='https://emploi.apecita.com'   
        page_apecita = apecita_session.get(urlpage, headers=headers)
        # on va sur la page d'authentification
        urlpage_auth ='https://emploi.apecita.com/front-identifier.html' 
        page_apecita = apecita_session.post(urlpage_auth, data = data_connexion, headers=headers)
        # on va sur les offres
        url_page_offres = 'https://emploi.apecita.com/front-offres.html'
        
        page_apecita = apecita_session.post(url_page_offres, data = data_connexion, headers=headers)
       
        # objet BeautifulSoup, page html complète
        soup_apecita=BeautifulSoup(page_apecita.text,'html.parser')
        print(soup_apecita)   
    
        # lister les éléments "offre row"
        offres=soup_arvalis.find_all('div', {'class':'offre row'})
    
        for offre in offres:
            # on récupère le titre
            titre = offre.find("h2", recursive=False).getText()
    
    
    #query = {'q': 'Forest', 'order': 'popular', 'min_width': '800', 'min_height': '600'}
    #req = requests.get('<a href="https://pixabay.com/en/photos/">https://pixabay.com/en/photos/</a>', params=query)   

#=================================================================
# APECITA TEMPORARY SOLUTION

organisme='APECITA'
# url page avec get déjà dans l'url des filtre de recherche voulu
urlpage ='https://www.apecita.com/offres?offer_search%5Bsector%5D=2&offer_search%5Bcontract%5D%5B%5D=2&offer_search%5Bcontract%5D%5B%5D=3&offer_search%5Blocation_filter%5D%5B%5D=110&offer_search%5Bexperience%5D%5B%5D=2&offer_search%5Bexperience%5D%5B%5D=3&offer_search%5Bremuneration%5D=&offer_search%5Bcurriculum%5D%5B%5D=6'
page_apecita = requests.get(urlpage)

# objet BeautifulSoup, page html complète
soup_apecita=BeautifulSoup(page_apecita.text,'html.parser')
print(soup_apecita)   

# infos des offres
offres = soup_apecita.find_all('div', {'class':["offers-list-item", "offers-list-item offers-list-item-highlight-1"]})

for offre in offres:
    # titre de l'offre    
    titre = offre.find('a').get('title')
    motif = re.compile("^ \\W")
    titre = str(re.sub(motif, "", titre)) 
    # lieu 
    lieu = offre.find('span', {'class':'location'}).getText()
    motif = re.compile("\\n")
    lieu = str(re.sub(motif, "", lieu)) 
    # type de contrat
    contrat = offre.find('span', {'class':'tag'}).getText()
    motif = re.compile("\\n")
    contrat = str(re.sub(motif, "", contrat))
    # organisme
    try:
        organisme=offre.find('div', {'class':'offers-list-item-logo'})
        organisme=organisme.find('img').get('alt')
    except:
        organisme='APECITA'
    # stockage données
    offres_emploi = offres_emploi.append({'Organisme':organisme,
                                          'Titre':titre,
                                          'Lieu':lieu,
                                          'Type_contrat':contrat,
                                          'Debut_emploi':'',
                                          'Limite_date_cv' : '',
                                          'Date_depot_offre':'',
                                          'Synthese' : ''}, 
                                          ignore_index=True
                                          )  



#=================================================================
# IN VIVO
# https://www.invivo-group.com/fr/candidats

#==============================================================================================
# Gestion du csv ==============================================================================
#==============================================================================================

#chemin absolu
#path_csv = 'C:/Users/amaur/Documents/GitHub/JunkiesMessenger/web_scrapping/tableaux_recap'

# initialiser un csv vide si première fois que le script est lancé ===========================
offres_emploi_init = pd.DataFrame(columns=['Organisme',
                                       'Titre',
                                       'Lieu',
                                       'Type_contrat',
                                       'Debut_emploi',
                                       'Limite_date_cv',
                                       'Date_depot_offre',
                                       'Synthese'])

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
offres_emploi_synthese_concat = pd.merge(offres_emploi_synthese, offres_emploi,
                                         on=list_colonnes,
                                         how='outer')
offres_emploi_synthese_concat.to_csv(path_csv_synthese, encoding='utf-8-sig', sep=';', decimal='.', index=False)




    

#test = offres_emploi.merge(offres_emploi_synthese,
#                           on=list_colonnes,
#                           how='outer',
#                           suffixes=['', '_'],
#                           indicator=True)

offres_du_jour = offres_emploi[~offres_emploi.isin(offres_emploi_synthese)].dropna()

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





