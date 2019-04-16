import json
from re import match

from flask import request
from flask_restful import reqparse, Resource
import numpy as np

# setup a request parser for parsing the query parameters
parser = reqparse.RequestParser()
parser.add_argument('fp', type=str, required=True)
parser.add_argument('vector', type=float, required=True, action='append')


class SearchService(Resource):
    def __init__(self, indexer_filepath):
        with open(indexer_filepath, 'r') as f:
            self._indexer = json.loads(f.read())

    @staticmethod
    def _cosine_similarity(query, vector):
        return np.dot(query, vector) / (np.sqrt(np.dot(query, query)) * np.sqrt(np.dot(vector, vector)))

    def get(self):
        args = parser.parse_args()
        fp = args.get('fp')
        vector = np.array(request.args.getlist('vector'), dtype=np.float16)
        matching_video_id = None
        max_cosine_similarity = None
        if fp in self._indexer:
            for frame in self._indexer[fp]:
                cosine_similarity = self._cosine_similarity(vector, frame[1])
                if max_cosine_similarity is None or cosine_similarity > max_cosine_similarity:
                    max_cosine_similarity = cosine_similarity
                    matching_video_id = frame[0].split('_')[0]

        return {"matching_video_id": matching_video_id}
