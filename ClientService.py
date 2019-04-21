import os
import re
import time

from requests import get
from multiprocessing import Pool


class ClientService:
    def __init__(self, index_builder, filepath, base_url, num_servers):
        self._result = {}
        self._index_builder = index_builder
        self._filepath = filepath
        self._base_url = base_url
        self._num_servers = num_servers

    def _process_snaps(self):
        index_builder = self._index_builder

        if not os.path.isdir(self._filepath):
            raise FileNotFoundError("The specified directory '{}' doesn't exist".format(self._filepath))

        pattern = re.compile('.*\.jpg')
        filenames = [os.path.join(self._filepath, f) for f in os.listdir(self._filepath)
                     if os.path.isfile(os.path.join(self._filepath, f)) and pattern.findall(f)]

        fp_vectors = {}
        for i in range(self._num_servers):
            fp_vectors[i] = []

        for filename in filenames:
            fid = os.path.split(filename)[-1].split('.')[0].split('_')[2]
            fp, vector = index_builder.finger_print(filename)
            fp_vectors[fp % self._num_servers].append((fid, fp, vector))

        return fp_vectors

    @staticmethod
    def _hit_api(url, fp_vectors):
        result_dict = {}
        key = 'result'
        for fid, fp, vector in fp_vectors:
            response = get(url, params={'fp': fp, 'vector': vector}).json()

            if key in response.keys():
                result_dict[fid] = response[key]

        return result_dict

    def _merge_responses(self, response):
        self._result.update(response)

    def run(self):
        fp_vectors = self._process_snaps()

        pool = Pool(processes=self._num_servers)

        start_time = time.time()
        for i in range(self._num_servers):
            pool.apply_async(func=self._hit_api, args=(self._base_url.format(8000 + i), fp_vectors[i],),
                             callback=self._merge_responses)

        pool.close()
        pool.join()

        print('Time taken {0}'.format(time.time() - start_time))

        return list(self._result.values())
