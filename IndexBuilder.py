import re
import cv2
import time
import json
import pickle
import numpy as np
import glob

from shutil import copyfile
import os
from os import path
from os import listdir
from os import walk
from collections import defaultdict

from keras import backend
from keras import Model
from keras.models import load_model


class IndexBuilder:
    # TODO: move all the model related code to the VectorTransformation file
    def __init__(self, model_filepath, input_dir, index_dir, layer_name='vector_layer', dtype='float16'):
        self._base = os.path.dirname(os.path.realpath(__file__))
        self._model_filepath = model_filepath
        self._input_dir = input_dir
        self._index_dir = index_dir
        self._layer_name = layer_name
        self._model = None
        self._images = []
        self._inverted_index = {}
        backend.set_floatx(dtype)

    def _vectorize(self, image):
        return self._model.predict(cv2.imread(image).reshape(1, 640, 480, 3)).flatten()

    def _finger_print(self,img):
        with open('resources/matrix.pkl', 'rb') as f:
            matrix = pickle.load(f)
        
        with open('resources/vector.pkl', 'rb') as f:
            vector = pickle.load(f)
            
        vec = self._vectorize(img).reshape(1, 1131).dot(matrix)
        return int(np.dot(vec, vector))
        
    
    
        
    def _index_builder(self,file_path,video_path):
        with open('resources/matrix.pkl', 'rb') as f:
            matrix = pickle.load(f)

        with open('resources/vector.pkl', 'rb') as f:
            vector = pickle.load(f)

        images = glob.glob(video_path+"/*.jpg")

        for i, img in enumerate(images):
            vec = self._vectorize(img).reshape(1, 1131).dot(matrix)
            fp = int(np.dot(vec, vector))
            name = path.split(img)[-1]
            if fp in self._inverted_index:
                self._inverted_index[fp].append((name, vec[0].tolist()))
            else:
                self._inverted_index[fp] = [(name, vec[0].tolist())]
# =============================================================================
#             if (i + 1) % 1000 == 0:
#                 with open(path.join(file_path + "inverted_index{}.json".format(i // 1000)), 'w') as f:
#                     json.dump(self._inverted_index, f)
# =============================================================================

                #self._inverted_index.clear()
            print("Completed: ", i)

        with open(path.join(file_path, "inverted_index_{}.json").format("_submaster"), 'w') as f:
            json.dump(self._inverted_index, f)
            self._inverted_index.clear()

    def _load_input_image_filenames(self):
        if not path.isdir(self._input_dir):
            raise FileNotFoundError("The specified input dir '{}' doesn't exist.".format(self._input_dir))

        # get the list of images from the input directory
        pattern = re.compile('.*\.jpg', re.IGNORECASE)
        self._images.extend([path.join(self._input_dir, f) for f in listdir(self._input_dir)
                             if path.isfile(path.join(self._input_dir, f)) and pattern.findall(f)])

    def _load_model(self):
        if not path.isfile(self._model_filepath):
            raise FileNotFoundError("The specified model file '{}' doesn't exist".format(self._model_filepath))

        # load the bottle-neck layer of the model
        model = load_model(self._model_filepath)
        self._model = Model(inputs=model.input, outputs=model.get_layer(self._layer_name).output)

    def _merge_inverted_indices(self,index_files,write_path):
# =============================================================================
#         if not path.isdir(file_path):
#             raise FileNotFoundError("The specified input dir '{}' doesn't exist.".format(file_path))
#         
#         
#         pattern = re.compile('inverted_index.*\.json', re.IGNORECASE)
#         index_files = [path.join(file_path, f) for f in listdir(file_path)
#                        if path.isfile(path.join(file_path, f)) and pattern.findall(f)]
# =============================================================================

        merged_inverted_index = defaultdict(list)

        dictionaries = []
        for f in index_files:
            with open(f, "r") as read_file:
                dictionaries.append(json.load(read_file))
            
        for d in dictionaries:
            for key, value in d.items():
                merged_inverted_index[key].extend(value)

        with open(path.join(self._base,write_path, "inverted_index_master.json"), 'w') as f:
            json.dump(dict(merged_inverted_index), f)
    
    def _build_multiple_indexes(self):
        
        video_directories = os.listdir(self._input_dir)
        resource_path = path.join(self._index_dir,"dictionaries\\")
        if not os.path.isdir(resource_path):
            os.mkdir(resource_path)
        
        for video in video_directories:
            dict_path = os.path.join(resource_path,video) 
            if not os.path.isdir(dict_path): 
                os.mkdir(dict_path)
            video_path = os.path.join(self._input_dir,video)
            self._index_builder(dict_path, video_path)
            
    def _create_master_index(self,relative_path):
        
        dict_directories = [os.path.join(self._base,relative_path,x) for x in os.listdir(relative_path) if os.path.isdir(os.path.join(relative_path,x))]
        index_files = []
        for d in dict_directories:
            index_files.extend(glob.glob(d+"\\*submaster.json"))
    
        self._merge_inverted_indices(index_files,relative_path)      
        
        if not os.path.isdir("master"):
            os.mkdir("master")
                
        print(glob.glob(relative_path+"*master.json")[0])
        print(os.path.join(self._base,"master\\"))
        
        copyfile(glob.glob(relative_path+"*master.json")[0],os.path.join(self._base,"master\\inverted_index_final_master.json"))
        
    #master path needs to be relative to data path and is a directory
    def _create_n_dictionaries(self,master_path,number_of_servers=6):
        if not path.isdir(master_path):
            raise FileNotFoundError("The specified input dir '{}' doesn't exist.".format(master_path))
        
        master_dictionary_path = glob.glob(master_path+"//*master.json")[0]
    
        try:
            with open(master_dictionary_path,'r') as f:
                master_dictionary = json.load(f)
        except:
            raise FileNotFoundError("No master file exists in {}".format(master_path))
                
                
        split_dict = [{} for _ in range(number_of_servers)]
        
        for key,val in master_dictionary.items():
            i = int(key) % number_of_servers
            split_dict[i][key] = val
        
        for i, d in enumerate(split_dict):
            with open(path.join(master_path, "server_{}.json".format(i+1)), 'w') as f:
                json.dump(d, f)
            
    
    def run(self):
        self._load_input_image_filenames()
        self._load_model()
        self._build_multiple_indexes()
        self._create_master_index(self._index_dir+"\\dictionaries\\")
        self._create_n_dictionaries("master")


if __name__ == '__main__':
    base_url = 'data'

    start_time = time.time()
    IndexBuilder('model.h5', base_url + '\snapshots', 'resources').run()
    print('total time taken {}'.format(time.time() - start_time))
    
    
    
    
    