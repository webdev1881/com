import pandas as pd
import json
from datetime import datetime, timedelta
from collections import defaultdict
import sys
import os

def parse_week_info(week_data):
    """
    Извлекает информацию о неделе из данных
    """
    weeks_info = {}
    unique_weeks = week_data.unique()
    
    for i, week_id in enumerate(sorted(unique_weeks)):
        if pd.isna(week_id):
            continue
            
        # Генерируем информацию о периоде
        period_num = i + 1
        period_id = f"period_{period_num}"
        
        # Генерируем даты для периода (примерные)
        # В реальном проекте логику нужно адаптировать под ваши данные
        current_year = datetime.now().year
        start_date = datetime(current_year, 1, 1) + timedelta(weeks=period_num-1)
        end_date = start_date + timedelta(days=6)
        
        weeks_info[week_id] = {
            "id": period_id,
            "name": period_id,
            "dateRange": f"{start_date.strftime('%d.%m.%y')} - {end_date.strftime('%d.%m.%y')}"
        }
    
    return weeks_info

def calculate_percent(plan, fact):
    """
    Вычисляет процент выполнения плана
    """
    if pd.isna(plan) or pd.isna(fact) or plan == 0:
        return 0
    return fact / plan

def parse_targets_json(df, output_targets_path):
    """
    Создает JSON файл с целевыми показателями
    """
    try:
        # Читаем вторую строку как метаданные
        if len(df) < 2:
            print("Недостаточно строк для обработки целевых показателей")
            return
            
        metadata_row = df.iloc[1]  # Вторая строка (индекс 1)
        
        # Основные показатели (столбцы 9-12, индексы 8-11)
        base_indicators = ['losses', 'shortages', 'fop', 'shiftRemainder']
        
        # Создаем targetTree
        target_tree = {}
        
        # Добавляем turnover (maxScore из столбца 7, индекс 6, строка 2)
        turnover_max_score = 100  # По умолчанию
        try:
            turnover_value = metadata_row.iloc[6]  # Столбец 7, строка 2
            if not pd.isna(turnover_value):
                turnover_max_score = float(turnover_value)
        except:
            pass
                
        target_tree['turnover'] = {
            'name': 'Оборот',
            'maxScore': turnover_max_score,
            'type': 'positive'
        }
        
        # Названия показателей
        indicator_names = {
            'losses': 'Списання ТМЦ',
            'shortages': 'Нестачі', 
            'fop': 'ФОП',
            'shiftRemainder': 'Непровед. списання'
        }
        
        # maxScore показателей из второй строки (столбцы 13-16, индексы 12-15)
        max_scores = []
        for i in range(4):  # 4 показателя
            col_index = 12 + i  # столбцы 13-16
            try:
                if col_index < len(metadata_row):
                    value = metadata_row.iloc[col_index]
                    if not pd.isna(value):
                        max_scores.append(float(value))
                    else:
                        max_scores.append(0)
                else:
                    max_scores.append(0)
            except:
                max_scores.append(0)
        
        # Добавляем показатели с правильными maxScore и типом "negative"
        for i, indicator_name in enumerate(base_indicators):
            display_name = indicator_names.get(indicator_name, indicator_name.title())
            
            target_tree[indicator_name] = {
                'name': display_name,
                'maxScore': max_scores[i],
                'type': 'negative'
            }
        
        # Создаем storeTargets
        store_targets = {}
        
        # Обрабатываем данные магазинов (начиная с 3 строки, индекс 2)
        for idx in range(2, len(df)):  # Начинаем с 3 строки
            row = df.iloc[idx]
            
            if pd.isna(row.iloc[5]):  # Проверяем store_id (столбец 6)
                continue
                
            store_id = str(row.iloc[5])  # Используем реальный store_id из столбца 6
            store_name = str(row.iloc[4]) if not pd.isna(row.iloc[4]) else f"Магазин {store_id}"
            
            # Создаем данные для магазина
            store_data = {
                'store': store_name
            }
            
            # Добавляем целевые показатели из столбцов 13-16 (индексы 12-15)
            for i, indicator_name in enumerate(base_indicators):
                target_col_index = 12 + i  # столбцы 13-16
                
                target_value = 0
                if target_col_index < len(row):
                    try:
                        target_val = row.iloc[target_col_index]
                        if not pd.isna(target_val):
                            target_value = float(target_val)
                    except:
                        pass
                        
                store_data[indicator_name] = target_value
            
            # Добавляем unprocessed если его нет
            if 'unprocessed' not in store_data:
                store_data['unprocessed'] = 0
                
            store_targets[store_id] = store_data  # Используем реальный store_id как ключ
        
        # Создаем финальную структуру
        targets_result = {
            'targetTree': target_tree,
            'storeTargets': store_targets
        }
        
        # Сохраняем в JSON файл
        with open(output_targets_path, 'w', encoding='utf-8') as f:
            json.dump(targets_result, f, ensure_ascii=False, indent=2)
        
        print(f"Файл целевых показателей создан: {output_targets_path}")
        print(f"Обработано показателей: {len(target_tree)}")
        print(f"Обработано магазинов: {len(store_targets)}")
        
        return targets_result
        
    except Exception as e:
        print(f"Ошибка при создании файла целевых показателей: {str(e)}")
        return None
