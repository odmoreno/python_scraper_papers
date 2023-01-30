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
        self.main_path = 'data/vinci_refs/'
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
        self.papers_col = ['type', 'title', 'date', 'authors', 'doi', 'publisher', 'venue', 'location']
        self.citations_col = ['paper_id', 'paper_title', 'self_citation', 'parent_id', 'parent_title', 'date']
        #self.cocite_authors_col = ['author_name', 'coauthor_name', 'self_citation', 'paper_doi', 'paper_title', 'parent_doi', 'parent_title']
        self.cocite_authors_col = ['author_name', 'coauthor_name', 'self_citation', 'paper_doi', 'parent_doi', 'date']
        #listas
        self.citation_list = []
        self.papers_list=[]
        #authores citations
        self.cocite_authors = []
        self.selfcitation = False

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
        #save_generic(self.main_path+'autores_ref.json', autores)
        #save_generic(self.main_path +'venues.json', venues)
        #save_generic(self.main_path + 'papers_refs.json', self.new_papers_hash)
        csv_generics(self.main_path+'cocitations_papers.csv', self.citation_list, self.citations_col)
        #csv_generics(self.main_path +'papers.csv', self.papers_list, self.papers_col)
        csv_generics(self.main_path + 'cocitations_authors.csv', self.cocite_authors, self.cocite_authors_col)

    def loop_refs_in_papers(self):
        self.new_papers_hash = load_generic(self.main_path + 'papers_refs.json')
        try:
            for doi, list in self.ref_per_paper.items():
                vinci_paper = self.papers_vinci[doi]
                self.save_papers(doi, mode=2)
                for element in list:
                    self.save_element(vinci_paper, element)
                    self.save_papers(element)
        except Exception as e:
            print(vinci_paper)
            fail_message(e)

    def save_element(self, vinci_paper, key):
        if key in self.new_papers_hash:
            document = self.new_papers_hash[key]
        else:
            document = self.papers_refs[key]
        data = {
            'paper_id' : vinci_paper['doi'],
            'paper_title': vinci_paper['title'],
            'parent_id': document['doi'],
            'parent_title': document['title']
        }
        self.citation_list.append(data)

    def save_papers(self, key, mode = 1):
        if mode == 1:
            if key in self.new_papers_hash:
                document = self.new_papers_hash[key]
            else:
                document = self.papers_refs[key]
            date = document['date']
            venue = document['venue']
            location = document['location']
            authors = document['authors']
        else :
            document = self.papers_vinci[key]
            date = document['year']
            venue = 'vinci'
            location = ''
            authors = []
            for autor in document['authors']:
                authors.append(autor['name'])

        data = {
            'type' : document['type'],
            'title': document['title'],
            'date': date,
            'authors': authors,
            'doi': document['doi'],
            'publisher': document['publisher'],
            'venue': venue,
            'location': location
        }
        self.papers_list.append(data)

    def loop_ref_authors(self):
        self.new_papers_hash = load_generic(self.main_path + 'papers_refs.json')
        try:
            for doi, list in self.ref_per_paper.items():
                vinci_paper = self.papers_vinci[doi]
                authors = []
                for autor in vinci_paper['authors']:
                    authors.append(autor['name'])
                #loop refs
                for element in list:
                    self.get_authors_per_papers(vinci_paper, authors, element)

        except Exception as e:
            print(vinci_paper)
            fail_message(e)

    def get_authors_per_papers(self, vinci_paper, authors_root, key):
        self.selfcitation = False

        if key in self.new_papers_hash:
            document = self.new_papers_hash[key]

        else:
            document = self.papers_refs[key]

        authors = document['authors']
        root_doi = vinci_paper['doi']
        parent_doi = document['doi']
        date = document['date'] if 'date' in document else document['year']
        date = self.check_date_list(date)

        print('---')
        print(authors_root)
        print(authors, len(authors))
        print('---!')

        if len(authors) == 0:
            return
        for root in authors_root:
            for author in authors:
                if author == ' ':
                    return

                selfcitation = False
                value = [item for item in authors_root if author in item]
                compare = self.compare_names(root, author)
                if len(value) > 0:
                    selfcitation = True
                    self.selfcitation = True
                else:
                    data_val = compare['values']
                    flag = compare['same_size']
                    size_val = compare['size']
                    if flag:
                        if len(data_val) == size_val:
                            selfcitation = True
                            self.selfcitation = True
                    elif len(data_val)>1:
                        print("hmm")
                        selfcitation = True
                        self.selfcitation = True

                data = {
                    'author_name': root,
                    'coauthor_name': author,
                    'self_citation': selfcitation,
                    'paper_doi': root_doi,
                    #'paper_title': vinci_paper['title'],
                    'parent_doi': parent_doi,
                    'date': date
                    #'parent_title': vinci_paper['doi']
                }
                self.cocite_authors.append(data)

        ''' cocitation paper zone'''
        cite = {
            'paper_id': vinci_paper['doi'],
            'paper_title': vinci_paper['title'],
            'self_citation': self.selfcitation,
            'parent_id': document['doi'],
            'parent_title': document['title'],
            'date': date
        }
        self.citation_list.append(cite)

        ''' FIN'''


    def compare_names(self, name1, name2):
        split_1 = name1.split(" ")
        newname = name2.replace('.', '').strip()
        split_2 = newname.split(" ")
        valuesp2 = []
        values = []

        size_aw = len(split_1)
        size_bw = len(split_2)

        for idx, p1 in enumerate(split_1):
            flag = False
            for idx2, p2 in enumerate(split_2):
                size = len(p2)
                size_a = len(p1)
                if p1.lower() == p2.lower():
                    valuesp2.append(p2)
                    flag = True
                else:
                    if size == 1:
                        #print("check", p2[0], p1[0].lower())
                        if p2[0].lower() == p1[0].lower():
                            if(idx == idx2):
                                valuesp2.append(p2)
                                flag = True
            if flag:
                values.append(p1)

        same_size = False
        if size_aw == size_bw: same_size = True

        data = {
            'values': values,
            'same_size': same_size,
            'size': size_aw
        }
        return data


    def check_date_list(self, date):
        newdate = date
        if type(date) == list:
            print("Variable is a list.")
            for element in date:
                size = len(element)
                if size == 4:
                    newdate = element
                    return newdate
                else:
                    newdate = element
                    if '-' in newdate:
                        splitdate = newdate.split("-")
                        for splits in splitdate:
                            if len(splits) == 4:
                                newdate = splits
        else:
            if '-' in date:
                splitdate = date.split("-")
                for split in splitdate:
                    if len(split) == 4:
                        newdate = split
        return newdate


if __name__ == '__main__':
    client = PostP()
    client.load_refs()
    #client.loop_refs()
    #client.loop_refs_in_papers()
    client.loop_ref_authors()
    client.check_info()
