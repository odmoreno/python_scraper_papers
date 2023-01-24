'''
Mejorar los datos generados y crear csvs
'''

from common_functions import *
import time
import json


class PostP:

    def __init__(self):

        self.current_doi = ''
        self.documents = {}
        self.main_path = 'data/jsons/vinci_refs/'
        #papers de vinci
        self.papers_vinci_path = 'data/jsons/papers.json'
        self.papers_vinci = {}
        #Documentos a procesar
        self.papers_refs_path = 'data/jsons/papers_ref.json'
        self.papers_refs = {}
        #Referencias por documento
        self.ref_per_paper_path = 'data/jsons/ref_per_paper.json'
        self.ref_per_paper = {}
        #Informacion de venues
        self.venues_hash = {}
        self.venue_id = 1
        #infomacion de autores
        self.authors_hash = {}
        self.author_id = 1
        #new docs
        self.new_papers_hash = {}
        # columnas para los csv
        self.papers_col = ['type', 'title', 'year', 'authors', 'citations', 'downloads', 'doi', 'publisher', 'venue',
                           'n_reference']

    def load_refs(self):
        with open(self.papers_refs_path, encoding='utf-8') as fh:
            element = json.load(fh)
        self.papers_refs = element
        with open(self.ref_per_paper_path, encoding='utf-8') as fh:
            element2 = json.load(fh)
        self.ref_per_paper = element2
        with open(self.papers_vinci_path, encoding='utf-8') as fh:
            element2 = json.load(fh)
        self.papers_vinci = element2

    def loop_refs(self):
        try:
            for document in self.papers_refs.values():
                #self.find_venues(document)
                #self.find_authors(document)
                doi = document['doi']
                self.new_papers_hash[doi] = document
            print("fin")
        except Exception as e:
            fail_message(e)

    def find_venues(self, document):
        if 'venue' in document:
            venue = document['venue']
            # print("hay venue",venue)
            if type(venue) == list:
                #print("lista")
                id = venue[0].lower()
            else:
                id = venue.lower()

            if id not in self.venues_hash:
                data = {
                    'id': self.venue_id,
                    'name': document['venue'],
                    'abbrev': '',
                    'cod': ''
                }
                self.venues_hash[id] = data
                self.venue_id += 1

    def find_authors(self, document):
        if 'authors' in document:
            authors = document['authors']
            for author in authors:
                id = author.lower()
                if id not in self.authors_hash:
                    data = {
                        'id': self.author_id,
                        'name': author,
                        'cod': ''
                    }
                    self.authors_hash[id] = data
                    self.author_id += 1

    def check_info(self):
        autores = self.authors_hash
        venues = self.venues_hash
        print(autores)
        save_generic(self.main_path+'autores_ref.json', autores)
        save_generic(self.main_path +'venues.json', venues)

    def loop_refs_in_papers(self):
        #save_generic(self.main_path + 'papers_refs.json', self.new_papers_hash)
        self.new_papers_hash = load_generic(self.main_path + 'papers_refs.json')
        print('hola')
        try:
            for doi, list in self.ref_per_paper.items():
                vinci_paper = self.papers_vinci[doi]
                for element in list:
                    self.save_element(vinci_paper, element)
        except Exception as e:
            fail_message(e)

    def save_element(self, vinci_paper, doi_ref):
        document = self.new_papers_hash[doi_ref]



if __name__ == '__main__':
    client = PostP()
    client.load_refs()
    #client.loop_refs()
    #client.check_info()
    client.loop_refs_in_papers()
