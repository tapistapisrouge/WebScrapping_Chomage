# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 16:25:04 2021

@author: amaur
"""

#==============================================================================================
# Modules/Packages à importer ===============================================================
#==============================================================================================

import re
import pandas as pd
import pathlib # pour gérer les chemins
from datetime import datetime

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


#==============================================================================================
# Dataframe de base ===========================================================================
#==============================================================================================

# créer dataframe qui stockera les données du script temporairement
#messenger_discret = pd.DataFrame(columns=['conversation',
#                                          'message'
#                                          ])

# suivi de la convo junkies en mode discret
convo_junkies = pd.DataFrame(columns=['date',
                                      'message'
                                      ])

convo_junkies = convo_junkies.append({'date':datetime.now(),
                                      'message':'test'},
                                      ignore_index=True
                                      )
# suivi de la convo asd en mode discret
convo_asd = pd.DataFrame(columns=['date',
                                  'orateur',
                                  'message'
                                      ])

convo_asd = convo_asd.append({'date':datetime.now(),
                              'orateur':'test',
                              'message':'test'},
                             ignore_index=True
                             )

#==============================================================================================
# Facebook Time ===============================================================================
#==============================================================================================

# on lance le driver
driver = configure_firefox_driver()

# authentification sur la page de connexion
url = 'https://www.facebook.com'
facebook_auth = driver.get(url)

# user mdp
user='amaurypaget@gmail.com'
mdp='FACd8CUwTHBzV$*'

# connexion
login = driver.find_element_by_xpath("//input[@id='email']").send_keys(user)
password = driver.find_element_by_xpath("//input[@id='pass']").send_keys(mdp)
submit = driver.find_element_by_xpath("//button[@name='login']")
driver.execute_script("arguments[0].click();", submit)

print(driver.page_source)

# on va sur la page messager ==================================================================

# message ==> class="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7 ltmttdrg g0qnabr5 ojkyduve"
#             class="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7 ltmttdrg g0qnabr5 ojkyduve"
# titre convers ==> class="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7 ltmttdrg g0qnabr5"
#                   class="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7 ltmttdrg g0qnabr5" 

url_messenger='https://www.facebook.com/messages/t/'
# url_messenger='https://www.facebook.com/messages/t/1475749529205290/'
messenger_page = driver.get(url_messenger)

# all_convers = driver.find_elements_by_xpath('//div[@data-testid="mwthreadlist-item"]')
# for convers in all_convers:
#     print(convers.text)
#     title = convers.find_element_by_xpath('//span[@dir="auto"]/span/span/span').text
#     print(title)
#     message = convers.find_element_by_xpath('//span[@dir="auto"]/span/div/span/span').text
#     print(message)



#=======================================================================================
# convo junkies ========================================================================
#=======================================================================================

url_messenger='https://www.facebook.com/messages/t/'
messenger_page = driver.get(url_messenger)
messager_timer=0

while messager_timer<100000:
    # créer dataframe qui stockera les données du script temporairement
    messenger_discret = pd.DataFrame(columns=['conversation',
                                          'message'
                                          ])
    # initialisation du temps d'une boucle
    debut=datetime.now()
    # début de l'extraction
    driver.refresh()
    # attente de l'élément
    try:
        myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='mwthreadlist-item']")))
        print ("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")

    soup_messenger = BeautifulSoup(driver.page_source,'html.parser')
    # print(soup_messenger)

    conversation = soup_messenger.find('div', {'aria-label':'Discussions'}).find_all('div', {'data-testid':'mwthreadlist-item'})
    # conversation = soup_messenger.find_all('a', {'data-visualcompletion':'ignore-dynamic'})
    print('page raffraichie')
    for convers in conversation:
        test=convers.find_all('span', {'dir':'auto'})
        if test==[]:
            print('element vide')
        else:
            title=test[0].find_all('span')
            title=title[2].getText()
            print(title)  
            message=test[1].find_all('span')
            message=message[2].getText()
            print(message)
        # enregistrement des données
        messenger_discret = messenger_discret.append({'conversation':title,
                                                      'message':message},
                                                      ignore_index=True
                                                      )
        date_temp = datetime.now()
    # checker le message de la convo junkies
    message_junkies_temp = str(messenger_discret.loc[messenger_discret['conversation'] == "L'Olympiade des Connards", 'message'].iloc[0])
    # recup participant et message
    participant=message_junkies_temp.split(":")[0]
    message=message_junkies_temp.split(":")[1]
    # voir si le message est identique à celui du dataframe junkies
    length = len(convo_asd)-1
    dernier_message = convo_junkies.loc[length,'message']
    # on ajoute le message ou non
    if message != dernier_message:
        convo_junkies = convo_junkies.append({'date':date_temp,
                                              'orateur':participant,
                                              'message':message},
                                             ignore_index=True
                                             )
    else:
        print('message identique')

    messager_timer+=1
    #calcul temps d'une boucle
    fin=datetime.now()
    duration = fin - debut
    duration_in_s = duration.total_seconds()
    print(duration_in_s)
    print(messager_timer)


#=======================================================================================
# convo courbou queinec ================================================================
#=======================================================================================

url_messenger='https://www.facebook.com/messages/t/'
messenger_page = driver.get(url_messenger)
messager_timer=0

while messager_timer<100000:
    # créer dataframe qui stockera les données du script temporairement
    messenger_discret = pd.DataFrame(columns=['conversation',
                                          'message'
                                          ])
    # initialisation du temps d'une boucle
    debut=datetime.now()
    # début de l'extraction
    driver.refresh()
    # attente de l'élément
    try:
        myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='mwthreadlist-item']")))
        print ("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")
    
    
    soup_messenger = BeautifulSoup(driver.page_source,'html.parser')
    # print(soup_messenger)

    conversation = soup_messenger.find('div', {'aria-label':'Discussions'}).find_all('div', {'data-testid':'mwthreadlist-item'})
    # conversation = soup_messenger.find_all('a', {'data-visualcompletion':'ignore-dynamic'})
    print('page raffraichie')
    for convers in conversation:
        test=convers.find_all('span', {'dir':'auto'})
        if test==[]:
            print('element vide')
        else:
            title=test[0].find_all('span')
            title=title[2].getText()
            print(title)  
            message=test[1].find_all('span')
            message=message[2].getText()
            print(message)
        # enregistrement des données
        messenger_discret = messenger_discret.append({'conversation':title,
                                                      'message':message},
                                                      ignore_index=True
                                                      )
        date_temp = datetime.now()
    # checker le message de la convo junkies
    message_asd_temp = str(messenger_discret.loc[messenger_discret['conversation'] == "les auvergnats sont Des Putes", 'message'].iloc[0])
    # recup participant et message
    participant=message_asd_temp.split(":")[0]
    message=message_asd_temp.split(":")[1]
    # voir si le message est identique à celui du dataframe asd
    length = len(convo_asd)-1
    dernier_message = convo_asd.loc[length,'message']
    # on ajoute le message ou non
    if message != dernier_message:
        convo_asd = convo_asd.append({'date':date_temp,
                                      'orateur':participant,
                                      'message':message},
                                      ignore_index=True
                                      )
    else:
        print('message identique')
        
    messager_timer+=1
    #calcul temps d'une boucle
    fin=datetime.now()
    duration = fin - debut
    duration_in_s = duration.total_seconds()
    print(duration_in_s)
    print(messager_timer)


driver.quit()








# =====================================================================================================

LOGIN_URL = 'https://www.facebook.com/login.php'
 
class FacebookLogin():
    def __init__(self, email, password, browser='Chrome'):
        # Store credentials for login
        self.email = email
        self.password = password
        if browser == 'Chrome':
            # Use chrome
            self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
        elif browser == 'Firefox':
            # Set it to Firefox
            self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        self.driver.get(LOGIN_URL)
        time.sleep(1) # Wait for some time to load
 
 
 
    def login(self):
        email_element = self.driver.find_element_by_id('email')
        email_element.send_keys(self.email) # Give keyboard input
 
        password_element = self.driver.find_element_by_id('pass')
        password_element.send_keys(self.password) # Give password as input too
 
        login_button = self.driver.find_element_by_id('loginbutton')
        login_button.click() # Send mouse click
 
        time.sleep(2) # Wait for 2 seconds for the page to show up
 
 
if __name__ == '__main__':
    # Enter your login credentials here
    fb_login = FacebookLogin(email='sample@example.com', password='PASSWORD', browser='Firefox')
    fb_login.login()






