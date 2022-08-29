from requests import get
from os import path, getcwd, makedirs
from bs4 import BeautifulSoup as soup
import csv
import json

class Asambleistas:

  def __init__(self):
    self.pleno2_url = "https://www.asambleanacional.gob.ec/es/pleno-asambleistas"
    self.baseUrl = "https://www.asambleanacional.gob.ec/es/"
    self.redes = []
    self.asambleistas = []
    self.danielBool = False
    self.cesarBool = False
    self.elizabetBool = False
    self.cuestaBool = False
    self.currentlink = ''
    self.check = {}

  def obj_dict(self, obj):
    return obj.__dict__

  def get_page(self, url):
    req = get(url)
    if req.status_code == 200:
        return req.text
    else:
      return None
    #raise Exception('Error {0}'.format(req.status_code))

  def get_all_links(self, html):
    bs = soup(html, 'html.parser')  # MISSING 'html.parser'
    #print(bs.prettify())
    links2 = bs.select("p.right strong a")
    #print('test')
    return links2

  def get_links_to_nav(self):
    html = self.get_page(self.pleno2_url)
    links = self.get_all_links(html)
    return links

  def get_info_descripcion(self, bs):
    if self.elizabetBool:
      info = None
    elif self.cuestaBool:
      info = None
    else:
      allinfo = bs.find(class_='large-8 columns').find(class_="separator").select("p")
      em = allinfo[0].select("em")
      span = allinfo[0].find("span")
      info = None
      if em and ('|' in em[0].contents[0]):
        text = em[0].contents
        info = text[0].split('|')
      elif self.danielBool:
        text2 = allinfo[0].contents
        info = text2[0].split('|')
        self.danielBool = False
      elif span and self.cesarBool:
        text = span.contents
        info = text[0].split('|')
        #self.spanBool = True
      else:
        text2 = allinfo[0].contents
        info = text2[0].split('|')

    return info

  def get_comisiones(self, informacion):
    comisiones = []
    if self.cesarBool:
      print('No tiene comisiones .. ')
      self.cesarBool = False
    elif self.elizabetBool:
      final = {'comision': 'Comisión del Desarrollo Económico, Productivo y la Microempresa', 'rol': 'Integrante'}
      comisiones.append(final)
      self.elizabetBool = False
    elif self.cuestaBool:
      final = {'comision': 'Comisión de Soberanía, Integración, Relaciones Internacionales y Seguridad Integral', 'rol': 'Integrante'}
      comisiones.append(final)
      self.cuestaBool = False
    else:
      for info in informacion:
        info = info.strip()
        tmp2 = info.split('-')
        if 'Comisión' in info:
          if len(tmp2) > 1:
            print('Mas de 2 comisiones')
            for comision in tmp2:
              tmpInfo = comision.strip().split(' ')
              rolComision = tmpInfo[0]
              new = tmpInfo[3:]
              newCom = " ".join(new)
              final = {'comision': newCom, 'rol': rolComision}
              comisiones.append(final)
          else:
            # print('Hay comision: ' + info)
            tmpInfo = info.strip().split(' ')
            rolComision = tmpInfo[0]
            new = tmpInfo[3:]
            newCom = " ".join(new)
            final = {'comision': newCom, 'rol': rolComision}
            comisiones.append(final)

    return comisiones

  def get_tipo_asambleista(self, info):
    tipo = ''
    nombre = ''
    if 'por' in info:
      print('Es asambleista de provincia o migrante')
      tmpinfo = info[16:].strip()
      if tmpinfo == 'EEUU - Canadá':
        print('Asambleista por EEUU - Canadá')
        tipo = 'Migrante'
        nombre = tmpinfo
      elif tmpinfo == 'Europa - Asia y Oceanía':
        tipo = 'Migrante'
        nombre = tmpinfo
      elif tmpinfo == 'América Latina El Caribe y África':
        tipo = 'Migrante'
        nombre = tmpinfo
      else:
        tipo = 'Provincia'
        nombre = tmpinfo
    else:
      print('Asambleista Nacional')
      tipo = 'Nacional'
      nombre = 'Ecuador'

    return tipo, nombre

  def manage_info(self, bs):
    nombre = bs.find(class_='large-4 columns').find(class_="text-right").find("h5")
    if nombre.contents:
      nombre = nombre.contents[0]
    else:
      new = self.currentlink.split('/')
      newname = new[len(new)-1]
      nombre = newname

    info = bs.find(class_='large-4 columns').find(class_="text-right").find("small")
    text = info.contents
    text = text[0].replace('\n', '|')
    infonew = text.split('|')
    #tipo = infonew[0].strip()
    #provincia = infonew[0].strip().split(' ')
    #size = len(provincia)
    #provnew = provincia[size-1]

    partido = infonew[1].strip()
    tipo, nombreTipo = self.get_tipo_asambleista(infonew[0].strip())

    if nombre == 'César Litardo':
      self.cesarBool = True
    elif nombre == 'Daniel Mendoza':
      self.danielBool = True
    elif nombre == 'Elizabeth Cabezas G.':
      self.elizabetBool = True
    elif nombre == 'Esther Cuesta Santana':
      self.cuestaBool = True

    info2 = self.get_info_descripcion(bs)
    comisiones = self.get_comisiones(info2)

    socialN = []
    redesSociales = bs.find(class_='large-8 columns').find(class_='medium-6 columns').find('p').findAll('a')
    for redes in redesSociales:
      #print(redes)
      link = redes.get('href')
      infoLink = redes.find("img").attrs['alt'].strip().split('-')
      name = infoLink[0].strip()
      redS = {name: link}
      socialN.append(redS)
      #self.redes.append(redS)

    #print('test')
    return nombre, tipo, nombreTipo, partido, comisiones, socialN


  def get_info(self, html):
    bs = soup(html, 'html.parser')
    #print(bs.prettify())

    nombre, tipo, nombreTipo, partido, comisiones, redes = self.manage_info(bs)
    asambleista = {
      'nombre': nombre.strip(),
      'organizacion politica': partido,
      'provincia': nombreTipo,
      'tipo': tipo,
      #'genero':'nan',
      #'profesion':'nan',
      #'telefono':'tel';
      'blog': self.currentlink,
      #'suplente':suplente
      'redes': redes,
      #'votaciones': votaciones
      'comisiones': comisiones,
    }

    if nombre in self.check:
      print('Ya existe este asambleista')
    else:
      self.check[nombre] = 1
      print(asambleista)
      self.asambleistas.append(asambleista)

    #print("text")

  def get_info_asambleista(self, link):
    print(str(link))
    self.currentlink = link
    html = self.get_page(link)
    if html != None:
      self.get_info(html)

  def get_json(self):

    with open('asambleistas.json', 'w', encoding='utf-8') as f:
      json.dump(self.asambleistas, f, ensure_ascii=False, default=self.obj_dict, indent=2)

  def get_all_asambleistas(self):
    links = self.get_links_to_nav()
    for link in links:
      print(link)
      currentLink = link.get('href')
      dir = self.baseUrl + currentLink
      self.get_info_asambleista(dir)

    self.get_json()
    #print('test')


if __name__ == '__main__':
  client = Asambleistas()
  client.get_all_asambleistas()