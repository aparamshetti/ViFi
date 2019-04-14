import json

from flask import request
from flask_restful import reqparse, Resource
import numpy as np

# setup a request parser for parsing the query parameters
parser = reqparse.RequestParser()
parser.add_argument('fp', type=str, required=True)
parser.add_argument('vector', type=float, required=True, action='append')


# TODO: Need to decide on the similarity threshold
class SearchService(Resource):
    def __init__(self, indexer_filepath):
        with open(indexer_filepath, 'r') as f:
            self._indexer = json.loads(f.read())

    @staticmethod
    # query is assumed to be a tuple of type (finger print, vector)
    def _cosine_similarity(self,query):
        if query[0] in self._indexer:
            vector_list = self._indexer[query[0]]
        else:
            return [()]
        
        result = []
        for ele in vector_list:
            cosine_similarity = np.sum(np.multiply(ele[1],query[1]))/(np.linalg.norm(ele[1])*np.linalg.norm(query[1]))
            result.append((ele[0],cosine_similarity))
    
        return result

    def get(self):
        args = parser.parse_args()
        fp = args.get('fp')
        vector = request.args.getlist('vector')
        if fp in self._indexer:
            # TODO: traverse through the list of vectors corresponding to the given fingerprint
            # find the frame with highest cosine similarity or
            # frames with cosine similarity greater than a decided threshold
            result = True
        else:
            result = False

        return {'fp': result}
