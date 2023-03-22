from common_functions import *
import json
import time
import pandas as pd



class dataVis:

    def __init__(self):
        self.base = 'data/dataforvis/'
        self.institutions = {}
        self.reverse_institutions = {}
        self.papers_upd = {}
        self.authors_vinci = {}
        self.authors_2009 = {}
        self.authors = {}
        self.countries = {}
        self.regiones = {}
        self.reverse_institutions = {}

        #nuevos dicts
        self.new_instis = {}
        self.paises = {}
        self.regiones = {}
        self.insti_final = {}
        self.new_authors = {}

        self.new_regions = {}

    def load_data(self):
        self.institutions = load_generic(self.base + 'insti.json')
        self.papers_upd = load_generic('data/vinci_2009/papers_update.json')
        self.authors_vinci = load_generic('data/jsons/authors.json')
        self.authors_2009 = load_generic('data/vinci_2009/authors.json')
        self.countries = load_generic('data/jsons/countries.json')
        self.papers_en_vinci = load_generic('data/vinci_refs/papers_vinci.json')

        for element in self.countries:
            pais = element["country"].strip().lower()
            region = element["continent"].strip().lower()
            self.regiones[pais] = region

        for key, list in self.institutions.items():
            name = list['name']
            codname = name.lower()
            self.reverse_institutions[codname] = list

    def reformat_papers(self):
        new_format = {}
        counter = 1
        insti_id = 1

        for doi, pvinci in self.papers_en_vinci.items():
            authors = pvinci['authors']
            list_ids = []
            list_instis = []
            list_paises = []
            list_regiones = []
            for author in authors:
                id = author['id']
                insti = author['institution']
                key = insti['name'].lower()
                id_insti = insti_id

                if insti['region'] not in self.new_regions:
                    self.new_regions[insti['region']] = insti['region']

                if key not in self.new_instis:
                    self.new_instis[key] = {
                        'id': insti_id,
                        'name': key,
                        'country': insti['country'],
                        'region': insti['region'],
                        'papers': [],
                        'authors': [],

                    }
                    self.new_instis[key]['papers'].append(doi)
                    self.new_instis[key]['authors'].append(id)

                    #if insti_id not in list_instis:
                    list_instis.append(insti_id)
                    insti_id += 1
                else:

                    if doi not in self.new_instis[key]['papers']:
                        self.new_instis[key]['papers'].append(doi)
                    if id not in self.new_instis[key]['authors']:
                        self.new_instis[key]['authors'].append(id)
                    temp = self.new_instis[key]
                    id_insti = temp['id']
                    if temp['id'] not in list_instis:
                        list_instis.append(temp['id'])

                if id not in self.new_authors:
                    if id in self.authors_vinci:
                        author = self.authors_vinci[id]

                    self.new_authors[id] = {
                        'id': id,
                        'name': author['name'],
                        'url': author['url'],
                        'papers': [],
                        'institutions': [],
                        'countries': [],
                        'regions': []
                    }
                    self.new_authors[id]['papers'].append(doi)
                    self.new_authors[id]['institutions'].append(id_insti)
                    self.new_authors[id]['countries'].append(insti['country'])
                    self.new_authors[id]['regions'].append(insti['region'])
                else:
                    if doi not in self.new_authors[id]['papers']:
                        self.new_authors[id]['papers'].append(doi)
                    if id_insti not in self.new_authors[id]['institutions']:
                        self.new_authors[id]['institutions'].append(id_insti)
                    if insti['country'] not in self.new_authors[id]['countries']:
                        self.new_authors[id]['countries'].append(insti['country'])
                    if insti['region'] not in self.new_authors[id]['regions']:
                        self.new_authors[id]['regions'].append(insti['region'])



                # append lists
                if insti['country'] not in list_paises:
                    list_paises.append(insti['country'])
                if insti['region'] not in list_regiones:
                    list_regiones.append(insti['region'])
                list_ids.append(id)

            data = {
                "type": pvinci['type'],
                "title": pvinci['title'],
                "url": pvinci['url'],
                "year": pvinci['year'],
                "authors": list_ids,
                "institutions": list_instis,
                "countries": list_paises,
                "regions": list_regiones,
                "doi": pvinci['doi'],
                "publisher": pvinci['publisher'],
                "conference": 'vinci',
                "id": counter
            }
            new_format[pvinci['doi']] = data
            counter += 1
        print("fin")
        save_generic('data/dataforvis/nodesu.json', new_format)
        save_generic('data/dataforvis/instiu.json', self.new_instis)
        save_generic('data/dataforvis/authorsu.json', self.new_authors)
        save_generic('data/dataforvis/regions.json', self.new_regions)

    def reformat_institutions(self):
        insti_reverse = load_generic('data/dataforvis/instiu.json')
        for key, list in insti_reverse.items():
            id = list['id']
            self.insti_final[id] = list

        save_generic('data/dataforvis/instiu.json', self.insti_final)

    def fill_authors_2009(self):
        papers = {}
        counter = 1
        for doi, pvinci in self.papers_upd.items():
            #print(pvinci)
            authors = pvinci['authors']
            year = pvinci['year']
            list_ids = []
            list_instis = []
            list_paises = []
            list_regiones = []
            for author in authors:
                id = author['id']
                institution = author['institution']
                for i in institution:
                    pass
                    #print( type(i['id']), i['id'])
                    #list_instis.append(i['id'])
                    #info_extra = self.get_countries_and_region(self.institutions[i['id']])
                    #list_paises.append(info_extra[0])
                    #list_regiones.append(info_extra[1])

                if id in self.authors_2009:
                    self.authors_2009[id]['institutions'] = institution
                    if 'papers' not in self.authors_2009[id]:
                        self.authors_2009[id]['papers'] = []
                        self.authors_2009[id]['papers'].append(doi)
                    else:
                        self.authors_2009[id]['papers'].append(doi)
                if id in self.authors_vinci:
                    if 'papers' not in self.authors_vinci[id]:
                        self.authors_vinci[id]['papers'] = []
                        self.authors_vinci[id]['papers'].append(doi)
                    else:
                        self.authors_vinci[id]['papers'].append(doi)
                list_ids.append(id)

            pvinci['authors'] = list_ids
           #pvinci['institutions'] = list_instis
           # pvinci['countries'] = list_paises
           # pvinci['regions'] = list_regiones

            pvinci['doi'] = doi
            pvinci['conference'] = 'vinci'

            pvinci['id'] = counter
            counter += 1

            if 'citations' in pvinci:
                del pvinci['citations']
            if 'downloads' in pvinci:
                del pvinci['downloads']
            if 'extra' in pvinci:
                del pvinci['extra']
            if 'conference_isbn' in pvinci:
                del pvinci['conference_isbn']
            if 'abstract' in pvinci:
                del pvinci['abstract']
            if 'n_reference' in pvinci:
                del pvinci['n_reference']
            if 'conference_title' in pvinci:
                del pvinci['conference_title']
            #if 'doi' in pvinci:
            #    del pvinci['doi']

        print('hi')
        save_generic('data/dataforvis/authors_2009.json', self.authors_2009)
        save_generic('data/dataforvis/authors_vinci.json', self.authors_vinci)
        save_generic('data/dataforvis/nodes.json', self.papers_upd)

    def config_vinci_au(self):
        for id, pvinci in self.authors_vinci.items():
            if 'institution' in self.authors_vinci:
                del self.authors_vinci[id]['institution']
        #print(self.authors_vinci)

    def get_countries_and_region(self, insti):
        region = ''
        if 'ad2' in insti:
            pais = insti['ad2']
        elif 'ad1' in insti:
            pais = insti['ad1']
        else:
            pais = insti['ad0']

        pais = pais.lower()
        if pais in self.regiones:
            region = self.regiones[pais]

        return [pais, region]


    def merge_authors(self):
        authors_vinci = {}
        for id, list in self.authors_vinci.items():

            instis = list['institutions']
            new = []
            for i in instis:
                if i['id'] != 'javascript:void(0)':
                    new.append(i['id'])

            data = {
                'doi': list['id'],
                'name': list['name'],
                'url': list['url'],
                'institutions': new,
                'papers': list['papers'],
                'n_insti': len(new),
                'n_paper': len(list['papers']),
            }
            authors_vinci[id] = data

        authors_2009 = {}
        for id, list in self.authors_2009.items():
            print(list)
            instis = list['institutions']
            new = []

            print(instis)
            if list['name'] == 'Kang Zhang':
                print('hmm')

            for i in instis:
                if i['id'] != 'javascript:void(0)':
                    new.append(i['id'])

            data = {
                'doi': list['id'],
                'name': list['name'],
                'url': '',
                'institutions': new,
                'papers': list['papers'],
                'n_insti': len(new),
                'n_paper': len(list['papers']),
            }
            authors_2009[id] = data

        self.authors = authors_2009 | authors_vinci

        save_generic('data/dataforvis/authors.json', self.authors)

    def fix_papers(self):

        pass

    def get_jsons_for_vis(self):
        self.fill_authors_2009()
        self.config_vinci_au()
        self.reformat_papers()
        self.reformat_institutions()

        self.merge_authors()


if __name__ == '__main__':

    datavis = dataVis()
    datavis.load_data()
    datavis.get_jsons_for_vis()
