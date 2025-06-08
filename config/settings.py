import os
from dotenv import load_dotenv

load_dotenv()

WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
TOKEN = os.getenv("BOT_TOKEN")

ERA_RANGES = {
    'ancient_rus': {'start': '0800', 'end': '1547', 'name': 'Древняя Русь (IX-XVI вв.)'},
    'tsar_rus': {'start': '1547', 'end': '1721', 'name': 'Царская Россия (XVI-XVIII вв.)'},
    'imperial': {'start': '1721', 'end': '1917', 'name': 'Императорская Россия (XVIII-XX вв.)'},
    'soviet': {'start': '1917', 'end': '1991', 'name': 'Советский период (1917-1991)'},
    'modern': {'start': '1991', 'end': '2025', 'name': 'Наше время (с 1991)'}
}