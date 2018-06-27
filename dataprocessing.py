from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch import helpers
from requests_aws4auth import AWS4Auth
import os

AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']
region = 'ap-northeast-2'
service = 'es'

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, service)

host = os.environ['AWS_ES_HOST']
# ex) tojung.search.net

es = Elasticsearch(
 hosts = [{'host': host, 'port': 443}],
 http_auth = awsauth,
 use_ssl = True,
 verify_certs = True,
 connection_class = RequestsHttpConnection
)

def bulk_insert(datas):
    actions = [
        {
            "_index": "korbill",
            "_type": "bill",
            "_id": data['id'],
            "_source": data
        }
        for data in datas
    ]

    helpers.bulk(es, actions)
