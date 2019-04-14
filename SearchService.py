import json

from flask import request
from flask_restful import reqparse, Resource

# setup a request parser for parsing the query parameters
parser = reqparse.RequestParser()
parser.add_argument('fp', type=str, required=True)
parser.add_argument('vector', type=float, required=True, action='append')


# TODO: Need to decide on the similarity threshold
class SearchService(Resource):
    def __init__(self, indexer_filepath):
        with open(indexer_filepath, 'r') as f:
            self._indexer = json.loads(f.read())

    # TODO: Add code to find the cosine similarity
    @staticmethod
    def _cosine_similarity(frame, vector):
        # frame - the frame in the indexer
        # vector - the vector in the query
        # Have some logic ready for this, will complete and push -- Jason
        
        return vector

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
