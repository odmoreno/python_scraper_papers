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
from references.patterns import pub_patterns

class refs:

    def __init__(self):
        self.temp = {}
        self.references = {}
        self.venues_names = {}
        self.venues_pub = {}
        self.refs_2009 = {}
        self.ref_per_paper_2009 = {}

        self.venue_keywords = []

    def load_data(self):
        # data 2009
        self.refs_2009 = load_generic('springer/refs_2009.json')
        self.ref_per_paper_2009 = load_generic('springer/ref_per_paper_2009.json')
        #data 2010 - 2022
        self.temp = load_generic('data/jsons/papers_ref.json')
        ref_per_papers = load_generic('data/jsons/ref_per_paper.json')
        #cargar venues names
        self.venues_names = load_generic('references/venues_name.json')
        #cargar publishers de venues
        self.venues_pub = load_generic('references/venues_pubs.json')

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

        for parent_doi, lista in ref_per_papers.items():
            newlist = []
            for doi in lista:
                paper = {}
                if doi in self.temp:
                    paper = self.temp[doi]
                elif doi in self.references:
                    paper = self.references[doi]
                #print(doi, paper)
                newlist.append(paper['doi'])
            new_ref_per_paper[parent_doi] = newlist

        new_ref_per_paper = new_ref_per_paper | self.ref_per_paper_2009
        self.temp = self.temp | self.refs_2009

        save_generic('references/paper_refs.json', self.temp)
        save_generic('references/ref_per_paper.json', new_ref_per_paper)

    '''
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
    '''

    def checkifhaslist(self, value):
        check = type(value) is list
        if check:
            newval = value[0].strip().lower()
        else:
            newval = value.strip().lower()
        return newval

    def check_status_publishers(self, paper):
        conference = paper['venue']
        pub = paper['publisher']

        if conference not in self.venues_pub:
            self.venues_pub[conference] = pub
        else:
            pub_tmp = self.venues_pub[conference]
            if pub_tmp == "":
                self.venues_pub[conference] = pub


    def identify_patterns(self):
        new_refs = {}
        venues_dict = {}
        # Diccionario para almacenar el número de veces que aparece cada conferencia o revista
        venue_counts = {}
        publisher_counts = {}
        venues_no_registradas = {}
        all_refs = {}
        # Iterar sobre cada objeto JSON en la lista de objetos
        for key in self.temp:
            paper = self.temp[key]
            type_paper = paper['type']

            venue = self.checkifhaslist(paper['venue'])
            self.temp[key]['venue'] = venue
            url = self.checkifhaslist(paper['url'])
            self.temp[key]['url'] = url
            publisher = self.checkifhaslist(paper['publisher'])
            self.temp[key]['publisher'] = publisher

            all_refs[paper['doi']] = self.temp[key]
            if type_paper == 'article-journal' or (type_paper == 'paper-conference'):
                print(type_paper)
                venue = self.checkifhaslist(paper['venue'])
                self.temp[key]['venue'] = venue
                url = self.checkifhaslist(paper['url'])
                self.temp[key]['url'] = url
                publisher = self.checkifhaslist(paper['publisher'])
                self.temp[key]['publisher'] = publisher

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

                # Buscar nombres de publishers en las urls
                for pub, pattern in pub_patterns.items():
                    if re.search(pattern, publisher):
                        self.temp[key]['publisher'] = pub
                        break
                    if re.search(pattern, url):
                        self.temp[key]['publisher'] = pub
                        break

                new_refs[paper['doi']] = self.temp[key]

                # Revisamos publicaciones del dict, para evitar los campos vacios
                current_paper = self.temp[key]
                conference = current_paper['venue']
                pub = current_paper['publisher']

                if conference == "Information Visualization" and pub !="":
                    new_name = conference +' '+pub

                    #print(f"Conf '{key}': {new_name}")
                    self.temp[key]['venue'] = new_name
                    if new_name in venue_counts:
                        venue_counts[new_name] += 1
                    else:
                        venue_counts[new_name] = 1


                if pub == "":
                    if conference in self.venues_pub:
                        pub_tmp = self.venues_pub[conference]
                        if pub_tmp != "":
                            self.temp[key]['publisher'] = self.venues_pub[conference]
                #actualizamos el dictionario
                self.check_status_publishers(current_paper)

                '''
                venue_cod = self.temp[key]['venue']
                pub_cod = self.temp[key]['publisher']
                if venue_cod in venue_counts:
                    data = {
                        "name": "",
                        "code": venue_cod,
                        "publisher": pub_cod
                    }
                    venues_dict[venue_cod] = data'''

                if publisher in publisher_counts:
                    publisher_counts[publisher] += 1
                else:
                    publisher_counts[publisher] = 1


        # Imprimir el diccionario de conteo de conferencias y revistas
        val = 0
        for key, value in venue_counts.items():
            val += value
            name = self.venues_names[key] if key in self.venues_names else ''
            publisher = self.venues_pub[key]
            data = {
                "name": name,
                "code": key,
                "publisher": publisher,
                "value": value
            }
            venues_dict[key] = data

        print(venue_counts)
        print(val)
        print(publisher_counts)
        pubxvenues = self.create_pub_conferences_dict(venues_dict)
        #pubxvenues = self.count_conferences_in_refs(new_refs, pubxvenues)


        for key, value in new_refs.items():
            venue = value['venue']
            if venue not in patterns:
                if venue in venues_no_registradas:
                    venues_no_registradas[venue] += 1
                else:
                    venues_no_registradas[venue] = 1

        # Sort the dictionary in descending order by values
        sorted_dict = dict(sorted(venues_no_registradas.items(), key=lambda x: x[1], reverse=True))
        sorted_counts = dict(sorted(venue_counts.items(), key=lambda x: x[1], reverse=True))
        sorted_pubs = dict(sorted(publisher_counts.items(), key=lambda x: x[1], reverse=True))


        save_generic('references/references.json', new_refs)
        save_generic('references/references_2.json', all_refs)
        save_generic('references/count.json', sorted_counts)
        save_generic('references/pub_count.json', sorted_pubs)
        save_generic('references/no_count.json', sorted_dict)
        save_generic('references/venues.json', venues_dict)
        save_generic('references/venues_pubs.json', self.venues_pub)
        save_generic('references/publishers.json', pubxvenues)

    def create_pub_conferences_dict(self, conferences):
        pub_dict = {}
        for key, value in conferences.items():
            #print(key)
            publisher = value['publisher'].lower().strip()
            venue = value['code'].lower().strip()
            if publisher not in pub_dict:
                data  = {}
                data[venue] = 0
                pub_dict[publisher] = {
                    'name' : publisher,
                    'venues': data
                }
            else:
                pub = pub_dict[publisher]
                #venues_in_pub = pub['venues']
                if venue not in pub['venues']:
                    pub['venues'][venue] = 0
                else:
                    pub['venues'][venue] += 1

        return  pub_dict

    def count_conferences_in_refs(self, refs, pubs):
        '''
                for key, value in refs.items():
            publisher = value['publisher']
            venue = value['venue']
            if publisher in pubs:
                if venue in pubs['venues']:
                    pubs['venue']:
        :param refs:
        :param pubs:
        :return:
        '''
        pass



    def create_cites_ref(self):
        papers_refs = load_generic('references/references.json')
        ref_per_papers = load_generic('references/ref_per_paper.json')
        cocitation_conf = {}

        #GI graphics interface
        #
        for parent_doi, list in ref_per_papers.items():
            newlist = []
            for doi in list:
                if doi in papers_refs:
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
