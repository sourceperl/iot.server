#!/usr/bin/env python3

import http.client
import json

connection = http.client.HTTPConnection('localhost', port=5000)
headers = {'Content-type': 'application/json'}
connection.request('GET', '/data/set/field1?value=42', headers=headers)
response = connection.getresponse().read()

d = json.loads(response.decode())
print('set field1 at value %s' % d['data']['field1']['value'])
