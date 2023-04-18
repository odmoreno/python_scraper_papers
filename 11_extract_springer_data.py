from common_functions import *
import json
import time
import pandas as pd

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

        # Coauthoria
        self.coauthors = {}
        self.coinsti = {}
        self.copais = {}
        self.coregion = {}
        self.coauthors_col = ['el1', 'el2', 'paper_doi', 'date']
        self.coinsti_col = ['el1', 'el2', 'paper_doi', 'date']
        self.copais_col = ['el1', 'el2', 'paper_doi', 'date']
        self.coregion_col = ['el1', 'el2', 'paper_doi', 'date']


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
        self.papers_vinci = load_generic('data/vinci_2009/papers_update.json')
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
                if title == 'Digital Artwork Creation Using Water and Sand on a Two-Dimensional Surface':
                    print('a')
                    pass

                for autor in autores:
                    instituto = autor['institution']
                    if title == 'National Chiao Tung University, Taiwan':
                        print('a')
                    if year == '2009':
                        name = instituto[0]['name']
                        id_insti = instituto[0]['id']
                        element = self.institutos_vinci[id_insti]
                        data = self.extract_info_2009(element['name'], element)
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
        save_generic('data/vinci_refs/nodes2.json', res1)

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
        #papers_col = ['type', 'title', 'url', 'year', 'authors', 'conference', 'id', 'is_vinci']
        #csv_generics('data/vinci_2009/papers.csv', list1, papers_col)

        list2 = res2.values()
        authors_col = ['id', 'name', 'institutions', 'url']
        #csv_generics('data/vinci_2009/authors.csv', list2, authors_col)



    def loop_coauthorship(self):
        panama_papers = load_generic('data/vinci_2009/papers_vinci.json')
        try:
            for doi, element in panama_papers.items():
                authors = element['authors']
                afilitions = element['afilitions']
                countries = element['countries']
                regions = element['regions']
                date = element['year']

                afilitions = list(set(afilitions))
                countries = list(set(countries))
                regions = list(set(regions))

                self.create_links_authors(doi, date, authors)
                self.loop_institutions(doi, date, afilitions)
                self.loop_countries(doi,date,countries)
                self.loop_regions(doi, date, regions)
        except Exception as e:
            print(doi, element)
            fail_message(e)

        save_generic('data/vinci_2009/co-authorship_people.json', self.coauthors)
        save_generic('data/vinci_2009/co-authorship_afilitions.json', self.coinsti)
        save_generic('data/vinci_2009/co-authorship_countries.json', self.copais)
        save_generic('data/vinci_2009/co-authorship_regions.json', self.coregion)
        csv_generics('data/vinci_2009/co-authorship_people.csv', self.coauthors.values(), self.coauthors_col)
        csv_generics('data/vinci_2009/co-authorship_afilitions.csv', self.coinsti.values(), self.coinsti_col)
        csv_generics('data/vinci_2009/co-authorship_countries.csv', self.copais.values(), self.copais_col)
        csv_generics('data/vinci_2009/co-authorship_regions.csv', self.coregion.values(), self.coregion_col)

    def create_links_authors(self, doi, date, authors):
        j = 1
        for author in authors:
            for i in range(j, len(authors)):
                element = authors[i]
                cod = author + '_ ' + element + '_ ' + doi
                icod = element + '_ ' + author + '_ ' + doi
                if (cod not in self.coauthors) and (icod not in self.coauthors):
                    data = {
                        'el1': author,
                        'el2': element,
                        'paper_doi': doi,
                        'date': date
                    }
                    self.coauthors[cod] = data
            j +=1

    def loop_institutions(self, doi, date, afilitions):
        j=1
        for insti in afilitions:
            for i in range(j, len(afilitions)):
                element = afilitions[i]
                cod = insti + '_ ' + element + '_ ' + doi
                icod = element + '_ ' + insti + '_ ' + doi
                if (cod not in self.coinsti) and (icod not in self.coinsti):
                    data = {
                        'el1': insti,
                        'el2': element,
                        'paper_doi': doi,
                        'date': date
                    }
                    self.coinsti[cod] = data
            j += 1

    def loop_countries(self, doi, date, countries):
        j=1
        for co1 in countries:
            for i in range(j, len(countries)):
                co2 = countries[i]
                cod = co1 + '_ ' + co2 + '_ ' + doi
                icod = co2 + '_ ' + co1 + '_ ' + doi
                if (cod not in self.copais) and (icod not in self.copais):
                    data = {
                        'el1': co1,
                        'el2': co2,
                        'paper_doi': doi,
                        'date': date
                    }
                    self.copais[cod] = data
            j +=1

    def loop_regions(self, doi, date, regions):
        j=1
        for co1 in regions:
            for i in range(j, len(regions)):
                co2 = regions[i]
                cod = co1 + '_ ' + co2 + '_ ' + doi
                icod = co2 + '_ ' + co1 + '_ ' + doi
                if (cod not in self.coregion) and (icod not in self.coregion):
                    data = {
                        'el1': co1,
                        'el2': co2,
                        'paper_doi': doi,
                        'date': date
                    }
                    self.coregion[cod] = data
            j +=1

    def get_acum_coauthorship(self, path, mainfolder, key, name):
        years = [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
        hash = load_generic(path)
        elements = list(hash.values())
        elements = sorted(elements, key=lambda d: d['date'])
        links = {}
        for year in years:
            filtered = [d for d in elements if int(d['date']) == year]
            for element in filtered:
                id = element['el1'] + '_' + element['el2']
                if id in links:
                    el = links[id]
                    value = el['value'] + 1
                    data = {
                        'e1': element['el1'],
                        'e2': element['el2'],
                        'value': value
                    }
                    links[id] = data
                else:
                    data = {
                        'e1': element['el1'],
                        'e2': element['el2'],
                        'value': 1
                    }
                    links[id] = data
            print('fin:', year)
            path = mainfolder + key + name + str(year) +'.csv'
            csv_generics(path, links.values(), ['e1', 'e2', 'value'])

    def extract_by_year(self):
        mainfolder =  'data/coauthor/'
        path1 = 'data/vinci_2009/co-authorship_countries.json'
        path2 = 'data/vinci_2009/co-authorship_people.json'
        path3 = 'data/vinci_2009/co-authorship_afilitions.json'
        path4 = 'data/vinci_2009/co-authorship_regions.json'
        self.get_acum_coauthorship(path1, mainfolder, 'co_pais/', 'co_authorship_countries_')
        self.get_acum_coauthorship(path2, mainfolder, 'co_people/', 'co_authorship_people_')
        self.get_acum_coauthorship(path3, mainfolder, 'co_insti/', 'co_authorship_afilitions_')
        self.get_acum_coauthorship(path4, mainfolder, 'co_region/', 'co_authorship_regions_')

    def extract_authors_vinci(self):
        authors_csv = load_csv('data/vinci_2009/authors.csv')
        print(authors_csv)
        authors = {}
        for raw in authors_csv:
            list_raw = raw['institutions']
            list_raw = list_raw.replace("'", '')
            res = list_raw.strip('][').split(', ')
            raw['institutions'] = res
            authors[raw['name']] = raw
        pass
        print(authors)
        save_generic('data/vinci_refs/authors.json', authors)



    def main(self):
        self.papers_acm = load_generic('data/vinci_2009/papers_acm.json')

        #self.extract_page_for_acm()
        #self.save_info()
        #self.driver_for_acm.get("https://dl.acm.org/profile/99660628905")

        #self.extract_info_springer()
        #self.save_info()
        #new_auths = self.extract_authors()

        #self.merge_data(new_auths)

        #self.merge_data_2(new_auths)

        self.get_papers_vinci_info()

        self.loop_coauthorship()

        self.extract_by_year()

        self.extract_authors_vinci()

if __name__ == '__main__':

    client = SpringerClient()
    client.main()