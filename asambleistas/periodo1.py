from requests import get
from os import path, getcwd, makedirs
from bs4 import BeautifulSoup as soup
import csv
import json
import re
import json


class Asambleistas1:

    def __init__(self):
        self.pleno1_url = "https://2013-2017.observatoriolegislativo.ec/asamblea-nacional/asambleistas/"
        self.baseUrl = "https://2013-2017.observatoriolegislativo.ec/"
        self.redes = []
        self.asambleistas = []
        self.danielBool = False
        self.cesarBool = False
        self.elizabetBool = False
        self.cuestaBool = False
        self.currentlink = ''
        self.check = {}
        self.basefolder = "Periodo_1/"

    def obj_dict(self, obj):
        return obj.__dict__

    def get_page(self, url):
        req = get(url, verify=False)
        if req.status_code == 200:
            return req.text
        else:
            return None
        # raise Exception('Error {0}'.format(req.status_code))

    def get_all_links(self, html):
        bs = soup(html, 'html.parser')  # MISSING 'html.parser'
        #print(bs.prettify())
        #table = bs.find(id='tblasambleistas').find('tbody')
        links2 = bs.find(id='tblasambleistas').find('tbody').findAll('tr')
        #print(links2.prettify())
        #print('test')
        return links2

    def get_links_to_nav(self):
        html = self.get_page(self.pleno1_url)
        links = self.get_all_links(html)
        return links


    def get_actividad(self, actividad):
        '''
        rcuentas = actividad[4].contents
        sizeCuentas = len(rcuentas)
        if sizeCuentas <= 7:
            info = rcuentas[3].text.replace('\n', '')
            info = info.strip()
        '''

        pley = actividad[10].text.replace('\n', '|').strip().split('|')
        pley2 = actividad[5].text.replace('\n', '|').strip().split('|')
        pley3 = actividad[6].text.replace('\n', '|').strip().split('|')

        if pley[1] == 'Proyectos de ley presentados:':
            pleyValue = pley[2].strip()
            p1 = actividad[10].contents[3].text.strip()
        elif pley2[1] == 'Proyectos de ley presentados:':
            pleyValue = pley2[2].strip()
            p1 = actividad[5].contents[3].text.strip()
        elif pley3[1] == 'Proyectos de ley presentados:':
            pleyValue = pley3[2].strip()
        else:
            pleyValue = ' '

        obsley = actividad[11].text.replace('\n', '|').strip().split('|')
        obsley2 = actividad[6].text.replace('\n', '|').strip().split('|')
        obsley3 = actividad[7].text.replace('\n', '|').strip().split('|')

        if obsley[1] == 'Observaciones a proyectos de ley:':
            obsleyValue = obsley[2].strip()
            #p2 = actividad[11].contents[3].text.strip()
        elif obsley2[1] == 'Observaciones a proyectos de ley:':
            obsleyValue = obsley2[2].strip()
        elif obsley3[1] == 'Observaciones a proyectos de ley:':
            obsleyValue = obsley3[2].strip()
        else:
            obsleyValue = ' '

        sizeA = len(list(actividad))
        if sizeA  <= 12:
            value = 11
        else:
            value = 12

        pedidos = actividad[value].text.replace('\n', '|').strip().split('|')
        pedidos2 = actividad[7].text.replace('\n', '|').strip().split('|')
        pedidos3 = actividad[8].text.replace('\n', '|').strip().split('|')

        if pedidos[1] == 'Pedidos de información:':
            pvalue = pedidos[2].strip()
        elif pedidos2[1] == 'Pedidos de información:':
            pvalue = pedidos2[2].strip()
        elif pedidos3[1] == 'Pedidos de información:':
            pvalue = pedidos3[2].strip()
        else:
            pvalue = ' '

        '''
        pleypresentados = actividad[5].contents[3].text
        obsley = actividad[6].contents[3].text
        pedidos = actividad[7].contents[3].text
        '''
        #print('text')

        if (pleyValue == 'El asambleísta no ha proporcionado información a nuestra organización' or pleyValue == 'la asambleísta no ha proporcionado información a nuestra organización'):
            pleyValue = 'nan'
        if (obsleyValue == 'El asambleísta no ha proporcionado información a nuestra organización' or obsleyValue == 'la asambleísta no ha proporcionado información a nuestra organización'):
            obsleyValue = 'nan'
        if (pvalue == 'El asambleísta no ha proporcionado información a nuestra organización' or pvalue == 'la asambleísta no ha proporcionado información a nuestra organización'):
            pvalue = 'nan'

        return pleyValue, obsleyValue, pvalue

    def get_info_asambleista(self, link):
        print(str(link))
        self.currentlink = link
        html = self.get_page(link)
        bs = soup(html, 'html.parser')
        #print(bs.prettify())
        perfil = bs.find(id="detalle_perfil").find('tbody').findAll('tr')
        genero = perfil[2].contents[3].string
        profesion = perfil[3].contents[3].string
        telefono = perfil[4].contents[3].string
        email = perfil[5].contents[3].string
        blog = perfil[6].contents[3].string
        twitter = perfil[7].contents[3].string
        suplente = perfil[8].contents[3].string

        actividad = bs.find(id="detalle_actividad").find('tbody').findAll('tr')
        proyectoley, obsley, pedidos = self.get_actividad(actividad)

        inforesto = bs.find(id="perfil").findAll(class_='comision')
        info2 = bs.find(id='perfil').select("li div.info table.comision")
        info3 = bs.find(id='perfil').select("li div.info table.comision tbody")
        proyectosLey = info2[1]
        '''
        sp = soup(html, 'lxml')
        scripts = sp.findAll("script")
        js = scripts[8]
        js2 = js.contents
        js3 = js2[0].string
        p = re.compile('var paramsGraficoVotaciones = (.{});')
        m = p.match(js3)
        #stocks = json.loads(m.groups()[0])
        '''
        #print('test')

        if (twitter == "No tiene" or twitter == "no tiene"):
            baseTwitter = "nan"
        else:
            subtwt = twitter[1:]
            baseTwitter = 'https://twitter.com/' + subtwt

        if blog == "No tiene":
            blog = "nan"

        return genero, profesion, telefono, email, blog, baseTwitter, suplente, proyectoley, obsley, pedidos

    def get_json(self):

        file = self.basefolder + 'asambleistas_1_tmp.json'
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.asambleistas, f, ensure_ascii=False, default=self.obj_dict, indent=2)


    def get_all_asambleistas(self):
        links = self.get_links_to_nav()
        for link in links:
            currentLink = link.attrs['data-href']
            content = link.contents
            nametag = content[1].contents
            name = nametag[0].attrs['title']
            orgtag = content[5].contents
            org = orgtag[0].attrs['title']
            provincia = content[7].contents[0].string
            tipo = content[9].contents[0].string

            #print(currentLink)
            #print(name +' | '+ org +' | '+ provincia +' | '+ tipo)
            dir = self.baseUrl + currentLink
            genero, profesion, telefono, email, blog, twitter, suplente, proyectoley, obsley, pedidos = self.get_info_asambleista(dir)

            asambleista = {
                'nombre': name,
                'dir': dir,
                'organizacion politica': org,
                'provincia': provincia,
                'tipo': tipo,
                'genero': genero,
                'profesion': profesion,
                'telefono': telefono,
                'blog': blog,
                'suplente': suplente,
                'proyectos de ley presentados': proyectoley,
                'observaciones a proyectos de ley': obsley,
                'pedidos de informacion': pedidos,
                'redes': [{
                    'email': email,
                    'twitter': twitter,
                }],
                'votaciones': {
                    'asistencias': 'nan',
                    'suplentes': 'nan',
                    'ausencias': 'nan'
                }
            }
            self.asambleistas.append(asambleista)

        self.get_json()
        # print('test')


if __name__ == '__main__':
  client = Asambleistas1()
  client.get_all_asambleistas()