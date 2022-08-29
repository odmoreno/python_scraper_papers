from requests import get
from os import path, getcwd, makedirs
from bs4 import BeautifulSoup as soup
import csv
import json
import time
from selenium import webdriver
from unidecode import unidecode
from webdriver_manager.chrome import ChromeDriverManager

class Asambleistas2:

    def __init__(self):
        self.oriurl = "https://observatoriolegislativo.ec/"
        self.pleno2_url = "https://observatoriolegislativo.ec/asamblea-nacional/asambleistas/"
        self.baseUrl = "https://observatoriolegislativo.ec/composicion/asambleistas/"
        self.redes = []
        self.asambleistas = []
        self.currentlink = ''
        self.check = {}
        self.basefolder = "Periodo_3/"

    def obj_dict(self, obj):
        return obj.__dict__

    def get_page(self, url):
        #req = get(url, verify=False)
        browser = webdriver.PhantomJS(executable_path= "C:/Users/oscar/Downloads/phantomjs-2.1.1-windows/bin/phantomjs.exe")
        browser.get(url)
        time.sleep(5)
        html = browser.page_source
        return html

    def get_page2(self,url):
        browser = webdriver.PhantomJS(executable_path="C:/Users/oscar/Downloads/phantomjs-2.1.1-windows/bin/phantomjs.exe")
        browser.get(url)
        time.sleep(60)
        html = browser.page_source
        return html

    def get_page3(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        #driver = webdriver.Chrome("C:/Users/oscar/Downloads/chromedriver_win32/chromedriver.exe", chrome_options=options)
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        driver.get(url)
        html = driver.page_source
        return  html

    def get_all_links(self, html):
        bs = soup(html, 'html.parser')  # MISSING 'html.parser'
        #print(bs.prettify())
        links2 = bs.find(id='tblasambleistas').find('tbody').findAll('tr')
        table3 = bs.find(id='tblasambleistas')
        table44 = bs.find(id='tblasambleistas').find('tbody')
        #print(links2.prettify())
        #print('test')
        return links2

    def get_links_to_nav(self):
        html = self.get_page3(self.pleno2_url)
        links = self.get_all_links(html)
        return links


    def get_info_asambleista(self, link):
        self.currentlink = link
        votos = '/?q=ajax#panel1'
        finallink = link + votos
        html2 = self.get_page3(finallink)
        bs2 = soup(html2, 'html.parser')
        #print(bs2.prettify())
        #votaciones2 = bs2.find(id="graficos-detalle row").findAll('tspan')

        asistencias = '' #votaciones2[6].text
        ausencias = ''#votaciones2[7].text
        suplente = ''#votaciones2[8].text

        panel5 = '/?q=ajax#panel5' #Link para cargar suplentes
        linkpanel = link + panel5
        print("linkpanel", linkpanel)

        html3 = self.get_page3(linkpanel)
        bs3 = soup(html3, 'html.parser')
        #print(bs3.prettify())
        #info = bs3.find(class_="info_contacto row datos_equipo").findAll(class_="dato_equipo")
        #tablas = bs3.findAll(class_="comision")
        #pLey = bs3.find(class_="comision").findAll('tr')
        #pLey = pLey[0].text.strip()

        email = ''#info[0].contents[3].text
        blog = ''#info[1].contents[3].text
        twitter = ''#info[2].contents[3].attrs['href']
        fono = ''#info[3].contents[3].text

        if email == "":
            email = "nan"
        if blog == "":
            blog = "nan"
        if twitter == "":
            twitter = "nan"
        if fono == "":
            fono = "nan"


        suplenteinfo = bs3.find(class_="suplente").find(class_="nombreasistente")
        suplenteinfo2 = suplenteinfo.text[9:].strip()

        suplentes = []

        if suplenteinfo2 == "":
            suplenteinfo2 ="nan"
        else:
            suplenteName = suplenteinfo2.split(',')

            if len(suplenteName)> 1:
                print('Tiene mas de 1 suplente')
                suplentes.append((suplenteName))
            else:
                suplentes.append(suplenteinfo2)

        #NavigableString
        #proLey = tablas[0].contents #proyectos de ley
        #obsLey = tablas[1].contents #observaciones de ley
        #solLey = tablas[1].contents #solicitudes de informacion

        html = self.get_page(link)
        bs = soup(html, 'html.parser')
        #print(bs.prettify())
        infotabla = bs.find(class_="table asambleista_tabla").find('tbody').findAll('tr')

        comisiones= infotabla[4].contents
        com = comisiones[3].contents  ## revisar si tiene mas de 1 elemento, si tiene mas significa que tiene 2 comisiones mas  validar

        comisions = []

        if len(com) > 1:
            print('tiene mas de 2 comisiones')
            com1 = com[0]
            com2 = com[2]
            comision1 = {
                'comision': com1,
                'rol': 'Integrante'
            }
            comision2 = {
                'comision': com2,
                'rol': 'Integrante'
            }

            print(com1 + ' | ' + com2)
            comisions.append(comision1)
            comisions.append(comision2)
        else:
            print('Tiene una comision')
            com1 = com[0]
            comision1 = {
                'comision': com1,
                'rol': 'Integrante'
            }
            comisions.append(comision1)

        print('test')
        return comisions, asistencias, ausencias, suplente, email, blog, twitter, fono, suplentes

    def get_json(self):

        file = self.basefolder + 'asambleistas_3.json'
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.asambleistas, f, ensure_ascii=False, default=self.obj_dict, indent=2)


    def get_all_asambleistas(self):
        links = self.get_links_to_nav()
        for link in links:
            content = link.contents

            nombre = content[0].contents[0].attrs['title']
            test = unidecode(nombre).lower().strip()

            test2 = ' '.join(test.split())
            print(test2)
            nameurl = test2.replace(' ', '-')

            prov = content[2].text
            tipo = content[3].text
            partido = content[1].contents[0].attrs['title']

            dir = self.baseUrl + nameurl
            print(dir)
            print(nombre +' | '+ partido +' | '+ prov +' | '+ tipo)

            comisiones, asistencias, ausencias, suplente, email, blog, twitter, fono, suplentes = self.get_info_asambleista(dir)

            asambleista = {
                #'dir': dir,
                'nombre': nombre,
                'tipo': tipo,
                #'organizacion politica': partido,
                'provincia': prov,
                'partido': partido,
                #'genero': 'Masculino',
                #'profesion': 'nan',
                #'telefono': fono,
                #'blog': blog,
                'suplente': suplentes,
                #'proyectos de ley presentados': 'nan',
                #'observaciones a proyectos de ley': '0',
                #'pedidos de informacion': 'nan',
                #'redes': [{
                #    'email': email,
                #    'twitter': twitter,
                #}],
                #'votaciones': {
                #    'asistencias': asistencias,
                #    'suplentes': suplente,
                #    'ausencias': ausencias
                #},
                #'comisiones': comisiones
            }
            print(asambleista)
            self.asambleistas.append(asambleista)
        self.get_json()
        print('test')


if __name__ == '__main__':
  client = Asambleistas2()
  client.get_all_asambleistas()