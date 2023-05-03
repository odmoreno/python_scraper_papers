import os
import sys
import json
import time

# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)

# adding the parent directory to
# the sys.path.
sys.path.append(parent)

# now we can import the module in the parent
# directory.
from common_functions import *

class newRefs:
    def __init__(self):

        self.springer_base_url = "https://link.springer.com"
        self.papers_base = {}
        self.ref_per_papers = {}

    def load_data(self):
        self.refs_2009 = load_generic('data-2009.json')

    def checkAuths(self, ref):
        listAuthors = []
        list1 = ref['author']  if 'author' in ref else ( ref['editor'] if 'editor' in ref else '')

        for auth in list1:
            given = auth['given'] if 'given' in auth else ''
            family = auth['family'] if 'family' in auth else ''
            listAuthors.append(given + ' ' + family)
        return listAuthors

    def checkParsePaper(self, ref, code):
        if ref['type'] == 'chapter':
            title = ref['title'][0] if 'title' in ref else (ref['container-title'][0] + ' ' + (ref['collection-title'][0] if 'collection-title' in ref else ''))
            venue = ''
        else:
            title = ref['title'][0] if 'title' in ref else ''
            venue = ref['container-title'][0] if 'container-title' in ref else ''

        listAuthors = self.checkAuths(ref)
        data = {
            'type': ref['type'],
            'title': title,
            'url': ref['url'] if 'url' in ref else '',
            'date': ref['date'][0] if 'date' in ref else '',
            'venue': venue,
            'publisher': ref['publisher'][0] if 'publisher' in ref else '',
            'id': ref['doi'] if 'doi' in ref else '',
            'doi': code,
            'authors': listAuthors,
        }
        return  data

    def loop_refs(self):
        code = 'temp09_'
        id = 1

        for key, refs in self.refs_2009.items():
            print(key)
            listofrefs = []
            for ref in refs:
                print(ref)
                idcode = code + str(id)
                data = self.checkParsePaper(ref, idcode)
                #format new refs
                self.papers_base[idcode] = data
                listofrefs.append(idcode)
                id +=1

            # save the access key
            self.ref_per_papers[key] = listofrefs

        print("fin")
        save_generic('refs_2009.json', self.papers_base)
        save_generic('ref_per_paper_2009.json', self.ref_per_papers)

    def main(self):
        self.loop_refs()

if __name__ == '__main__':
    linker = newRefs()
    linker.load_data()
    linker.main()
