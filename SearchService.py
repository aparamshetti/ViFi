import json
import flask
import numpy as np

from flask import request, session
from flask_restful import reqparse, Resource

# setup a request parser for parsing the query parameters
parser = reqparse.RequestParser()
parser.add_argument('fp', type=str, required=True)
parser.add_argument('vector', type=float, required=True, action='append')


class SearchService(Resource):
    def __init__(self, indexer):
        self._indexer = indexer

    @staticmethod
    def _cosine_similarity(query, vector):
        return np.dot(query, vector) / (np.sqrt(np.dot(query, query)) * np.sqrt(np.dot(vector, vector)))

    def get(self):
        args = parser.parse_args()
        fp = args.get('fp')
        vector = [float(ele) for ele in request.args.getlist('vector')]
        result = []
        if fp in self._indexer:
            for frame in self._indexer[fp]:
                video_id = frame[0].split('_')[0]
                result.append((video_id, self._cosine_similarity(vector, frame[1])))

        return {"result": result}
