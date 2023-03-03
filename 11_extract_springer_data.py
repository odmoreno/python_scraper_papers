from common_functions import *
import json
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class SpringerClient:

    def __init__(self):
        self.base_url = "https://link.springer.com/book/10.1007/978-1-4419-0312-9?page=2#toc"
        self.acm_url = "https://dblp.org/db/conf/vinci/vinci2009.html"

        self.papers_vinci ={}
        self.autores_vinci = {}
        self.institutos_vinci = {}

        self.reverse_institutos = {}
        self.reverse_authors = {}
        
        self.institutions = {}
        self.papers_acm = {}
        self.authors = {}

        self.paises = []
        self.regions = {}
        self.cities_check = {}

        #valores tmp
        self.tmp = 1
        self.tmp2 = 1

    def extract_page_for_acm(self):
        self.driver_for_acm.get(self.acm_url)
        # parse source code
        soup = BeautifulSoup(self.driver_for_acm.page_source, "html.parser")
        papers = soup.findAll("li", class_="entry inproceedings")
        for index in range(len(papers)):
            paper = papers[index]
            self.extract_content_acm(paper)

    def extract_content_acm(self, paper):
        nav_url =  paper.find('nav', {'class': 'publ'})
        url = nav_url.a["href"]
        title = paper.find('span', {'class': 'title'}).text
        pagination = paper.find(attrs={"itemprop": "pagination"})
        datepublished = '2009'
        # authors
        authors = paper.findAll(attrs={"itemprop": "author"})
        #validate
        pagination = '' if pagination is None else pagination.text
        #loop authors
        autores = []
        for author in authors:
            autores.append(author.text)
            id = 'a09_'+ str(self.tmp)
            id2 = 'i09_' + str(self.tmp2)

            author_data = {
                'name': author.text,
                'institutions': [
                    {
                        "id": id2,
                        "name": "",
                    }
                ],
                'id': id
            }
            insti_data = {
                "id": id2,
                "name": "",
                "ad0": "",
                "ad1": "",
            }
            self.institutions[id2] = insti_data
            self.tmp2 += 1

            self.authors[id] = author_data
            self.tmp += 1

        doi_split = url.split('doi.org/', 1)
        doi = doi_split[1]

        data = {
            'type': 'paper-conference',
            "title": title,
            "url": url,
            "authors": autores,
            "doi": doi,
            "date": datepublished,
            "publisher": "Springer",
            "venue": "vinci"
        }
        self.papers_acm[doi] = data

    def save_info(self):
        save_generic('data/vinci_2009/papers_acm.json', self.papers_acm)
        save_generic('data/vinci_2009/authors.json', self.authors)
        save_generic('data/vinci_2009/insti.json', self.institutions)


    def extract_info_springer(self):
        self.papers_acm = load_generic('data/vinci_2009/papers_acm.json')
        self.authors = load_generic('data/vinci_2009/authors.json')
        self.driver_for_acm = make_chrome_headless()

        for doi, list in self.papers_acm.items():
            print(doi)
            #url = list['url']
            type = "paper-conference"
            self.papers_acm[doi]['type'] = type
            #self.get_data_springer(doi, list)

    def get_data_springer(self, doi, paper):

        url_springer = paper['url']
        self.driver_for_acm.get(url_springer)
        soup = BeautifulSoup(self.driver_for_acm.page_source, "html.parser")
        #type = soup.find(attrs={"data-test": "article-category"}).text
        #self.papers_acm[doi]['type'] = type
        authors = soup.find(attrs={"data-test": "author-name"})
        for author in authors:
            author.click()
            #popup = soup.find(attrs={"data-test": "author-name"}) "c-author-popup__author-list"
            pass
        pass
    
    def load_data_vinci(self):
        self.papers_vinci = load_generic('data/jsons/papers_update.json')
        self.institutos_vinci = load_generic('data/jsons/insti.json')
        self.autores_vinci = load_generic('data/jsons/authors_update.json')
        self.paises = load_generic('data/jsons/countries.json')
        self.cities = load_generic('data/jsons/country-by-capital.json')

    def reverse_dicts(self):
        for key, list in self.institutos_vinci.items():        
            name = list['name']
            codname = name.lower()
            self.reverse_institutos[codname] = list
            
        for key, list in self.autores_vinci.items():        
            name = list['name']
            codname = name.lower()
            self.reverse_authors[codname] = list

        for element in self.paises:
            pais = element["country"].strip().lower()
            region = element["continent"].strip().lower()
            self.regions[pais] = region

        for element in self.cities:
            print(element)
            city = element["city"].strip().lower()
            country = element["country"].strip().lower()
            self.cities_check[city] = country

    def extract_info_2009(self, name, instituto):
        if 'ad2' in instituto:
            value = instituto['ad2']
        elif 'ad1' in instituto:
            value = instituto['ad1']
        else:
            value = instituto['ad0']

        value = value.strip().lower()
        if value in self.regions:
            region = self.regions[value]

        data = self.get_data_insti(name, value, region)
        return  data

    def get_data_insti(self, name, value, region):
        data = {
            'name': name,
            'country': value,
            'region': region
        }
        return data

    def check_pais_region(self, insti):
        split_e = insti.split(" ")
        pais = ""
        region = ""
        for bx in split_e:
            if bx in self.cities_check:
                pais = self.cities_check[bx.lower()]
            if bx in self.regions:
                pais = bx.lower()

        if pais in self.regions:
            region = self.regions[pais]

        return [pais, region]

    def format_papers_vinci_2(self):
        try:
            new_papers = {}
            for doi, list in self.papers_vinci.items():
                autores = list['authors']
                year = list['year']
                autor_list_new = []
                title = list['title']
                if title == 'IMDb Explorer: Visual Exploration of a Movie Database':
                    print('a')
                    pass

                for autor in autores:
                    instituto = autor['institution']
                    if year == '2009':
                        name = instituto[0]['name']
                        id_insti = instituto[0]['id']
                        element = self.institutos_vinci[id_insti]
                        data = self.extract_info_2009(name, element)
                        autor['institution'] = data
                    else:
                        instituto = instituto.replace('.', ',')
                        split_insti = instituto.split(',')
                        check_first = True
                        size_instituto = len(split_insti)
                        if size_instituto == 1:
                            instituto = split_insti[0].lower()
                            if instituto in self.reverse_institutos:
                                element = self.reverse_institutos[instituto]
                                data = self.extract_info_2009(element['name'], element)
                                autor['institution'] = data
                                pass
                            else:
                                split_by_parts = split_insti[0].lower().split(" ")
                                size_parts = len(split_by_parts)
                                tempKey = ''
                                temp_size = 1
                                for key in self.reverse_institutos:
                                    key = key.replace(',', ' ')
                                    split2 = key.lower().split(" ")
                                    duplicated = [i for i in split_by_parts if i in split2]
                                    size = len(duplicated)
                                    if size > temp_size:
                                        temp_size = size
                                        tempKey = key
                                print(tempKey, temp_size)
                                if size_parts >= 6 and (temp_size == size_parts-1):
                                    element = self.reverse_institutos[instituto]
                                    data = self.extract_info_2009(element['name'], element)
                                    autor['institution'] = data
                                else:
                                    unversidad = instituto
                                    e = self.check_pais_region(instituto)
                                    data = self.get_data_insti(unversidad, e[0], e[1])
                                    autor['institution'] = data
                                    pass

                        else:
                            last_index = size_instituto - 1
                            posible_universidad = split_insti[0].strip()
                            posible_pais = split_insti[last_index].strip().lower()
                            for ax in split_insti:
                                ax = ax.lower().strip()
                                ax = re.sub(r'[^\w\s]', '', ax)
                                ax = ''.join([i for i in ax if not i.isdigit()])
                                ax = ax.strip()
                                second = ax.split(" ")
                                for bx in second:
                                    if 'university' in bx:
                                        posible_universidad = ax.lower()
                                    if bx in self.cities_check:
                                        posible_pais = self.cities_check[bx.lower()]
                                    if bx in self.regions:
                                        posible_pais = bx.lower()

                            if posible_pais in self.regions:
                                region = self.regions[posible_pais]
                            data = self.get_data_insti(posible_universidad, posible_pais, region)
                            autor['institution'] = data
                new_papers[doi] = list
            print(new_papers)
            save_generic('data/vinci_refs/papers_vinci.json', new_papers)

        except Exception as e:
            print(list)
            fail_message(e)
            driver_for_dblp.quit()




    def format_papers_vinci(self):
        try:
            new_papers = {}
            for doi, list in self.papers_vinci.items():
                autores = list['authors']
                year = list['year']
                autor_list_new = []
                for autor in autores:
                    instituto = autor['institution']
                    if year == '2009':
                        name = instituto[0]['name']
                        print(name)
                        split_insti = name.split(',')
                    else:
                        instituto = instituto.replace('.', ',')
                        split_insti = instituto.split(',')

                    if year != '2009':
                        check_first = True
                        size_instituto = len(split_insti)
                        if size_instituto == 1:
                            # think
                            split1 = split_insti[0].lower().split(" ")
                            size = len(split1)
                            for key in self.reverse_institutos:
                                split2 = key.lower().split(" ")
                                match = [i for i, j in zip(split1, split2) if i == j]

                                if split_insti[0] in key.lower():
                                    print(self.reverse_institutos[key])
                                    instituto_element = self.reverse_institutos[key]
                                    id_insti = instituto_element['id']
                                    autor['institution'] = id_insti
                                    break;


                                if (len(match) == size):
                                    instituto_element = self.reverse_institutos[key]
                                    id_insti = instituto_element['id']
                                    value = ''
                                    if 'ad2' in instituto_element:
                                        value = instituto_element['ad2']
                                    elif 'ad1' in instituto_element:
                                        value = instituto_element['ad1']
                                    else:
                                        value = instituto_element['ad0']

                                    value = value.strip().lower()
                                    if value in self.regions:
                                        region = self.regions[value]

                                    data = {
                                        'name': name.strip(),
                                        'country': value.strip(),
                                        'region': region.strip()
                                    }
                                    autor['institution'] = data
                                    check_first = False
                        else:
                            last_index = size_instituto - 1
                            posible_universidad = split_insti[0].strip()
                            posible_pais = split_insti[last_index].strip().lower()


                            for ax in split_insti:

                                if 'university' in ax.lower():
                                    posible_universidad = ax.lower()

                            for ax in split_insti:
                                if (ax == "chinese academy of sciences and university of chinese academy of sciencess"):
                                    print('xa')
                                    pass
                                ax = ax.lower().strip()
                                ax = re.sub(r'[^\w\s]', '', ax)
                                ax = ''.join([i for i in ax if not i.isdigit()])
                                ax = ax.strip()

                                second = ax.split(" ")
                                for bx in second:
                                    if 'university' in bx:
                                        posible_universidad = ax.lower()
                                    if bx in self.cities_check:
                                        posible_pais = self.cities_check[bx.lower()]
                                    if bx in self.regions:
                                        posible_pais = bx.lower()

                            if posible_pais in self.regions:
                                region = self.regions[posible_pais]


                            data = {
                                'name': posible_universidad.strip(),
                                'country': posible_pais.strip(),
                                'region': region.strip()
                            }
                            autor['institution'] = data
                            check_first = False

                        if check_first == True:
                            last_index = size_instituto - 1
                            posible_universidad = split_insti[0].strip()
                            posible_pais = split_insti[last_index].strip().lower()

                            for ax in split_insti:
                                ax = ax.lower().strip()
                                #ax = ''.join(filter(str.isalnum, ax))
                                ax = re.sub(r'[^\w\s]', '', ax)
                                ax = ''.join([i for i in ax if not i.isdigit()])
                                ax = ax.strip()

                                if 'university' in ax.lower():
                                    posible_universidad = ax.lower()
                                if ax in self.cities_check:
                                    posible_pais = self.cities_check[ax.lower()]
                                if ax in self.regions:
                                    posible_pais = ax.lower()

                            if posible_pais in self.regions:
                                region = self.regions[posible_pais]


                            data = {
                                'name': posible_universidad.strip(),
                                'country': posible_pais.strip(),
                                'region': region.strip()
                            }
                            autor['institution'] = data

                    for element in split_insti:
                        element = element.lower()
                        #split1 = element.split(" ")
                        '''
                        size= len(split1)
                        for key in self.reverse_institutos:
                            split2 = key.lower().split(" ")
                            match  = [i for i, j in zip(split1, split2) if i == j]
                            #print(len(match), match)
                            if(len(match) == size ):
                                savekey = key
                                instituto_element = self.reverse_institutos[savekey]
                                id_insti = instituto_element['id']
                                autor['institution'] = id_insti
                                break;

                            if element in key.lower():
                                print(self.reverse_institutos[key])
                                instituto_element = self.reverse_institutos[key]
                                id_insti = instituto_element['id']
                                autor['institution'] = id_insti
                                break;
                        '''
                        ##nueva forma
                        if year == '2009':
                            insti = element
                            if insti in self.reverse_institutos:
                                instituto_element = self.reverse_institutos[insti]
                                id_insti = instituto_element['id']
                                name = instituto_element['name']
                                value = ''
                                if 'ad2' in instituto_element:
                                    value = instituto_element['ad2']
                                elif 'ad1' in instituto_element:
                                    value = instituto_element['ad1']
                                else:
                                    value = instituto_element['ad0']

                                value = value.strip().lower()
                                if value in self.regions:
                                    region = self.regions[value]

                                data = {
                                    'name': name.strip(),
                                    'country': value,
                                    'region': region
                                }
                                autor['institution'] = data
                        else:

                            pass

                    autor_list_new.append(autor)
                new_papers[doi] = list
            print(new_papers)
            save_generic('data/vinci_refs/papers.json', new_papers)
            pass

        except Exception as e:
            print(list)
            fail_message(e)
            driver_for_dblp.quit()



    def get_papers_vinci_info(self):
        self.load_data_vinci()
        self.reverse_dicts()
        self.format_papers_vinci_2()


    def extract_authors(self):
        self.papers_acm = load_generic('data/vinci_2009/papers_acm.json')
        self.authors = load_generic('data/vinci_2009/authors.json')

        self.load_data_vinci()

        autores_vinci = self.autores_vinci.values()
        autores_2009 = self.authors.values()

        new_authors = {}

        for autorB  in autores_2009:

            name_compare = autorB['name'].lower()
            new_authors[autorB['id']] = autorB
            new_authors[autorB['id']]['url'] = ''
            for autorA in autores_vinci:
                original = autorA['name'].lower()
                if name_compare == original:
                    print(autorB)
                    newid = autorA['id']
                    oldid = autorB['id']
                    data = autorA
                    del new_authors[oldid]
                    new_authors[newid] = data
                    break;

        return  new_authors

    def merge_data_2(self, new_auths):
        res1 = new_auths | self.autores_vinci
        #save_generic('data/jsons/authors_update.json', res1)

        reverse_auth = {}
        for id, list in res1.items():
            name = list['name']
            reverse_auth[name] = list

        for doi, list in self.papers_acm.items():
            autores_string = list['authors']
            newlist = []
            for autor in autores_string:
                find = reverse_auth[autor]
                newlist.append(find)

            self.papers_acm[doi]['authors'] = newlist


        res2 = self.papers_acm | self.papers_vinci
        save_generic('data/jsons/papers_update.json', res2)

        pass

    def merge_data (self, new_auths):
        all_papers = load_generic('data/vinci_refs/nodes.json')

        papers_2009 = {}
        for doi, list in self.papers_acm.items():
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
            papers_2009[doi] = data

        res1 = papers_2009 | all_papers
        print(res1)

        authors_2009 = {}
        authors_vinci = {}

        for id, list in new_auths.items():
            #print(list)
            institutos = list['institutions'] if 'institutions' in list else []
            list_names = []
            for insti in institutos:
                list_names.append(insti['name'])

            data = {
                'id': list['id'],
                'name': list['name'],
                'institutions': institutos,
                'url': list['url']
            }
            authors_2009[id] = data

        for id, list in self.autores_vinci.items():
            #print(list)
            institutos = list['institutions'] if 'institutions' in list else []
            list_names = []
            for insti in institutos:
                list_names.append(insti['name'])

            data = {
                'id': list['id'],
                'name': list['name'],
                'institutions': institutos,
                'url': list['url']
            }
            authors_vinci[id] = data


        res2= authors_2009 | authors_vinci
        print(res2)


        list1 = res1.values()
        papers_col = ['type', 'title', 'url', 'year', 'authors', 'conference', 'id', 'is_vinci']
        csv_generics('data/vinci_2009/papers.csv', list1, papers_col)

        list2 = res2.values()
        authors_col = ['id', 'name', 'institutions', 'url']
        #csv_generics('data/vinci_2009/authors.csv', list2, authors_col)

    def main(self):
        #self.extract_page_for_acm()
        #self.save_info()
        #self.driver_for_acm.get("https://dl.acm.org/profile/99660628905")

        #self.extract_info_springer()
        #self.save_info()
        #new_auths = self.extract_authors()
        #self.merge_data(new_auths)
        #self.merge_data_2(new_auths)

        self.get_papers_vinci_info()

if __name__ == '__main__':

    client = SpringerClient()
    client.main()