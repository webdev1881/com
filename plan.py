import pandas as pd
import json
from collections import defaultdict
import datetime

def parse_excel_to_json():
    """
    Парсит Excel файл data.xlsx и создает два JSON файла:
    - output.json: данные по неделям, регионам и магазинам
    - targets.json: целевые показатели и метаданные
    """
    
    # Читаем Excel файл
    try:
        df = pd.read_excel('data.xlsx', header=None)
    except FileNotFoundError:
        print("Ошибка: файл data.xlsx не найден!")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return
    
    # Получаем заголовки из первой строки
    headers = df.iloc[0].tolist()
    
    # Получаем метаданные из второй строки
    metadata = df.iloc[1].tolist()
    
    # Получаем данные (строки 3+)
    data_rows = df.iloc[2:].copy()
    data_rows.columns = headers
    
    # Извлекаем метаданные
    turnover_max_score = metadata[6]  # Столбец 7 (индекс 6)
    
    # maxScore для показателей из столбцов 13-16 (индексы 12-15)
    losses_max_score = metadata[12]
    shortages_max_score = metadata[13]
    fop_max_score = metadata[14]
    shift_remainder_max_score = metadata[15]
    
    # Создаем структуру данных
    weeks_set = set()
    regions_data = defaultdict(lambda: {
        'id': '',
        'name': '',
        'color': '',
        'stores': defaultdict(lambda: {
            'id': '',
            'name': '',
            'weeklyData': []
        })
    })
    
    store_targets = {}
    
    # Обрабатываем каждую строку данных
    for _, row in data_rows.iterrows():
        # Пропускаем строки с пустыми данными
        if pd.isna(row.iloc[0]) or pd.isna(row.iloc[5]):
            continue
            
        week_id = str(row.iloc[0])  # periodData
        region_name = str(row.iloc[1])  # region_name
        region_id = str(row.iloc[2])  # region_id
        region_color = str(row.iloc[3])  # region_color
        store_name = str(row.iloc[4])  # stores_name
        store_id = str(row.iloc[5])  # store_id
        plan = float(row.iloc[6]) if not pd.isna(row.iloc[6]) else 0.0  # Plan
        fact = float(row.iloc[7]) if not pd.isna(row.iloc[7]) else 0.0  # Fact
        losses = float(row.iloc[8]) if not pd.isna(row.iloc[8]) else 0.0  # losses
        shortages = float(row.iloc[9]) if not pd.isna(row.iloc[9]) else 0.0  # shortages
        fop = float(row.iloc[10]) if not pd.isna(row.iloc[10]) else 0.0  # fop
        shift_remainder = float(row.iloc[11]) if not pd.isna(row.iloc[11]) else 0.0  # shiftRemainder
        
        # Вспомогательные данные из столбцов 13-16 для storeTargets
        losses_target = float(row.iloc[12]) if not pd.isna(row.iloc[12]) else 0.0  # losses (вспомогательные)
        shortages_target = float(row.iloc[13]) if not pd.isna(row.iloc[13]) else 0.0  # shortages (вспомогательные)
        fop_target = float(row.iloc[14]) if not pd.isna(row.iloc[14]) else 0.0  # fop (вспомогательные)
        shift_remainder_target = float(row.iloc[15]) if not pd.isna(row.iloc[15]) else 0.0  # shiftRemainder (вспомогательные)
        
        # Добавляем неделю
        weeks_set.add(week_id)
        
        # Заполняем данные региона
        if regions_data[region_id]['id'] == '':
            regions_data[region_id]['id'] = region_id
            regions_data[region_id]['name'] = region_name
            regions_data[region_id]['color'] = region_color
        
        # Заполняем данные магазина
        if regions_data[region_id]['stores'][store_id]['id'] == '':
            regions_data[region_id]['stores'][store_id]['id'] = store_id
            regions_data[region_id]['stores'][store_id]['name'] = store_name
        
        # Вычисляем percent
        percent = fact / plan if plan != 0 else 0
        
        # Добавляем недельные данные
        weekly_data = {
            "weekId": week_id,
            "plan": plan,
            "fact": fact,
            "percent": percent,
            "losses": losses,
            "shortages": shortages,
            "fop": fop,
            "shiftRemainder": shift_remainder,
            "unprocessed": 0
        }
        
        regions_data[region_id]['stores'][store_id]['weeklyData'].append(weekly_data)
        
        # Сохраняем целевые показатели для магазина (из вспомогательных столбцов 13-16)
        if store_id not in store_targets:
            store_targets[store_id] = {
                "losses": losses_target,
                "shortages": shortages_target,
                "fop": fop_target,
                "shiftRemainder": shift_remainder_target,
                "unprocessed": 0,
                "store": store_name
            }
    
    # Создаем список недель (в прямом порядке)
    weeks_list = sorted(list(weeks_set))
    weeks_output = []
    
    for week_id in weeks_list:
        # Генерируем примерные даты (можно настроить под ваши нужды)
        week_name = week_id
        date_range = generate_date_range(week_id)
        
        weeks_output.append({
            "id": week_id,
            "name": week_name,
            "dateRange": date_range
        })
    
    # Преобразуем структуру данных для выходного формата
    regions_output = {}
    for region_id, region_data in regions_data.items():
        stores_list = []
        for store_id, store_data in region_data['stores'].items():
            stores_list.append({
                "id": store_data['id'],
                "name": store_data['name'],
                "weeklyData": store_data['weeklyData']
            })
        
        regions_output[region_id] = {
            "id": region_data['id'],
            "name": region_data['name'],
            "color": region_data['color'],
            "stores": stores_list
        }
    
    # Формируем output.json
    output_data = {
        "weeks": weeks_output,
        "regions": regions_output
    }
    
    # Формируем targets.json
    targets_data = {
        "targetTree": {
            "turnover": {
                "name": "Оборот",
                "maxScore": int(turnover_max_score) if not pd.isna(turnover_max_score) else 100,
                "type": "positive"
            },
            "losses": {
                "name": "Списання ТМЦ",
                "maxScore": int(losses_max_score) if not pd.isna(losses_max_score) else 20,
                "type": "negative"
            },
            "shortages": {
                "name": "Нестачі",
                "maxScore": int(shortages_max_score) if not pd.isna(shortages_max_score) else 100,
                "type": "negative"
            },
            "fop": {
                "name": "ФОП",
                "maxScore": int(fop_max_score) if not pd.isna(fop_max_score) else 15,
                "type": "negative"
            },
            "shiftRemainder": {
                "name": "Непровед. списання",
                "maxScore": int(shift_remainder_max_score) if not pd.isna(shift_remainder_max_score) else 10,
                "type": "negative"
            }
        },
        "storeTargets": store_targets
    }
    
    # Записываем JSON файлы
    try:
        with open('output.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print("Файл output.json успешно создан!")
        
        with open('targets.json', 'w', encoding='utf-8') as f:
            json.dump(targets_data, f, ensure_ascii=False, indent=2)
        print("Файл targets.json успешно создан!")
        
    except Exception as e:
        print(f"Ошибка при записи JSON файлов: {e}")

def generate_date_range(week_id):
    """
    Генерирует диапазон дат для недели.
    Можно настроить под ваши нужды.
    """
    # Простая логика генерации дат на основе week_id
    # Можно изменить под ваши требования
    if "period_1" in week_id:
        return "08.01.25 - 14.01.25"
    elif "period_2" in week_id:
        return "01.01.25 - 07.01.25"
    else:
        # Генерируем произвольную дату
        return f"01.01.25 - 07.01.25"

if __name__ == "__main__":
    print("Начинаем парсинг Excel файла...")
    parse_excel_to_json()
    print("Парсинг завершен!")