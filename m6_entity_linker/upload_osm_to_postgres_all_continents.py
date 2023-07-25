from dotenv import load_dotenv
import psycopg2


load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

conn = psycopg2.connect(database=DB_NAME, host=DB_HOST, user=DB_USERNAME, password=DB_PASSWORD, port=DB_PORT)
cur = conn.cursor()
cur.execute('''CREATE TABLE entire_continents (
    ogc_fid SERIAL PRIMARY KEY,
    osm_id character varying,
    name character varying,
    source_table character varying
    );''')


continents = ['africa', 'asia', 'central_america', 'north_america', 'south_america', 'antarctica', 'australia_oceania', 'europe']
tables = ['points', 'lines', 'multilinestrings','multipolygons','other_relations']

for continent in continents:
    for table in tables:
        name = continent + "." + table
        cur.execute(f'''INSERT INTO entire_continents(osm_id, name, source_table)
        SELECT osm_id, name, '{name}' FROM {name}
        WHERE name IS NOT NULL AND osm_id IS NOT NULL ;''')
        print(name, " inserting into entire_continents...")
    
conn.commit()
cur.close()
conn.close()