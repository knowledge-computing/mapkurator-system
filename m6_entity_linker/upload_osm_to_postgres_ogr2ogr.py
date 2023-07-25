from dotenv import load_dotenv
import subprocess
import os

import psycopg2

continents = ['africa', 'asia', 'centeral_america', 'north_america', 'south_america', 'antarctica', 'australia_oceania', 'europe']

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


try:
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USERNAME, password=DB_PASSWORD)
except:
    logging.warning('Error on psycopg2 connection while running %s', geojson_file.split("/")[-1])

cur = conn.cursor()

for continent in continents:
    cur.execute(f'''CREATE SCHEMA {continent};''')
    print(continent, " creating schema...")

conn.commit()
cur.close()
conn.close()

for continent in continents:
    cmd = f'''ogr2ogr -f PostgreSQL PG:"dbname='{DB_NAME}' host='{DB_HOST}' port='{DB_PORT}' user='{DB_USERNAME}' password='{DB_PASSWORD}'" {continent.replace('_','-')}-latest.osm.pbf -nlt PROMOTE_TO_MULTI -lco SCHEMA={continent}'''
    print("--", continent, "--")
    print(cmd)
    subprocess.call(cmd, shell=True)