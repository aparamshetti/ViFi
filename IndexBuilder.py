import re
import cv2
import time
import json
import pickle
import numpy as np

from os import path
from os import listdir
from collections import defaultdict

from keras import backend
from keras import Model
from keras.models import load_model


class IndexBuilder:
    # TODO: move all the model related code to the VectorTransformation file
    def __init__(self, model_filepath, input_dir, index_dir, layer_name='vector_layer', dtype='float16'):
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

    def _index_builder(self):
        with open('resources/matrix.pkl', 'rb') as f:
            matrix = pickle.load(f)

        with open('resources/vector.pkl', 'rb') as f:
            vector = pickle.load(f)

        for i, img in enumerate(self._images):
            vec = self._vectorize(img).reshape(1, 1131).dot(matrix)
            fp = int(np.dot(vec, vector))
            name = path.split(img)[-1]
            if fp in self._inverted_index:
                self._inverted_index[fp].append((name, vec[0].tolist()))
            else:
                self._inverted_index[fp] = [(name, vec[0].tolist())]
            if (i + 1) % 1000 == 0:
                with open(path.join(self._index_dir + "inverted_index{}.json".format(i // 1000)), 'w') as f:
                    json.dump(self._inverted_index, f)

                print("Completed: ", i)

                self._inverted_index.clear()

        with open(path.join(self._index_dir, "inverted_index{}.json".format((len(self._images) // 1000) + 1)), 'w') as f:
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

    def _merge_inverted_indices(self):
        if not path.isdir(self._index_dir):
            raise FileNotFoundError("The specified input dir '{}' doesn't exist.".format(self._input_dir))

        pattern = re.compile('inverted_index.*\.json', re.IGNORECASE)
        index_files = [path.join(self._index_dir, f) for f in listdir(self._index_dir)
                       if path.isfile(path.join(self._index_dir, f)) and pattern.findall(f)]

        merged_inverted_index = defaultdict(list)

        for d in [json.loads(open(f, 'r').read()) for f in index_files]:
            for key, value in d.items():
                merged_inverted_index[key].extend(value)

        with open(path.join(self._index_dir, 'inverted_index.json'), 'w') as f:
            json.dump(dict(merged_inverted_index), f)

    def run(self):
        self._load_input_image_filenames()
        self._load_model()
        self._index_builder()
        self._merge_inverted_indices()


if __name__ == '__main__':
    base_url = 'data'

    start_time = time.time()
    IndexBuilder('model.h5', base_url + '/snapshots', 'resources').run()
    print('total time taken {}'.format(time.time() - start_time))