def parse_excel_to_json(excel_file_path, output_json_path):
    """
    Основная функция парсинга Excel файла в JSON
    """
    try:
        # Читаем Excel файл
        print(f"Читаю файл: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        # Проверяем количество столбцов
        if len(df.columns) < 12:
            print(f"Внимание: В файле {len(df.columns)} столбцов, ожидается минимум 12")
        
        # Присваиваем названия столбцам согласно описанию
        column_names = [
            'weekId', 'region_name', 'region_id', 'region_color', 
            'stores_name', 'store_id', 'plan', 'fact', 
            'losses', 'shortages', 'fop', 'shiftRemainder'
        ]
        
        # Переименовываем столбцы
        for i, col_name in enumerate(column_names):
            if i < len(df.columns):
                df.rename(columns={df.columns[i]: col_name}, inplace=True)
        
        # Пропускаем первые 2 строки (заголовок и метаданные) для основных данных
        # Но сначала сохраняем их для обработки
        header_df = df.copy()
        
        # Удаляем первые 2 строки для основной обработки
        df_data = df.iloc[2:].copy()  # Начинаем с 3 строки
        
        # Удаляем строки с пустыми значениями в ключевых столбцах
        df_data = df_data.dropna(subset=['region_id', 'store_id'])
        
        print(f"Обработано {len(df_data)} строк данных")
        
        # Получаем информацию о неделях
        weeks_info = parse_week_info(df_data['weekId'])
        
        # Создаем маппинг для period_id
        week_to_period = {}
        for original_week, week_info in weeks_info.items():
            week_to_period[original_week] = week_info['id']
        
        # Группируем данные по регионам
        regions_data = defaultdict(lambda: {
            'stores': defaultdict(lambda: {
                'weeklyData': []
            })
        })
        
        # Создаем счетчики для store_id
        store_id_mapping = {}
        store_counter = 1
        
        # Обрабатываем каждую строку данных
        for _, row in df_data.iterrows():
            region_id = str(row['region_id'])  # Убираем добавление "region_" так как оно уже есть в данных
            original_store_id = str(row['store_id'])
            week_id = row['weekId']
            
            # Создаем уникальный store_id
            if original_store_id not in store_id_mapping:
                store_id_mapping[original_store_id] = f"store_{store_counter}"
                store_counter += 1
            
            store_id = store_id_mapping[original_store_id]
            
            # Определяем period_id
            period_id = week_to_period.get(week_id, "period_1")
            
            # Заполняем данные региона
            if 'id' not in regions_data[region_id]:
                regions_data[region_id].update({
                    'id': region_id,  # region_id уже содержит полный ID типа "region_2"
                    'name': str(row['region_name']) if not pd.isna(row['region_name']) else f"Регион {region_id}",
                    'color': str(row['region_color']) if not pd.isna(row['region_color']) else "#000000"
                })
            
            # Заполняем данные магазина
            store_data = regions_data[region_id]['stores'][store_id]
            if 'id' not in store_data:
                store_data.update({
                    'id': store_id,
                    'name': str(row['stores_name']) if not pd.isna(row['stores_name']) else f"Магазин {store_id}"
                })
            
            # Добавляем недельные данные
            plan = float(row['plan']) if not pd.isna(row['plan']) else 0
            fact = float(row['fact']) if not pd.isna(row['fact']) else 0
            
            weekly_data = {
                'weekId': period_id,
                'plan': plan,
                'fact': fact,
                'percent': calculate_percent(plan, fact),
                'losses': float(row['losses']) if not pd.isna(row['losses']) else 0,
                'shortages': float(row['shortages']) if not pd.isna(row['shortages']) else 0,
                'fop': float(row['fop']) if not pd.isna(row['fop']) else 0,
                'shiftRemainder': float(row['shiftRemainder']) if not pd.isna(row['shiftRemainder']) else 0,
                'unprocessed': 0  # По умолчанию 0, можно изменить логику
            }
            
            store_data['weeklyData'].append(weekly_data)
        
        # Преобразуем в финальную структуру
        result = {
            'weeks': list(reversed(list(weeks_info.values()))),
            'regions': {}
        }
        
        for region_id, region_data in regions_data.items():
            stores_list = []
            for store_id, store_data in region_data['stores'].items():
                stores_list.append({
                    'id': store_data['id'],
                    'name': store_data['name'],
                    'weeklyData': store_data['weeklyData']
                })
            
            result['regions'][region_id] = {
                'id': region_id,  # region_id уже содержит полный ID типа "region_2"
                'name': region_data['name'],
                'color': region_data['color'],
                'stores': stores_list
            }
        
        # Сохраняем в JSON файл
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"JSON файл успешно создан: {output_json_path}")
        print(f"Обработано регионов: {len(result['regions'])}")
        print(f"Обработано недель: {len(result['weeks'])}")
        
        return result, header_df
        
    except Exception as e:
        print(f"Ошибка при обработке файла: {str(e)}")
        return None, None

def main():
    """
    Главная функция
    """
    # Настройки файлов
    excel_file = "data.xlsx"  # Путь к вашему Excel файлу
    json_file = "output.json"  # Путь к выходному JSON файлу
    targets_file = "targets.json"  # Путь к файлу целевых показателей
    
    # Проверяем существование входного файла
    if not os.path.exists(excel_file):
        print(f"Файл {excel_file} не найден!")
        print("Пожалуйста, поместите Excel файл в папку со скриптом и назовите его 'data.xlsx'")
        print("Или измените путь к файлу в переменной excel_file")
        return
    
    # Парсим основной файл
    result, header_df = parse_excel_to_json(excel_file, json_file)
    
    if result and header_df is not None:
        print("Основной JSON создан успешно!")
        
        # Создаем файл целевых показателей
        targets_result = parse_targets_json(header_df, targets_file)
        
        if targets_result:
            print("Файл целевых показателей создан успешно!")
            print("Обработка завершена!")
        else:
            print("Ошибка при создании файла целевых показателей")
    else:
        print("Произошла ошибка при обработке основного файла")

if __name__ == "__main__":
    main()