'''
Mejorar los datos generados y crear csvs
'''

from common_functions import *
import time
import json


import pandas as pd

class PostP:

    def __init__(self):

        self.current_doi = ''
        self.documents = {}
        self.main_path = 'data/vinci_refs/'
        #papers de vinci
        self.papers_vinci_path = 'data/jsons/papers_update.json'
        self.papers_vinci = {}
        #vinci authors
        self.authors_vinci = {}
        # vinci institutions
        self.insti_vinci = {}
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
        #merge papers refs
        self.merge_docs = {}
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
        #Coauthoria
        self.coauthors = {}
        self.coinsti = {}
        self.copais = {}
        self.coauthors_col = ['author_id', 'author_name', 'author2_id', 'author2_name', 'paper_doi', 'date']
        self.coinsti_col = ['institution1', 'institution2', 'paper_doi', 'date']
        self.copais_col = ['pais1', 'pais2', 'paper_doi', 'date']


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
        with open('data/jsons/authors.json', encoding='utf-8') as fh:
            element2 = json.load(fh)
        self.authors_vinci = element2
        with open('data/jsons/insti.json', encoding='utf-8') as fh:
            element2 = json.load(fh)
        self.insti_vinci = element2

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
                    #self.get_authors_per_papers(vinci_paper, authors, element)
                    self.merge_papers_refs(element)

        except Exception as e:
            print(vinci_paper)
            fail_message(e)

    def merge_papers_refs(self, key):
        if key in self.new_papers_hash:
            document = self.new_papers_hash[key]
        else:
            document = self.papers_refs[key]

        #self.merge_docs[key] = document
        self.merge_docs[document['doi']] = document

    def get_authors_per_papers(self, vinci_paper, authors_root, key):
        self.selfcitation = False

        if key in self.new_papers_hash:
            document = self.new_papers_hash[key]
        else:
            document = self.papers_refs[key]

        self.merge_docs[document['doi']] = document

        authors = document['authors']
        root_doi = vinci_paper['doi']
        parent_doi = document['doi']
        #date = document['date'] if 'date' in document else document['year']
        #date = self.check_date_list(date)
        date = vinci_paper['year']

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

    def coauthor_loop(self):

        try:
            for doi, element in self.papers_vinci.items():
                authors = element['authors']
                doi = element['doi']
                date = element['year']
                self.create_links_authors(doi, date, authors)
                #self.loop_institutions(doi, date, authors)
                #self.loop_countries(doi,date,authors)
        except Exception as e:
            print(doi, element)
            fail_message(e)

    def create_links_authors(self, doi, date, authors):
        for author in authors:
            id = author['id']
            for element in authors:
                id2 = element['id']
                if True: #id != id2:
                    cod = id + ':' +id2 + ':' + doi
                    icod = id2 + ':' +id + ':' + doi
                    if (cod not in self.coauthors) and (icod not in self.coauthors):
                        data = {
                            'author_id': id,
                            'author_name': author['name'].replace(",", " "),
                            'author2_id': id2,
                            'author2_name': element['name'].replace(",", " "),
                            'paper_doi': doi,
                            'date': date
                        }
                        #print(data)
                        self.coauthors[cod] = data

    def save_info(self):
        list = self.coauthors.values()
        list2 = self.coinsti.values()
        csv_generics(self.main_path + 'coauthorsU.csv', list, self.coauthors_col)
        #csv_generics(self.main_path + 'coinstitutions.csv', list2, self.coinsti_col)
        #csv_generics(self.main_path + 'copaises.csv', self.copais.values(), self.copais_col)

    def generate_coauthors_data(self):
        self.coauthor_loop()
        self.save_info()

    def loop_institutions(self, doi, date, authors):
        for e in authors:
            author = self.authors_vinci[e['id']] if e['id'] in self.authors_vinci else ''
            print(author)
            if author == '': continue
            if len(author['institutions']) == 0:
                continue
            insti = author['institutions'][0]
            id1 = insti['id']
            for i in authors:
                a2 = self.authors_vinci[i['id']] if i['id'] in self.authors_vinci else ''
                print(a2)
                if a2 == '': continue
                if len(a2['institutions']) == 0:
                    continue
                #insti2 = i['institution']
                insti2 = a2['institutions'][0]
                id2 = insti2['id']
                print('-> ', insti['name'], '--' ,insti2['name'])
                print(insti2)
                if True: #id1 != id2:
                    cod = id1 + ':' + id2 + ':' + doi
                    icod = id2 + ':' + id1 + ':' + doi
                    if (cod and icod) not in self.coinsti:
                        data = {
                            #'author_id': id,
                            'institution1': insti['name'].replace(",", " "),
                            #'author2_id': id2,
                            'institution2': insti2['name'].replace(",", " "),
                            'paper_doi': doi,
                            'date': date
                        }
                        self.coinsti[cod] = data


    def loop_countries(self, doi, date, authors):
        for e in authors:
            author = self.authors_vinci[e['id']] if e['id'] in self.authors_vinci else ''
            if author == '': continue
            if len(author['institutions']) == 0:
                continue
            insti = author['institutions'][0]
            id1 = insti['id']
            pais = self.insti_vinci[id1]
            ad2 = pais['ad2'] if 'ad2' in pais else ''
            ad1 = pais['ad1'] if 'ad1' in pais else ''
            ad0 = pais['ad0'] if 'ad0' in pais else ''
            if ad2 != '':
                value = ad2
            elif ad1 != '':
                value = ad1
            else:
                value = ad0

            for i in authors:
                a2 = self.authors_vinci[i['id']] if i['id'] in self.authors_vinci else ''
                if a2 == '': continue
                if len(a2['institutions']) == 0:
                    continue
                # insti2 = i['institution']
                insti2 = a2['institutions'][0]
                id2 = insti2['id']
                pais2 = self.insti_vinci[id2]
                _ad2 = pais2['ad2'] if 'ad2' in pais2 else ''
                _ad1 = pais2['ad1'] if 'ad1' in pais2 else ''
                _ad0 = pais2['ad0'] if 'ad0' in pais2 else ''

                if _ad2 != '':
                    _value = _ad2
                elif ad1 != '':
                    _value = _ad1
                else:
                    _value = _ad0

                if True: #value.lower() != _value.lower():
                    cod = value.lower() + ':' + _value.lower() + ':' + doi
                    icod = _value.lower() + ':' + value.lower() + ':' + doi
                    if (cod and icod) not in self.copais:
                        data = {
                            # 'author_id': id,
                            'pais1': value.replace(",", " "),
                            # 'author2_id': id2,
                            'pais2': _value.replace(",", " "),
                            'paper_doi': doi,
                            'date': date
                        }
                        self.copais[cod] = data


    def mergue_papers(self):

        papers_vinci = self.papers_vinci
        papers_ref = self.merge_docs
        res2 = papers_ref | papers_vinci
        print(res2)

        for key, value in res2.items():
            res2[key]['doi'] = key

        print(res2)
        save_generic('data/vinci_refs/all_data.json', res2)
        #dict3 = {'a': 5, 'b': 1, 'c': 2}
        #dict1 = {'x': 10, 'y': 8, 'b': 3}
        #dict2 = {'a': 6, 'b': 4}
        #res = dict3 | dict1 | dict2
        #print(res)

    def handle_nodes(self):
        papers_vinci = {}
        papers_refs = {}
        for doi, list in self.papers_vinci.items():
            #print(list)
            data = {
                'type': list['type'],
                'title': list['title'],
                'url': list['url'],
                'year': list['year'],
                'authors': list['authors'],
                'conference': list['conference_title'] if 'conference_title' in list else '',
                'id': doi,
                'is_vinci': True
            }
            papers_vinci[doi] = data

        for doi, list in self.merge_docs.items():
            data = {
                'type': list['type'],
                'title': list['title'],
                'url': list['url'],
                'year': list['date'],
                'authors': list['authors'],
                'conference': list['venue'],
                'id': doi,
                'is_vinci': False
            }
            papers_refs[doi] = data

        res2 = papers_refs | papers_vinci
        print(res2)
        save_generic('data/vinci_refs/nodes.json', res2)

    def handle_links(self):
        data = load_csv('data/vinci_refs/cocitations_papers.csv')
        #print(data)
        links = []
        for value in data:
            element = {
                'source': value['paper_id'],
                'target': value['parent_id'],
                'self_citation': value['self_citation'],
                'date': value['date']
            }
            links.append(element)

        json_string = json.dumps(links)
        with open('data/vinci_refs/links.json', 'w') as outfile:
            outfile.write(json_string)

    def docs_handler(self):
        self.handle_nodes()
        self.handle_links()

    def assign_id_links(self):
        links = load_generic('data/vinci_refs/links.json')
        id = 0
        new_hash = {}
        for value in links:
            new_hash[id] = value
            new_hash[id]['id'] = id
            id +=1
        #print(new_hash)

        json_string = json.dumps(new_hash)
        with open('data/vinci_refs/links2.json', 'w') as outfile:
            outfile.write(json_string)

    def get_types_nodes(self):
        nodes = load_generic('data/vinci_refs/nodes.json')
        types = {}
        id = 1
        for doi, node in nodes.items():
            tipo = node['type']
            if tipo not in types:
                types[tipo] = id
                id += 1

        json_string = json.dumps(types)
        with open('data/vinci_refs/types.json', 'w') as outfile:
            outfile.write(json_string)

    def make_csv_papers(self):
        papers_vinci = load_generic('data/vinci_refs/papers_vinci.json')
        all_authors = load_generic('data/jsons/authors_update.json')

        new_paper_vinci = {}
        new_authors = {}

        for doi, list in papers_vinci.items():
            listaut = list['authors']
            autores = []
            afilitions = []
            countries = []
            regiones = []
            for element in listaut:
                print(element)
                name = element['name']
                insti = element['institution']
                nameinsti = insti['name']
                pais = insti['country']
                region = insti['region']
                autores.append(name)
                afilitions.append(nameinsti)
                countries.append(pais)
                regiones.append(region)

                id_auth = element['id']
                author_element = all_authors[id_auth]
                institutions_list = author_element['institution']
                list1 =[]
                for insti in institutions_list:
                    list1.append(insti['name'])
                data_auth = {
                    'name': name,
                    'institutions': list1,
                }
                new_authors[id_auth] = data_auth


            data = {
                'type': list['type'],
                'title': list['title'],
                'url': list['url'],
                'year': list['year'],
                'authors': autores,
                'afilitions':afilitions,
                'countries': countries,
                'regions': regiones,
                'conference': list['conference_title'] if 'conference_title' in list else '',
                'id': doi,
            }
            new_paper_vinci[doi] = data

        list1 = new_paper_vinci.values()
        papers_col = ['type', 'title', 'url', 'year', 'authors',  'afilitions', 'countries', 'regions', 'conference', 'id']
        save_generic('data/vinci_2009/papers_vinci.json', new_paper_vinci)
        csv_generics('data/vinci_2009/papers_vinci.csv', list1, papers_col)

        list2 = new_authors.values()
        papers_col = ['name', 'institutions']
        csv_generics('data/vinci_2009/authors_vinci.csv', list2, papers_col)


if __name__ == '__main__':
    client = PostP()
    client.load_refs()
    #client.loop_refs()
    #client.loop_refs_in_papers()

    #client.loop_ref_authors()

    #client.check_info()

    #client.generate_coauthors_data()

    #client.mergue_papers()
    #client.handle_docs()
    #client.load_links()
    #client.docs_handler()

    #client.assign_id_links()
    #client.get_types_nodes()

    client.make_csv_papers()
