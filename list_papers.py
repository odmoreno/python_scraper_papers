from common_functions import *
import json

class AcmClient:
    def __init__(self,urls):
        self.base_url = "https://dl.acm.org"
        self.list_urls = urls
        self.driver_for_acm = make_chrome_headless()

    def save_data_to_json(self, name, data):
        filename = 'data/' + name + '.json'
        json_string = json.dumps(data, indent=2)
        # Using a JSON string
        with open(filename, 'w') as outfile:
            outfile.write(json_string)


    def get_data_papers(self, tipo, contenido):
        # Result title
        title_tmp = contenido.find("h5").text
        title = title_tmp.strip("'")
        """
        journal_temp = contenido.find("div", class_="issue-item__detail")
        journal = journal_temp.find("a")
        """
        # Result url
        temp_url = contenido.find("h5").a["href"]
        lst = ["https:/",temp_url[:4],".org",temp_url[4:],]
        url = "".join(lst)
        # Get DOI
        doi = temp_url[5:]
        # Result date
        allspans = contenido.find("div", class_="issue-item__detail").findAll("span")
        texts = []
        for span in allspans:
            contenttext = span.text.rstrip(", ")
            texts.append(contenttext)
        date = texts[0]
        numbers = re.compile(r"\d+(?:\.\d+)?")
        p_year = numbers.findall(date)[0]
        # Result authors
        authors = []

        ul = contenido.find("ul")

        for li in ul.findAll("li"):  # list of authors
            name = li.text.rstrip(", \n").strip("'")
            temp_urlname = li.a["href"]
            lst = ["https:/", "dl.acm", ".org", temp_urlname, ]
            urlname = "".join(lst)
            dataauthor = {
                "name": name,
                "url": urlname
            }
            authors.append(dataauthor)
            #authors.append(li.text.rstrip(", \n").strip("'"))

        t_author_list = str(authors).strip("[]")
        author_list = t_author_list.replace("'", "")
        # Citation
        n_citation = contenido.find("div", class_="citation").find('span').text
        # Downloads
        n_descargas = contenido.find("div", class_="metric").find('span').text
        data = {
            "type": tipo,
            "title" : title,
            "url" : url,
            "year": p_year,
            #"journal": journal,
            "authors": author_list,
            "citations": n_citation,
            "downloads": n_descargas,
            "doi" : doi,
            "extra": texts
        }
        return data

    def get_info_conference(self, content):

        pass


    def main_fun(self):
        try:
            for url in self.list_urls:
                # get the name of conference
                name = url[0] + '_' + url[1]
                conference = {}
                # Check if exist path of json
                flag_path = check_if_exist_file_json(config.path_to_search_results, name)
                if not flag_path:
                    self.driver_for_acm.get(url[2])
                    # parse source code
                    soup = BeautifulSoup(self.driver_for_acm.page_source, "html.parser")
                    '''
                    #find buttons
                    liss = self.driver_for_acm.find_elements_by_class_name('removed-items-count')
                    for a in liss:
                        a.click()
                    '''
                    # Get info of conference
                    meta_info = soup.find("div", class_="item-meta__info")

                    # Get the result containers
                    result_containers = soup.findAll("div", class_="issue-item clearfix")
                    item_citation = soup.findAll("div", class_="issue-heading")
                    item_content = soup.findAll("div", class_="issue-item__content")
                    #loop and search for results
                    for index in range(len(item_content)):

                        citation = item_citation[index]
                        tipo_de_paper = citation.text
                        contenido = item_content[index].find('div', {'class': 'issue-item__content-right'})
                        data = self.get_data_papers(tipo_de_paper, contenido)
                        conference[data['doi']] = data

                    self.save_data_to_json(name, conference)
                    """
                     for citation, content in (item_citation, item_content):
                        tipo_de_paper = citation.find('div', {'class': 'issue-heading'}).text
                        contenido = content.find('div', {'class': 'issue-item__content-right'})
                        data = self.get_data_papers(tipo_de_paper, contenido)
                    """

                else:
                    print('Ya existe :', name)

        except Exception as e:
            fail_message(e)
            self.driver_for_acm.quit()

