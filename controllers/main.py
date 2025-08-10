# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging
import os

_logger = logging.getLogger(__name__)


class VueController(http.Controller):
    """
    Контроллер для Vue.js интеграции
    Предоставляет API для взаимодействия Vue приложения с Odoo
    """
    
    @http.route('/vue/api/data', type='json', auth='user', methods=['POST'])
    def get_vue_data(self, model=None, domain=None, fields=None, limit=50, **kwargs):
        """Универсальный API для получения данных из Odoo"""
        try:
            if not model:
                model = 'res.users'
            
            if not fields:
                fields = ['id', 'name', 'create_date']
            
            if not domain:
                domain = []
            
            # Проверяем права доступа
            if not request.env[model].check_access_rights('read', raise_exception=False):
                return {
                    'success': False,
                    'error': 'Недостаточно прав для чтения модели ' + model
                }
            
            # Получаем данные
            records = request.env[model].search_read(
                domain, fields, limit=limit
            )
            
            return {
                'success': True,
                'data': records,
                'count': len(records)
            }
            
        except Exception as e:
            _logger.error(f"Ошибка в get_vue_data: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/vue/api/create', type='json', auth='user', methods=['POST'])
    def create_vue_record(self, model=None, values=None, **kwargs):
        """API для создания записей из Vue приложения"""
        try:
            if not model or not values:
                return {
                    'success': False,
                    'error': 'Не указана модель или значения'
                }
            
            # Проверяем права
            if not request.env[model].check_access_rights('create', raise_exception=False):
                return {
                    'success': False,
                    'error': 'Недостаточно прав для создания записи'
                }
            
            # Создаем запись
            record = request.env[model].create(values)
            
            return {
                'success': True,
                'id': record.id,
                'message': 'Запись успешно создана'
            }
            
        except Exception as e:
            _logger.error(f"Ошибка в create_vue_record: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/vue/api/update', type='json', auth='user', methods=['POST'])
    def update_vue_record(self, model=None, record_id=None, values=None, **kwargs):
        """API для обновления записей из Vue приложения"""
        try:
            if not model or not record_id or not values:
                return {
                    'success': False,
                    'error': 'Не указаны все необходимые параметры'
                }
            
            # Получаем запись
            record = request.env[model].browse(record_id)
            if not record.exists():
                return {
                    'success': False,
                    'error': 'Запись не найдена'
                }
            
            # Проверяем права
            if not record.check_access_rights('write', raise_exception=False):
                return {
                    'success': False,
                    'error': 'Недостаточно прав для изменения записи'
                }
            
            # Обновляем запись
            record.write(values)
            
            return {
                'success': True,
                'message': 'Запись успешно обновлена'
            }
            
        except Exception as e:
            _logger.error(f"Ошибка в update_vue_record: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/vue/api/delete', type='json', auth='user', methods=['POST'])
    def delete_vue_record(self, model=None, record_id=None, **kwargs):
        """API для удаления записей из Vue приложения"""
        try:
            if not model or not record_id:
                return {
                    'success': False,
                    'error': 'Не указаны модель или ID записи'
                }
            
            # Получаем запись
            record = request.env[model].browse(record_id)
            if not record.exists():
                return {
                    'success': False,
                    'error': 'Запись не найдена'
                }
            
            # Проверяем права
            if not record.check_access_rights('unlink', raise_exception=False):
                return {
                    'success': False,
                    'error': 'Недостаточно прав для удаления записи'
                }
            
            # Удаляем запись
            record.unlink()
            
            return {
                'success': True,
                'message': 'Запись успешно удалена'
            }
            
        except Exception as e:
            _logger.error(f"Ошибка в delete_vue_record: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/vue/api/user-info', type='json', auth='user', methods=['POST'])
    def get_user_info(self, **kwargs):
        """Получение информации о текущем пользователе"""
        try:
            user = request.env.user
            company = user.company_id
            
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'login': user.login,
                    'email': user.email,
                    'lang': user.lang,
                    'tz': user.tz,
                    'company': {
                        'id': company.id,
                        'name': company.name,
                        'currency': company.currency_id.name if company.currency_id else None
                    }
                }
            }
            
        except Exception as e:
            _logger.error(f"Ошибка в get_user_info: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========== НОВЫЕ API ДЛЯ ЦЕЛЕВЫХ ПОКАЗАТЕЛЕЙ ==========
    
    @http.route('/vue/api/targets/load', type='json', auth='user', methods=['POST'])
    def load_targets(self, **kwargs):
        """Загрузка целевых показателей из файла targets.json"""
        try:
            # Получаем путь к файлу targets.json
            addon_path = request.env['ir.module.module']._get_module_resource_path('com')
            targets_path = os.path.join(addon_path, 'static', 'data', 'targets.json')
            
            # Проверяем существование файла
            if not os.path.exists(targets_path):
                # Если файла нет, возвращаем дефолтные данные
                default_targets = {
                    "targetTree": {
                        "turnover": {"name": "Оборот", "maxScore": 100, "type": "positive"},
                        "losses": {"name": "Списання ТМЦ", "maxScore": 20, "type": "negative"},
                        "shortages": {"name": "Нестачі", "maxScore": 100, "type": "negative"},
                        "fop": {"name": "ФОП", "maxScore": 15, "type": "negative"},
                        "unprocessed": {"name": "Непровед. списання", "maxScore": 10, "type": "negative"}
                    },
                    "storeTargets": {
                        "1": {"losses": 0.0007, "shortages": 0.00018, "fop": 0.012, "unprocessed": 0.0000008},
                        "2": {"losses": 0.0007, "shortages": 0.00020, "fop": 0.015, "unprocessed": 0.0000009},
                        "3": {"losses": 0.0007, "shortages": 0.00022, "fop": 0.013, "unprocessed": 0.0000010},
                        "4": {"losses": 0.0007, "shortages": 0.00019, "fop": 0.014, "unprocessed": 0.0000009},
                        "5": {"losses": 0.0007, "shortages": 0.00024, "fop": 0.016, "unprocessed": 0.0000011},
                        "6": {"losses": 0.0007, "shortages": 0.00017, "fop": 0.011, "unprocessed": 0.0000007},
                        "7": {"losses": 0.0007, "shortages": 0.00016, "fop": 0.010, "unprocessed": 0.0000007},
                        "8": {"losses": 0.0007, "shortages": 0.00021, "fop": 0.014, "unprocessed": 0.0000009},
                        "9": {"losses": 0.0007, "shortages": 0.00017, "fop": 0.011, "unprocessed": 0.0000008},
                        "10": {"losses": 0.0007, "shortages": 0.00023, "fop": 0.015, "unprocessed": 0.0000010},
                        "11": {"losses": 0.0007, "shortages": 0.00018, "fop": 0.012, "unprocessed": 0.0000008},
                        "12": {"losses": 0.0007, "shortages": 0.00020, "fop": 0.013, "unprocessed": 0.0000009},
                        "13": {"losses": 0.0007, "shortages": 0.00019, "fop": 0.014, "unprocessed": 0.0000009},
                        "14": {"losses": 0.0007, "shortages": 0.00021, "fop": 0.013, "unprocessed": 0.0000008},
                        "15": {"losses": 0.0007, "shortages": 0.00020, "fop": 0.012, "unprocessed": 0.0000009},
                        "16": {"losses": 0.0007, "shortages": 0.00024, "fop": 0.016, "unprocessed": 0.0000011}
                    }
                }
                
                return {
                    'success': True,
                    'data': default_targets,
                    'source': 'default'
                }
            
            # Читаем файл
            with open(targets_path, 'r', encoding='utf-8') as f:
                targets = json.load(f)
            
            return {
                'success': True,
                'data': targets,
                'source': 'file',
                'path': targets_path
            }
            
        except Exception as e:
            _logger.error(f"Ошибка загрузки targets.json: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/vue/api/targets/save', type='json', auth='user', methods=['POST'])
    def save_targets(self, targets=None, **kwargs):
        """Сохранение целевых показателей"""
        try:
            if not targets:
                return {
                    'success': False,
                    'error': 'Не переданы данные для сохранения'
                }
            
            # Валидация данных
            if not isinstance(targets, dict):
                return {
                    'success': False,
                    'error': 'Данные должны быть в формате объекта'
                }
            
            if 'targetTree' not in targets or 'storeTargets' not in targets:
                return {
                    'success': False,
                    'error': 'Отсутствуют обязательные поля targetTree или storeTargets'
                }
            
            # Проверяем модель com.targets
            targets_model = None
            try:
                targets_model = request.env['com.targets']
            except KeyError:
                # Модель не существует, сохраняем в файл
                pass
            
            # Если модель существует, сохраняем в базу данных
            if targets_model:
                # Деактивируем предыдущие записи
                old_targets = targets_model.search([('active', '=', True)])
                if old_targets:
                    old_targets.write({'active': False})
                
                # Создаем новую запись
                new_target = targets_model.create({
                    'name': f"Автосохранение - {request.env.user.name}",
                    'target_tree': json.dumps(targets.get('targetTree', {})),
                    'store_targets': json.dumps(targets.get('storeTargets', {})),
                    'active': True
                })
                
                return {
                    'success': True,
                    'message': 'Целевые показатели сохранены в базу данных',
                    'id': new_target.id,
                    'storage': 'database'
                }
            else:
                # Сохраняем в файл (резервный вариант)
                addon_path = request.env['ir.module.module']._get_module_resource_path('com')
                targets_path = os.path.join(addon_path, 'static', 'data', 'targets.json')
                
                # Создаем директорию если не существует
                os.makedirs(os.path.dirname(targets_path), exist_ok=True)
                
                # Сохраняем в файл
                with open(targets_path, 'w', encoding='utf-8') as f:
                    json.dump(targets, f, ensure_ascii=False, indent=2)
                
                return {
                    'success': True,
                    'message': 'Целевые показатели сохранены в файл',
                    'path': targets_path,
                    'storage': 'file'
                }
                
        except Exception as e:
            _logger.error(f"Ошибка сохранения целевых показателей: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/vue/api/targets/history', type='json', auth='user', methods=['POST'])
    def get_targets_history(self, limit=10, **kwargs):
        """Получение истории изменений целевых показателей"""
        try:
            targets_model = None
            try:
                targets_model = request.env['com.targets']
            except KeyError:
                return {
                    'success': False,
                    'error': 'Модель com.targets не найдена'
                }
            
            # Получаем историю записей
            targets_history = targets_model.search(
                [], 
                order='created_date desc', 
                limit=limit
            )
            
            history_data = []
            for target in targets_history:
                history_data.append({
                    'id': target.id,
                    'name': target.name,
                    'created_date': target.created_date.isoformat() if target.created_date else None,
                    'created_by': target.created_by.name if target.created_by else None,
                    'active': target.active,
                    'target_tree': json.loads(target.target_tree) if target.target_tree else {},
                    'store_targets': json.loads(target.store_targets) if target.store_targets else {}
                })
            
            return {
                'success': True,
                'data': history_data,
                'count': len(history_data)
            }
            
        except Exception as e:
            _logger.error(f"Ошибка получения истории целевых показателей: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/vue/api/targets/restore', type='json', auth='user', methods=['POST'])
    def restore_targets(self, target_id=None, **kwargs):
        """Восстановление целевых показателей из истории"""
        try:
            if not target_id:
                return {
                    'success': False,
                    'error': 'Не указан ID записи для восстановления'
                }
            
            targets_model = request.env['com.targets']
            target_record = targets_model.browse(target_id)
            
            if not target_record.exists():
                return {
                    'success': False,
                    'error': 'Запись не найдена'
                }
            
            # Деактивируем текущие активные записи
            active_targets = targets_model.search([('active', '=', True)])
            if active_targets:
                active_targets.write({'active': False})
            
            # Активируем выбранную запись
            target_record.write({'active': True})
            
            # Возвращаем восстановленные данные
            restored_data = {
                'targetTree': json.loads(target_record.target_tree) if target_record.target_tree else {},
                'storeTargets': json.loads(target_record.store_targets) if target_record.store_targets else {}
            }
            
            return {
                'success': True,
                'message': f'Целевые показатели восстановлены из записи: {target_record.name}',
                'data': restored_data
            }
            
        except Exception as e:
            _logger.error(f"Ошибка восстановления целевых показателей: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/vue/api/analytics/real-data', type='json', auth='user', methods=['POST'])
    def get_real_analytics_data(self, **kwargs):
        """Получение данных аналитики из real-data.json"""
        try:
            # Получаем путь к файлу real-data.json
            addon_path = request.env['ir.module.module']._get_module_resource_path('com')
            data_path = os.path.join(addon_path, 'static', 'data', 'real-data.json')
            
            # Проверяем существование файла
            if not os.path.exists(data_path):
                return {
                    'success': False,
                    'error': 'Файл real-data.json не найден'
                }
            
            # Читаем файл
            with open(data_path, 'r', encoding='utf-8') as f:
                analytics_data = json.load(f)
            
            return {
                'success': True,
                'data': analytics_data,
                'source': 'file',
                'path': data_path
            }
            
        except Exception as e:
            _logger.error(f"Ошибка загрузки real-data.json: {e}")
            return {
                'success': False,
                'error': str(e)
            }
