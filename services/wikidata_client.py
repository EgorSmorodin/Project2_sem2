import requests
import html
import random
from datetime import datetime
from typing import List, Dict, Set, Optional
from config.settings import WIKIDATA_API_URL, WIKIDATA_SPARQL_URL, ERA_RANGES
from storage.user_data import user_data
import logging

logger = logging.getLogger(__name__)


async def get_city_wikidata_id(city_name: str) -> Optional[str]:
    try:
        params = {
            'action': 'wbsearchentities',
            'format': 'json',
            'language': 'ru',
            'type': 'item',
            'search': city_name
        }
        response = requests.get(WIKIDATA_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data['search'][0]['id'] if data.get('search') else None
    except Exception as e:
        logger.error(f"Error getting Wikidata ID for city {city_name}: {e}")
        return None


async def get_events_from_wikidata(city_id: str, era: str, exclude_events: Set[str] = None) -> List[Dict]:
    try:
        range_data = ERA_RANGES[era]
        query = f"""
            SELECT ?event ?eventLabel ?date ?description WHERE {{
              ?event wdt:P31 wd:Q1190554;
                    wdt:P585 ?date;
                    wdt:P276/wdt:P131* wd:{city_id}.
              OPTIONAL {{ ?event schema:description ?description FILTER(LANG(?description) = "ru") }}
              FILTER(?date >= "{range_data['start']}-01-01"^^xsd:dateTime)
              FILTER(?date <= "{range_data['end']}-12-31"^^xsd:dateTime)
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],ru". }}
            }}
            ORDER BY ?date
            LIMIT 50
        """
        headers = {'Accept': 'application/sparql-results+json'}
        response = requests.get(WIKIDATA_SPARQL_URL, params={'query': query}, headers=headers)
        response.raise_for_status()
        data = response.json()

        events = []
        for result in data.get('results', {}).get('bindings', []):
            event = {
                'label': result.get('eventLabel', {}).get('value', 'Неизвестное событие'),
                'date': result.get('date', {}).get('value', 'Неизвестная дата'),
                'description': result.get('description', {}).get('value', '')
            }
            if exclude_events is None or event['label'] not in exclude_events:
                events.append(event)
        return events
    except Exception as e:
        logger.error(f"Error getting events from Wikidata: {e}")
        return []


async def get_historical_event(user_id: int) -> str:
    try:
        if user_id not in user_data or 'city' not in user_data[user_id]:
            return "❌ Сначала настройте город и эпоху через меню"

        city = user_data[user_id]['city']
        era = user_data[user_id]['era']
        city_id = user_data[user_id].get('city_id')

        if not city_id:
            city_id = await get_city_wikidata_id(city)
            if city_id:
                user_data[user_id]['city_id'] = city_id

        if not city_id:
            return f"❌ Не удалось найти информацию о городе {city}"

        shown_events = user_data[user_id].get('shown_events', set())
        events = await get_events_from_wikidata(city_id, era, shown_events)

        if not events:
            if shown_events:
                return f"ℹ️ Все события для {city} в этом периоде уже показаны"
            return f"❌ Не найдено событий для {city} в выбранный период"

        event = random.choice(events)

        if 'shown_events' not in user_data[user_id]:
            user_data[user_id]['shown_events'] = set()
        user_data[user_id]['shown_events'].add(event['label'])

        try:
            date_obj = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%d.%m.%Y')
        except:
            formatted_date = event['date']

        message = f"<b>📅 {html.escape(formatted_date)}</b>\n\n"
        message += f"<b>📜 {html.escape(event['label'])}</b>\n"

        if event.get('description'):
            message += f"\n📝 {html.escape(event['description'])}\n"

        message += f"\n🏙 {html.escape(city)}\n"

        return message

    except Exception as e:
        logger.error(f"Error in get_historical_event: {e}")
        return "❌ Ошибка при получении события. Попробуйте позже."