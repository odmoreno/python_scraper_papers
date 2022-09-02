from common_functions import *

class AcmClient:
    def __init__(self,urls):
        self.base_url = "https://dl.acm.org"
        self.list_urls = urls
        self.driver_for_acm = make_chrome_headless()

    def get_data_papers(self, tipo, contenido):
        # Result title
        title_tmp = contenido.find("h5").text
        title = title_tmp.strip("'")
        journal = contenido.find("div", class_="issue-item__detail").a["title"]
        # Result url
        temp_url = contenido.find("h5").a["href"]
        lst = ["https:/",temp_url[:4],".org",temp_url[4:],]
        url = "".join(lst)
        # Result date
        date = (
            contenido.find("div", class_="issue-item__detail")
            .find("span", class_="dot-separator")
            .find("span")
            .text.rstrip(", ")
        )
        numbers = re.compile(r"\d+(?:\.\d+)?")
        p_year = numbers.findall(date)[0]
        # Result authors
        authors = []
        ul = contenido.find("ul")
        for li in ul.findAll("li"):  # list of authors
            authors.append(li.text.rstrip(", \n").strip("'"))
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
            "journal": journal,
            "authors": author_list,
            "citations": n_citation,
            "downloads": n_descargas
        }
        return  data

    def main_fun(self):
        try:
            for url in self.list_urls:
                # get the name of conference
                name = url[0] + '_' + url[1]
                # Check if exist path of json
                flag_path = check_if_exist_file_json(config.path_to_search_results, name)
                if not flag_path:
                    self.driver_for_acm.get(url[2])
                    # parse source code
                    soup = BeautifulSoup(self.driver_for_acm.page_source, "html.parser")
                    # Get the result containers
                    result_containers = soup.findAll("div", class_="issue-item clearfix")
                    item_citation = soup.findAll("div", class_="issue-heading")
                    item_content = soup.findAll("div", class_="issue-item__content")
                    #loop and search for results
                    #for citation, content in (item_citation, item_content):
                    for citation, content in (item_citation, item_content):
                        tipo_de_paper = citation.find('div', {'class': 'issue-heading'}).text
                        contenido = content.find('div', {'class': 'issue-item__content-right'})
                        data = self.get_data_papers(tipo_de_paper, contenido)

                else:
                    print('Ya existe :', name)

        except Exception as e:
            fail_message(e)
            self.driver_for_acm.quit()

