from flask_restful import Api, Resource, reqparse
from flask import Flask
import pandas as pd
import re

app = Flask(__name__)
api = Api(app)
regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"

def find_string(file_name, word):
   with open(file_name, 'r') as a:
       for line in a:
           line = line.rstrip()
           if re.search(r"\b{}\b".format(word),line):
             return True
   return False

class InfoFetch(Resource):
    def get(self):
        data = pd.read_csv('dvcsetups.csv')
        data = data.to_dict('records')
        return {'data' : data}, 200


    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('MAC', required=True, location='args')
        parser.add_argument('IP', required=True, location='args')
        args = parser.parse_args()

        data = pd.read_csv('dvcsetups.csv')
        try:
            new_data = pd.DataFrame({
                'MAC': [':'.join(format(s, '02x') for s in bytes.fromhex(args['MAC']))],
                'IP': [args['IP']],
            })
            if (re.search(regex, args['IP'])):
                print("Valid Ip address")

                if find_string('dvcsetups.csv', ':'.join(format(s, '02x') for s in bytes.fromhex(args['MAC']))) or find_string('dvcsetups.csv', args['IP']):
                    print("found")
                    return {'Error': "Data Already Present"}, 201
                else:
                    print("not found")
                    data = data.append(new_data, ignore_index=True)
                    data.to_csv('dvcsetups.csv', index=False)
                    return {'data': new_data.to_dict('records')}, 201
            else:
                print("Invalid Ip address")
                return {'Error': "IP ADDRESS IS NOT VALID"}, 201
        except:
            print("Invalid Mac")
            return {'Error': "MAC ADDRESS IS NOT VALID"}, 201



    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('IP', required=True, location='args')
        args = parser.parse_args()
        data = pd.read_csv('dvcsetups.csv')
        data = data[data['IP'] != args['IP']]
        data.to_csv('dvcsetups.csv', index=False)
        return {'message' : 'Record deleted successfully.'}, 200


# Add URL endpoints
api.add_resource(InfoFetch,'/dvc')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4011)