from common_functions import *
import json
import time
import pandas as pd



class dataVis:

    def __init__(self):
        self.base = 'data/dataforvis/'
        self.institutions = {}
        self.papers_upd = {}
        self.authors_vinci = {}
        self.authors_2009 = {}
        self.authors = {}
        self.countries = {}

    def load_data(self):
        self.institutions = load_generic(self.base + 'insti.json')
        self.papers_upd = load_generic('data/vinci_2009/papers_update.json')
        self.authors_vinci = load_generic('data/jsons/authors.json')
        self.authors_2009 = load_generic('data/vinci_2009/authors.json')
        self.countries = load_generic('data/jsons/countries.json')

    def fill_authors_2009(self):
        papers = {}
        counter = 1
        for doi, pvinci in self.papers_upd.items():
            authors = pvinci['authors']
            list_ids = []
            list_instis = []
            for author in authors:
                id = author['id']
                institution = author['institution']

                for i in institution:
                    list_instis.append(i['id'])


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
            pvinci['authors'] = list_instis

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
        self.merge_authors()


if __name__ == '__main__':

    datavis = dataVis()
    datavis.load_data()
    datavis.get_jsons_for_vis()
