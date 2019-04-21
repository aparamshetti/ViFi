import os
import re
import json

from flask import Flask
from flask_restful import Api
from multiprocessing import Process
from SearchService import SearchService


class StartSearchServices:
    def __init__(self, indexer_filepaths):
        self._indexer_filepaths = indexer_filepaths
        print('Starting service!!')

    @staticmethod
    def _start(port, filepath):
        with open(filepath, 'r') as f:
            indexer = json.loads(f.read())

        app = Flask(__name__)
        api = Api(app)

        api.add_resource(SearchService, '/search', resource_class_kwargs={'indexer': indexer})
        app.run(port=port)

    # spawn multiple processes to run the search service
    def start_services(self):
        processes = []
        for i, filepath in enumerate(self._indexer_filepaths):
            if not os.path.isfile(filepath):
                print("The indexer file '{}' doesn't exist!".format(filepath))
                continue

            t = Process(target=StartSearchServices._start, args=(8000 + i, filepath,))
            processes.append(t)
            t.start()

        for one_process in processes:
            one_process.join()


if __name__ == '__main__':
    dict_path = 'master'
    pattern = re.compile('server_.*\.json')
    StartSearchServices([os.path.join(dict_path, f) for f in os.listdir(dict_path)
                         if os.path.isfile(os.path.join(dict_path, f))]).start_services()

    #  Run the following lines of code to make sure the services are running fine
    # from requests import get
    #
    # response = get('http://localhost:8000/search', params={'fp': '3114119', 'vector': [1.123, 1213.2, 4412.321]})
    # response.json()
    # response = get('http://localhost:8001/search', params={'fp': '3114119', 'vector': [1.123, 1213.2, 4412.321]})
    # response.json()
    # response = get('http://localhost:8001/search', params={'fp': '3114119'})
    # response.json()
