'''
Extraer informacion de las ref segun la pagina del publisher
'''

from common_functions import *
import time
import json

class Refs:

    def __init__(self):

        self.driver = make_chrome_headless()
        self.pub_list_path = 'data/jsons/publishers.json'
        self.ref_papers_tmp_path = 'data/jsons/ref_papers_tmp.json'
        self.ref_papers_tmp_dict = {}
        self.pub_list ={}

    def load_data(self):
        with open(self.ref_papers_tmp_path, encoding='utf-8') as fh:
            papers = json.load(fh)
        self.ref_papers_tmp_dict = papers

    def save_generic(self, path, collection):
        json_string = json.dumps(collection, ensure_ascii=False, indent=2)
        with open(path, 'w', encoding="utf-8") as outfile:
            outfile.write(json_string)

    def get_info_tmp_ref(self):
        #main fun
        try:
            for key in self.ref_papers_tmp_dict:
                self.detect_url(key)
            self.save_generic(self.pub_list_path, self.pub_list)
        except Exception as e:
            print(key)
            fail_message(e)

    def detect_url(self, key):
        paper = self.ref_papers_tmp_dict[key]
        url = paper['url']
        self.driver.get(url)
        time.sleep(2)
        print(self.driver.current_url)
        self.save_publisher(self.driver.current_url)

    def save_publisher(self, url):
        new_url = url.replace('https://', '')
        url_split = new_url.split('/')
        publisher_name = url_split[0]
        if publisher_name not in self.pub_list:
            self.pub_list[publisher_name] = {'name': publisher_name, "example": url}
            self.save_generic(self.pub_list_path, self.pub_list)

if __name__ == '__main__':
    client = Refs()
    client.load_data()
    client.get_info_tmp_ref()