from requests import get
from urllib.parse import urljoin
import os
from os import path, getcwd, makedirs
from bs4 import BeautifulSoup as soup
import sys
import logging


class PdfClient:
  '''
  Cliente para obtener las sessiones de la asamblea en los años 2013 - 2020 en adelante
  '''
  def __init__(self):
    #pagina inicial de donde obtener las sesiones de la asamblea

    self.base_url = 'http://guest:guest@documentacion.asambleanacional.gob.ec'
    self.url = 'http://guest:guest@documentacion.asambleanacional.gob.ec/alfresco/webdav/Documentos%20Web/Votaciones%20del%20Pleno'
    self.base_dir = 'pdfs/'
    self.current_dir = ''
    self.mesdir = ''
    self.tmpdir = ''
    self.currentYear = 0 #Validar desde este anio que esta en las pos 7 [2013 2014 2015 2016 2017 2018 2019 2020]

  def get_page(self, base_url):
    "Comprobamos si existe la ruta o pagina web"
    req = get(base_url)
    if req.status_code == 200:
        return req.text
    logging.warning('http status_code: ' + req.status_code)
    raise Exception('Error {0}'.format(req.status_code))

  def get_all_content(self, html):
    "Filtramos los elementos que deseamos navegar usando BS"
    bs = soup(html, 'html.parser')  # MISSING 'html.parser'
    #print(bs.prettify())
    links = bs.findAll('a')
    links = links[1:]
    #dates = bs.findAll('table')[1]
    infoTR = bs.find(class_='listingTable').findAll('tr')
    infoTR = infoTR[2:]

    dates = []
    for info in infoTR:
        dates.append(info.contents[3].get_text())

    return links, dates

  def get_all_links(self, html):
    "Filtramos los elementos que deseamos navegar usando BS"
    bs = soup(html, 'html.parser')  # MISSING 'html.parser'
    #print(bs.prettify())
    links = bs.findAll('a')
    links = links[1:]
    return links

  def get_links_to_nav(self, base_url):
    html = self.get_page(base_url)  # MISSING ARGUMENT
    links = self.get_all_links(html)

    if len(links) == 0:
      logging.warning('No links found on the webpage.')
      #raise Exception('No links found on the webpage')
    return links

  def get_links_to_nav_initial(self, base_url):
      "Pagina inicial de la web, donde se encuentran las carpetas de todos los anios de las sesiones"
      html = self.get_page(base_url)
      links = self.get_all_links(html)
      links = links[self.currentYear:] # apartir del anio 2020 (Ultimo anio) vamos a explorar
      if len(links) == 0:
          logging.warning('No links found on the webpage.')
          # raise Exception('No links found on the webpage')
      return links

  def validate_name(self, text):
    tmp = ''
    size = len(text)
    if (len(text) > 120):
      tmp = text[:110]
      tmp2 = tmp[-4:]
      #print(tmp2)
      #print(tmp)
      if (tmp2 != '.pdf'):
        tmp = tmp + '.pdf'    
      return tmp
    return text

  def validate_dir(self,path):
    if not os.path.exists(path):
      makedirs(path)

  def get_pdf(self, base_url, base_dir):

    logging.info(' ')
    logging.info(' ')
    logging.info('---------------------------')
    html = self.get_page(base_url)  # MISSING ARGUMENT
    links, dates = self.get_all_content(html)
    if len(links) == 0:
        logging.warning('No links found on the webpage.')
        #raise Exception('No links found on the webpage')

    n_pdfs = 0
    n_saved_pdfs = 0
    logging.info('Pdfs Total: ' + str(len(links)))

    #for link in links:
    for i in range(0, len(links)):
        link = links[i]
        date = dates[i]
        current_link = link.get('href')  # This line and the line below
        text = link.contents
        name = str(i) + self.validate_name(text[0])
        logging.info('Info pdf: ' + str(text))
        logging.info('Nombre pdf: ' + str(name))

        'Validamos si el archivo seleccionado termina con la ext .pdf'
        if current_link.endswith('pdf'):
            weblink = urljoin(base_url, link['href'])
            logging.info('pdf file found at ' + str(weblink))
            #print('pdf file found:', weblink)

            n_pdfs += 1
            file_address = path.join(base_dir, name) #Obtenemos el full path del archivo

            'Validamos si existe el pdf de la sesion en nuestra carpeta, sino crea el archivo correspondiente'
            if path.exists(file_address) == False:
                content = get(weblink, stream=True)  # https://stackoverflow.com/a/44299915/2449724
                # stream=True means when function returns, only the response header is downloaded, response body is not.

                if content.status_code == 200 and content.headers[
                    'content-type'] == 'application/pdf':  # status to status_code
                    value = round(float(content.headers['Content-length']) / 1000000, 2)
                    logging.info('File size(mb): ' + str(value) )
                    with open(file_address, 'wb') as pdf:
                        logging.info('Guardando pdf en ' + file_address)
                        #print('Saving pdf to', file_address)

                        pdf.write(content.content)

                        logging.info('LISTO')
                        #print('COMPLETE')

                        n_saved_pdfs += 1
                        #Number of save pdfs is
                        logging.info('Numero de pdfs guardados es' + str(n_saved_pdfs))
                        #print()
                else:
                    logging.info('content.status_code: ' + str(content.status_code))
                    logging.info('''content.headers['content-type']:''' + content.headers['content-type'])
                    #print('content.status_code:', content.status_code)
                    #print('''content.headers['content-type']:''', content.headers['content-type'])
                    #print()

            else:
                logging.info('Ya existe el archivo!')
                #print('Already saved')
                n_saved_pdfs += 1
                #print()
        if n_pdfs == 0:
            logging.warning('No pdfs found on the page.')

        logging.info("{0} pdfs found, {1} saved in {2}".format(n_pdfs, n_saved_pdfs, base_dir))
        #print("{0} pdfs found, {1} saved in {2}".format(n_pdfs, n_saved_pdfs, base_dir))
        logging.info('_________________________ !')
        logging.info(' ')
        

  def get_all_sessions(self, base_url, url, base_dir):
    links = self.get_links_to_nav_initial(url)
    for link in links:
      #Anios 2013-2020 (O filtrados)
      current_link = link.get('href')

      'bloque de codigo para validar'
      text = link.contents
      name = self.validate_name(text[0])
      current_dir = base_dir + name + '/'
      self.validate_dir(current_dir)

      current_link = base_url + current_link  #Path de la carpeta
      meses = self.get_links_to_nav(current_link) #Links de los meses correspondientes al anio seleccionado
      #meses = meses[1:]
      for mes in meses:
        'Validar meses (valida si existe la carpeta del mes indicado, sino la crea)'
        #Meses del año correspondiente
        current_mes = mes.get('href') # Link del mes actual

        'bloque de codigo para validar'
        textM = mes.contents
        if(textM[0] == 'Septiembre 2021'):
            print('OJO')
        name = self.validate_name(textM[0])
        mesdir = current_dir + name + '/'
        self.validate_dir(mesdir) 

        current_mes = base_url + current_mes
        sesiones = self.get_links_to_nav(current_mes)
        #sesiones = sesiones[1:]
        for sesion in sesiones:
          'Validar Sesiones (valida si existe la carpeta de la sesion indicado, sino la crea)'
          #sesion actual 
          sesion_link = sesion.get('href')

          'bloque de codigo para validar'
          text = sesion.contents
          name = self.validate_name(text[0])
          tmpdir = mesdir + name + '/'
          #current_dir = current_dir + name + '/'
          self.validate_dir(tmpdir)

          sesion_link = base_url + sesion_link
          logging.info('              #SESION                        ')
          logging.info(' --------- ' + name + ' --------------------')
          self.get_pdf(sesion_link, tmpdir)

if __name__ == '__main__':
  'Info para los logs'
  client = PdfClient()
  basedir = client.base_dir
  baseurl = client.base_url
  url = client.url
  logging.basicConfig(filename='logs/pdfs_log.log' , filemode='w', level=logging.INFO, format='%(asctime)s %(message)s')
  logger = logging.getLogger('__FileServer__')
  logging.info('------------------------------------------------------------------------------------------')
  logging.info('')
  logging.info('')
  logging.info('Starting')
  logging.info('base_url: ' + baseurl)
  logging.info('base_dir: ' + basedir)

  'Funcion principal'
  client.get_all_sessions(baseurl, url, basedir)