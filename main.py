import config
from common_functions import *
from list_papers import *
from get_extra_info import *

dblp_base_url = 'https://dblp.org/db/conf/vinci/index.html'

def load_all_conferences():
    """
    - Buscamos todos los enlaces de ACM de vinci dentro dblp.org
    """
    try:
        # 1 - create drivers for each database
        driver_for_dblp = make_chrome_headless()  # True hides automated browser
        print("Driver for DBLP is ready.")
        # 2 - driver visits links
        driver_for_dblp.get(dblp_base_url)
        # 3 - parse source code
        soup = BeautifulSoup(driver_for_dblp.page_source, "html.parser")
        uls = soup.findAll("ul", class_="publ-list")
        # 4 - Get the result containers
        result_containers = soup.findAll("li", class_="ee")
        # 5 - check href
        hrefs = []
        file_path = create_file(config.path_to_search_results, 'conferences')
        with open(str(file_path), "w", encoding="UTF8", newline="") as f:
            # create the csv writer
            writer = csv.writer(f)
            # write the header
            #writer.writerow(['urls'])
            for li, ul in zip(result_containers, uls):
                id_conference = ul.next_element.attrs['id']
                id_split = id_conference.split('/')
                conf_age = id_split[len(id_split)-1]
                href = li.find("a").attrs['href']
                title = ul.find('span', {'class': 'title'}).text
                publisher = ul.find(attrs={"itemprop": "publisher"})
                datepublished = ul.find(attrs={"itemprop": "datePublished"})
                isbn = ul.find(attrs={"itemprop": "isbn"})
                isbn = '' if isbn is None else isbn.text
                publisher = '' if publisher is None else publisher.text
                if datepublished.text == '':
                    idsplit = id.split('/')
                    datepublished = idsplit[len(idsplit)-1]
                else:
                    datepublished = datepublished.text

                data = ['vinci', conf_age, href, title, publisher, datepublished, isbn]
                hrefs.append(data)
                writer.writerow(data)
        return hrefs
    except Exception as e:
        fail_message(e)
        driver_for_dblp.quit()


def main():
    value = check_if_exist_file(config.path_to_search_results, 'conferences')
    data = []
    if value:
        data = get_data_conferences()
    else:
        data = load_all_conferences()

    print(data)
    #papers_client = AcmClient(data)
    #papers_client.main_fun()
    extra_info_client = Info(data)
    #extra_info_client.main_fun()
    #extra_info_client.get_authors()
    #extra_info_client.get_institutions()
    extra_info_client.loop_authors()
    print('Finish')




if __name__ == "__main__":
    main()