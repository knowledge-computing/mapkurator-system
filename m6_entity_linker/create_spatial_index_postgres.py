from dotenv import load_dotenv
import psycopg2


load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

conn = psycopg2.connect(database=DB_NAME, host=DB_HOST, user=DB_USERNAME, password=DB_PASSWORD, port=DB_PORT)

continents = ['africa', 'asia', 'central_america', 'north_america', 'south_america', 'antarctica', 'australia_oceania', 'europe']
tables = ['points', 'lines', 'multilinestrings','multipolygons','other_relations']

for continent in continents:
    for table in tables:
        name = continent + "." + table
        cur.execute(f'''CREATE INDEX {name.replace(".","_")+"_index"} ON {name} USING gist (wkb_geometry);''')
        cur.execute(f'''CREATE INDEX {name.replace(".","_")+"_osm_index"} ON {name} (osm_id);''')
        print(name, " creating index...")
    
conn.commit()
cur.close()
conn.close()
