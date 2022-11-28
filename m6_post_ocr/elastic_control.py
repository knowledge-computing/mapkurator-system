from elasticsearch_dsl import Search, Q
from elasticsearch import Elasticsearch, helpers
from elasticsearch import RequestsHttpConnection

from dotenv import load_dotenv
import os


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
USER_NAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")

es = Elasticsearch([DB_HOST], connection_class=RequestsHttpConnection, http_auth=(USER_NAME, PASSWORD), verify_certs=False)
# es.index(index='testaa')

es.indices.delete(index='osm')