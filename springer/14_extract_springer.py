import os
import sys



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

import json
import time



class linker:

    def __init__(self):

        self.springer_base_url = "https://link.springer.com"
        self.papers_2009 = {}
        self.ref_per_papers = {}

    def load_data(self):
        self.papers_2009 = load_generic('vinci_2009.json')

    def loop_papers(self):
        self.driver_for_springer = make_chrome_headless()

        for key, elements in self.papers_2009.items():
            url = elements['url']
            self.driver_for_springer.get(url)
            soup = BeautifulSoup(self.driver_for_springer.page_source, "html.parser")
            # get references
            refs = soup.findAll('p', {'class': 'c-article-references__text'})
            # authors
            authors = soup.findAll(attrs={"data-test": "author-name"})
            type_paper = soup.find(attrs={"data-test": "article-category"}).text
            title = soup.find('h1', {'class': 'c-article-title'}).text
            doi = soup.find('span', {'class': 'c-bibliographic-information__value'}).text

            lista = self.extract_refs(refs)
            self.ref_per_papers[key] = lista


        save_generic('raw_refs.json', self.ref_per_papers)
        print('fin')

    def extract_refs(self, refs):
        list = []
        for ref in refs:
            text = ref.text
            list.append(text)
        return  list

    def main(self):
        self.loop_papers()



if __name__ == '__main__':
    linker = linker()
    linker.load_data()
    linker.main()