import re
import cv2
import time
import json
import pickle
import numpy as np
import glob

import os
from os import path
from os import listdir
from collections import defaultdict

from keras import backend
from keras import Model
from keras.models import load_model


class IndexBuilder:
    # TODO: move all the model related code to the VectorTransformation file
    def __init__(self, model_filepath, input_dir, resource_dir, layer_name='vector_layer', dtype='float16'):
        self._base = os.path.dirname(os.path.realpath(__file__))
        self._model_filepath = model_filepath
        self._input_dir = input_dir
        self._resource_dir = resource_dir
        self._layer_name = layer_name
        self._model = None
        backend.set_floatx(dtype)

        self._load_model()
        self._load_vectors()

    def _vectorize(self, image):
        return self._model.predict(cv2.imread(image).reshape(1, 640, 480, 3)).flatten()

    def finger_print(self, image):
        vector = self._vectorize(image).reshape(1, 1131).dot(self._matrix)
        fp = int(np.dot(vector, self._vector))
        return fp, vector[0].tolist()

    def _index_builder(self, video_path):
        images = self._load_image_filenames(video_path)
        inverted_index = {}

        for i, img in enumerate(images):
            fp, vector = self.finger_print(img)
            name = path.split(img)[-1]
            if fp in inverted_index:
                inverted_index[fp].append((name, vector))
            else:
                inverted_index[fp] = [(name, vector)]
        print("Completed: ", len(images))

        return inverted_index

    def _load_image_filenames(self, filepath):
        if not os.path.isdir(filepath):
            raise FileNotFoundError("The specified directory '{}' doesn't exist".format(filepath))

        pattern = re.compile('.*\.jpg')
        return [os.path.join(filepath, f) for f in listdir(filepath)
                if os.path.isfile(os.path.join(filepath, f)) and pattern.findall(f)]

    def _load_model(self):
        if not path.isfile(self._model_filepath):
            raise FileNotFoundError("The specified model file '{}' doesn't exist".format(self._model_filepath))

        # load the bottle-neck layer of the model
        model = load_model(self._model_filepath)
        self._model = Model(inputs=model.input, outputs=model.get_layer(self._layer_name).output)

    def _load_vectors(self):
        with open(self._resource_dir + '/matrix.pkl', 'rb') as f:
            self._matrix = pickle.load(f)

        with open(self._resource_dir + '/vector.pkl', 'rb') as f:
            self._vector = pickle.load(f)

    def _merge_inverted_indices(self, index_files, write_path):
        merged_inverted_index = defaultdict(list)

        dictionaries = []
        for f in index_files:
            with open(f, "r") as read_file:
                dictionaries.append(json.load(read_file))
            
        for d in dictionaries:
            for key, value in d.items():
                merged_inverted_index[key].extend(value)

        with open(path.join(self._base, write_path, "inverted_index_master.json"), 'w') as f:
            json.dump(dict(merged_inverted_index), f)
    
    def _build_multiple_indexes(self):
        video_directories = os.listdir(self._input_dir)
        resource_path = path.join(self._resource_dir, "dictionaries")
        if not os.path.isdir(resource_path):
            os.mkdir(resource_path)
        
        for video in video_directories:
            dict_path = os.path.join(resource_path, video)
            if not os.path.isdir(dict_path): 
                os.mkdir(dict_path)
            video_path = os.path.join(self._input_dir, video)
            inverted_index = self._index_builder(video_path)

            with open(path.join(dict_path, "inverted_index_submaster.json"), 'w') as f:
                json.dump(inverted_index, f)

    def _create_master_index(self, relative_path):
        
        dict_directories = [os.path.join(self._base, relative_path, x) for x in os.listdir(relative_path)
                            if os.path.isdir(os.path.join(relative_path, x))]
        index_files = []
        for d in dict_directories:
            index_files.extend(glob.glob(d + "\\*submaster.json"))
    
        self._merge_inverted_indices(index_files, relative_path)
        
        if not os.path.isdir("master"):
            os.mkdir("master")

    # master path needs to be relative to data path and is a directory
    @staticmethod
    def _create_n_dictionaries(master_path, write_path, number_of_servers=6):
        if not path.isdir(master_path):
            raise FileNotFoundError("The specified input dir '{}' doesn't exist.".format(master_path))
        
        master_dictionary_path = glob.glob(master_path+"//*master.json")[0]

        if not path.isdir(master_path):
            raise FileNotFoundError("No master file exists in {}".format(master_path))

        with open(master_dictionary_path, 'r') as f:
            master_dictionary = json.load(f)
                
        split_dict = [{} for _ in range(number_of_servers)]
        
        for key, val in master_dictionary.items():
            i = int(key) % number_of_servers
            split_dict[i][key] = val
        
        for i, d in enumerate(split_dict):
            with open(path.join(write_path, "server_{}.json".format(i)), 'w') as f:
                json.dump(d, f)

    def run(self):
        self._build_multiple_indexes()
        self._create_master_index(self._resource_dir + "/dictionaries/")
        self._create_n_dictionaries("resources/dictionaries/", "master", number_of_servers=2)


if __name__ == '__main__':
    base_url = 'data'

    start_time = time.time()
    IndexBuilder('model.h5', base_url + '\snapshots', 'resources').run()
    print('total time taken {}'.format(time.time() - start_time))
