import pandas as pd
import json
from collections import defaultdict
import datetime

def parse_excel_to_json():
    
    try:
        df = pd.read_excel('data.xlsx', header=None)
    except FileNotFoundError:
        print("Ошибка: файл data.xlsx не найден!")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return
    
    headers = df.iloc[0].tolist()
    metadata = df.iloc[1].tolist()
    data_rows = df.iloc[2:].copy()
    data_rows.columns = headers
    turnover_max_score = metadata[6]
    losses_max_score = metadata[12]
    shortages_max_score = metadata[13]
    fop_max_score = metadata[14]
    shift_remainder_max_score = metadata[15]
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
    for _, row in data_rows.iterrows():
        if pd.isna(row.iloc[0]) or pd.isna(row.iloc[5]):
            continue
        week_id = str(row.iloc[0])
        region_name = str(row.iloc[1])
        region_id = str(row.iloc[2])
        region_color = str(row.iloc[3])
        store_name = str(row.iloc[4])
        store_id = str(row.iloc[5])
        plan = float(row.iloc[6]) if not pd.isna(row.iloc[6]) else 0.0
        fact = float(row.iloc[7]) if not pd.isna(row.iloc[7]) else 0.0
        losses = float(row.iloc[8]) if not pd.isna(row.iloc[8]) else 0.0
        shortages = float(row.iloc[9]) if not pd.isna(row.iloc[9]) else 0.0
        fop = float(row.iloc[10]) if not pd.isna(row.iloc[10]) else 0.0
        shift_remainder = float(row.iloc[11]) if not pd.isna(row.iloc[11]) else 0.0
        losses_target = round(float(row.iloc[12]), 4) if not pd.isna(row.iloc[12]) else 0.0
        shortages_target = round(float(row.iloc[13]), 4) if not pd.isna(row.iloc[13]) else 0.0
        fop_target = round(float(row.iloc[14]), 4) if not pd.isna(row.iloc[14]) else 0.0
        shift_remainder_target = round(float(row.iloc[15]), 4) if not pd.isna(row.iloc[15]) else 0.0
        weeks_set.add(week_id)
        if regions_data[region_id]['id'] == '':
            regions_data[region_id]['id'] = region_id
            regions_data[region_id]['name'] = region_name
            regions_data[region_id]['color'] = region_color
        if regions_data[region_id]['stores'][store_id]['id'] == '':
            regions_data[region_id]['stores'][store_id]['id'] = store_id
            regions_data[region_id]['stores'][store_id]['name'] = store_name
        percent = fact / plan if plan != 0 else 0
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
        if store_id not in store_targets:
            store_targets[store_id] = {
                "losses": losses_target,
                "shortages": shortages_target,
                "fop": fop_target,
                "shiftRemainder": shift_remainder_target,
                "unprocessed": 0,
                "store": store_name
            }
    weeks_list = sorted(list(weeks_set))
    weeks_output = []
    for week_id in weeks_list:
        week_name = week_id
        date_range = generate_date_range(week_id)
        weeks_output.append({
            "id": week_id,
            "name": week_name,
            "dateRange": date_range
        })
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
    output_data = {
        "weeks": weeks_output,
        "regions": regions_output
    }
    targets_data = {
        "targetTree": {
            "turnover": {
                "name": "Оборот",
                "maxScore": int(turnover_max_score) if not pd.isna(turnover_max_score) else 100,
                "type": "positive"
            },
            "losses": {
                "name": "Списання",
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
                "name": "Повернення",
                "maxScore": int(shift_remainder_max_score) if not pd.isna(shift_remainder_max_score) else 10,
                "type": "negative"
            }
        },
        "storeTargets": store_targets
    }
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
    if "1" in week_id:
        return ""
    elif "2" in week_id:
        return ""
    else:
        return f""

if __name__ == "__main__":
    print("Начинаем парсинг Excel файла...")
    parse_excel_to_json()
    print("Парсинг завершен!")