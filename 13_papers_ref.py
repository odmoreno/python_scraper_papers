from common_functions import *
import json
import time
import pandas as pd

import re
import nltk
nltk.download('punkt')
nltk.download('stopwords')

from collections import Counter

from references.patterns import patterns

class refs:

    def __init__(self):
        self.temp = {}
        self.references = {}
        self.temp_venues = {}
        self.venues = {}

        self.refs_2009 = {}
        self.ref_per_paper_2009 = {}

        self.venue_keywords = []

    def load_data(self):
        # data 2009
        self.refs_2009 = load_generic('springer/refs_2009.json')
        self.ref_per_paper_2009 = load_generic('springer/ref_per_paper_2009.json')
        #data 2010 - 2022
        self.temp = load_generic('data/jsons/papers_ref.json')
        self.temp_venues = load_generic('references/venue_temp.json')
        ref_per_papers = load_generic('data/jsons/ref_per_paper.json')
        new_ref_per_paper = {}

        for key in self.temp:
            element = self.temp[key]
            doi = element['doi']
            self.references[doi] = element

            venueT = element['venue']
            check = type(venueT) is list
            if(check):
                venue = element['venue'][0].strip().lower()
            else:
                venue = element['venue'].strip().lower()

            if venue not in self.temp_venues:
                self.temp_venues[venue] = {
                    'name': venue,
                    'value': '',
                    'publisher': '',
                    'type': '',
                    'cod': ''
                }

        for parent_doi, lista in ref_per_papers.items():
            newlist = []
            for doi in lista:
                paper = {}
                if doi in self.temp:
                    paper = self.temp[doi]
                elif doi in self.references:
                    paper = self.references[doi]
                newlist.append(paper['doi'])
            new_ref_per_paper[parent_doi] = newlist

        new_ref_per_paper = new_ref_per_paper | self.ref_per_paper_2009
        self.temp = self.temp | self.refs_2009

        save_generic('references/paper_refs.json', self.temp)
        save_generic('references/ref_per_paper.json', new_ref_per_paper)

    def main(self):
        print("hola")
        for key in self.temp:
            paper = self.temp[key]

            venueT = paper['venue']
            check = type(venueT) is list
            if (check):
                venue = paper['venue'][0].strip().lower()
            else:
                venue = paper['venue'].strip().lower()


            words = nltk.word_tokenize(venue)
            stopwords = nltk.corpus.stopwords.words('english')
            words = [word for word in words if word.isalnum() and word not in stopwords]
            self.venue_keywords.extend(words)

        venue_keywords_count = Counter(self.venue_keywords)
        sorted_keywords = venue_keywords_count.most_common()
        print(sorted_keywords)

    def identify_patterns(self):

        new_refs = {}
        venues_list = {}
        # Lista de patrones de búsqueda para cada conferencia o revista
        patterns2 = {
            'ACM Conference on Computer and Communications Security': r'\b(CCS|Conference on Computer and Communications Security)\b',
            'IEEE Symposium on Security and Privacy': r'\b(S&P|Symposium on Security and Privacy)\b',
            'USENIX Security Symposium': r'\b(USENIX Security|USENIX Security Symposium)\b',
            'IEEE Transactions on Information Forensics and Security': r'\b(TIFS|IEEE Transactions on Information Forensics and Security)\b',
            'IEEE Transactions on Dependable and Secure Computing': r'\b(TDSC|IEEE Transactions on Dependable and Secure Computing)\b',
            'Journal of Cryptology': r'\b(JoC|Journal of Cryptology)\b',
            'Annual Network and Distributed System Security Symposium': r'\b(NDSS|Annual Network and Distributed System Security Symposium)\b',
            'IEEE Symposium on Visual Languages and Human-Centric Computing': r'\b(VL/HCC|Visual Languages|Human-Centric Computing)\b',
            'VL/HCC': re.compile(r'\b(VL/HCC|Visual Languages|Human-Centric Computing)\b', re.IGNORECASE),
        }

        # Diccionario para almacenar el número de veces que aparece cada conferencia o revista
        venue_counts = {}

        # Iterar sobre cada objeto JSON en la lista de objetos
        for key in self.temp:
            if key == 'temp6513':
                print('check')

            paper = self.temp[key]
            venueT = paper['venue']
            check = type(venueT) is list
            if (check):
                venue = paper['venue'][0].strip().lower()
            else:
                venue = paper['venue'].strip().lower()

            self.temp[key]['venue'] = venue
            # Buscar coincidencias entre la cadena del atributo "venue" y los patrones de búsqueda
            for conference, pattern in patterns.items():
                if re.search(pattern, venue):
                    matches = re.findall(pattern, venue)
                    # Si se encuentra una coincidencia, aumentar el contador correspondiente en el diccionario
                    if conference in venue_counts:
                        venue_counts[conference] += 1
                    else:
                        venue_counts[conference] = 1

                    self.temp[key]['venue'] = conference
                    break

            new_refs[paper['doi']] = self.temp[key]

        # Imprimir el diccionario de conteo de conferencias y revistas
        val = 0
        for key, value in venue_counts.items():
            val += value
        print(venue_counts)
        print(val)

        save_generic('references/references.json', new_refs)
        save_generic('references/count.json', venue_counts)

    def create_cites_ref(self):
        papers_refs = load_generic('references/references.json')
        ref_per_papers = load_generic('references/ref_per_paper.json')
        cocitation_conf = {}


        for parent_doi, list in ref_per_papers.items():
            newlist = []
            for doi in list:
                paper = papers_refs[doi]
                venue = paper['venue']
                data = {
                    'venue': venue,
                    'doi': paper['doi']
                }
                newlist.append(data)
            cocitation_conf[parent_doi] = newlist

        print('fin')
        save_generic('references/paper_per_conf.json', cocitation_conf)

    def count_citations(self):
        ref_per_papers = load_generic('references/paper_per_conf.json')
        cocitation_count = {}

        for parent_doi, list in ref_per_papers.items():
            newlist = []
            banlist = {}
            for element in list:
                venue = element['venue']
                #print(element)
                if venue in patterns:
                    if venue in banlist:
                        banlist[venue] += 1
                    else:
                        banlist[venue] = 1
                else:
                    if '' in banlist:
                        banlist[''] += 1
                    else:
                        banlist[''] = 1

            cocitation_count[parent_doi] = banlist

        print('fin')
        save_generic('references/count_ref_paper.json', cocitation_count)

    def acum_nodes_ref(self):
        papers_vinci = load_generic('data/jsons/papers_update.json') #year
        ref_count = load_generic('references/count_ref_paper.json')

        elements = sorted(papers_vinci.values(), key=lambda d: d['year'])

        lista = {}
        id = 1
        for element in elements:
            paper_doi = element['doi']
            if paper_doi in ref_count:
                dict_refs = ref_count[paper_doi]
                for venue, value in dict_refs.items():
                    data = {
                        'paper': paper_doi,
                        'year': element['year'],
                        'venue': venue,
                        'value': value
                    }
                    lista[id] = data
                    id += 1

        csv_generics('references/cocitation_venues.csv', lista.values(), ['paper', 'year', 'venue', 'value'])
        print('fin')


if __name__ == '__main__':

    datavis = refs()
    datavis.load_data()
    datavis.identify_patterns()

    datavis.create_cites_ref()
    datavis.count_citations()
    datavis.acum_nodes_ref()
