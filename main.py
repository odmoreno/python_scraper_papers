import config
from common_functions import *

"""
Vinci 2021,
Vinci 2020
"""
list_of_conference = [
    'https://dl.acm.org/doi/proceedings/10.1145/3481549',
    'https://dl.acm.org/doi/proceedings/10.1145/3430036'
]

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
        # 4 - Get the result containers
        result_containers = soup.findAll("li", class_="ee")
        # 5 - check href
        hrefs = []
        file_path = create_file(config.path_to_search_results, 'conferences')
        with open(str(file_path), "w", encoding="UTF8", newline="") as f:
            # create the csv writer
            writer = csv.writer(f)
            # write the header
            writer.writerow(['urls'])
            for li in result_containers:
                href = li.find("a").attrs['href']
                hrefs.append(href)
                data = [href]
                writer.writerow(data)
        return  hrefs
    except Exception as e:
        fail_message(e)


def main():
    value = check_if_exist_file(config.path_to_search_results, 'conferences')
    data = []
    if value:
        with open('data/conferences.csv', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                data.append(row[0])
    else:
        data = load_all_conferences()

    print(data)
    print('Finish')




if __name__ == "__main__":
    main()