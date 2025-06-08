def format_era_name(era_key: str) -> str:
    era_names = {
        'ancient_rus': 'Древняя Русь (IX-XVI вв.)',
        'tsar_rus': 'Царская Россия (XVI-XVIII вв.)',
        'imperial': 'Императорская Россия (XVIII-XX вв.)',
        'soviet': 'Советский период (1917-1991)',
        'modern': 'Наше время (с 1991)'
    }
    return era_names.get(era_key, era_key)