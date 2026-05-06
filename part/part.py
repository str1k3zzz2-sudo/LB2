from flask_restx import Namespace, Resource, fields, reqparse

api = Namespace('sports', description='Операции со спортивными состязаниями')

# ============================================================
# МОДЕЛЬ ДАННЫХ ДЛЯ SWAGGER
# ============================================================
competition_model = api.model('Competition', {
    'id': fields.String(required=True, example='1', description='Уникальный ID'),
    'name': fields.String(required=True, example='Олимпийские игры 2024', description='Название соревнования'),
    'sport': fields.String(required=True, example='Плавание', description='Вид спорта'),
    'athlete': fields.String(required=True, example='Майкл Фелпс', description='ФИО спортсмена'),
    'country': fields.String(required=True, example='США', description='Страна'),
    'result': fields.Float(required=True, example=47.51, description='Результат (сек/очки/метры)'),
    'place': fields.Integer(required=True, example=1, description='Занятое место'),
    'year': fields.Integer(required=True, example=2024, description='Год проведения')
})

# ============================================================
# ХРАНИЛИЩЕ ДАННЫХ (В ПАМЯТИ)
# ============================================================
COMPETITIONS = [
    {'id': '1', 'name': 'Олимпийские игры 2024', 'sport': 'Плавание',
     'athlete': 'Майкл Фелпс', 'country': 'США', 'result': 47.51, 'place': 1, 'year': 2024},
    {'id': '2', 'name': 'Чемпионат мира', 'sport': 'Легкая атлетика',
     'athlete': 'Усэйн Болт', 'country': 'Ямайка', 'result': 9.58, 'place': 1, 'year': 2023},
    {'id': '3', 'name': 'Кубок мира', 'sport': 'Футбол',
     'athlete': 'Лионель Месси', 'country': 'Аргентина', 'result': 7.5, 'place': 2, 'year': 2022}
]

# ============================================================
# ПАРСЕРЫ ДЛЯ ПАРАМЕТРОВ ЗАПРОСОВ
# ============================================================

# Парсер для сортировки
sort_parser = reqparse.RequestParser()
sort_parser.add_argument('sort_by', type=str, required=False,
                         choices=['name', 'sport', 'athlete', 'country', 'result', 'place', 'year'],
                         help='Поле для сортировки')
sort_parser.add_argument('order', type=str, default='asc', choices=['asc', 'desc'],
                         help='Порядок сортировки (asc/desc)')

# Парсер для добавления и обновления
competition_parser = reqparse.RequestParser()
competition_parser.add_argument('name', type=str, required=True, help='Название соревнования')
competition_parser.add_argument('sport', type=str, required=True, help='Вид спорта')
competition_parser.add_argument('athlete', type=str, required=True, help='ФИО спортсмена')
competition_parser.add_argument('country', type=str, required=True, help='Страна')
competition_parser.add_argument('result', type=float, required=True, help='Результат')
competition_parser.add_argument('place', type=int, required=True, help='Место')
competition_parser.add_argument('year', type=int, required=True, help='Год проведения')

# ============================================================
# ЭНДПОИНТ 1: /sports/competitions (GET все, POST добавить)
# ============================================================
@api.route('/competitions')
class CompetitionList(Resource):
    @api.doc('get_all_competitions')
    @api.expect(sort_parser)
    @api.marshal_list_with(competition_model)
    def get(self):
        """
        Получить список всех соревнований.
        Можно сортировать по любому полю:
        - GET /sports/competitions?sort_by=year&order=desc
        - GET /sports/competitions?sort_by=result&order=asc
        """
        args = sort_parser.parse_args()
        sort_by = args.get('sort_by')
        order = args.get('order')

        if sort_by and sort_by in COMPETITIONS[0]:
            reverse = (order == 'desc')
            return sorted(COMPETITIONS, key=lambda x: x[sort_by], reverse=reverse)
        return COMPETITIONS

    @api.doc('create_competition')
    @api.expect(competition_parser)
    @api.marshal_with(competition_model, code=201)
    def post(self):
        """
        Добавить новое соревнование.
        ID генерируется автоматически.
        """
        args = competition_parser.parse_args()
        new_id = str(max(int(c['id']) for c in COMPETITIONS) + 1)
        new_competition = {'id': new_id}
        for field in ['name', 'sport', 'athlete', 'country', 'result', 'place', 'year']:
            new_competition[field] = args[field]
        COMPETITIONS.append(new_competition)
        return new_competition, 201

# ============================================================
# ЭНДПОИНТ 2: /sports/competitions/{id} (GET, PUT, DELETE)
# ============================================================
@api.route('/competitions/<string:id>')
@api.param('id', 'Идентификатор соревнования (1, 2, 3...)')
@api.response(404, 'Соревнование с указанным ID не найдено')
class CompetitionResource(Resource):
    @api.doc('get_competition')
    @api.marshal_with(competition_model)
    def get(self, id):
        """Получить соревнование по ID"""
        for comp in COMPETITIONS:
            if comp['id'] == id:
                return comp
        api.abort(404, f'Соревнование с id {id} не найдено')

    @api.doc('update_competition')
    @api.expect(competition_parser)
    @api.marshal_with(competition_model)
    def put(self, id):
        """Полностью обновить данные соревнования по ID"""
        for i, comp in enumerate(COMPETITIONS):
            if comp['id'] == id:
                args = competition_parser.parse_args()
                COMPETITIONS[i] = {'id': id}
                for field in ['name', 'sport', 'athlete', 'country', 'result', 'place', 'year']:
                    COMPETITIONS[i][field] = args[field]
                return COMPETITIONS[i]
        api.abort(404, f'Соревнование с id {id} не найдено')

    @api.doc('delete_competition')
    @api.response(204, 'Запись успешно удалена')
    def delete(self, id):
        """Удалить соревнование по ID"""
        for i, comp in enumerate(COMPETITIONS):
            if comp['id'] == id:
                COMPETITIONS.pop(i)
                return '', 204
        api.abort(404, f'Соревнование с id {id} не найдено')

# ============================================================
# ЭНДПОИНТ 3: /sports/competitions/statistics/{field} (статистика)
# ============================================================
@api.route('/competitions/statistics/<string:field>')
@api.param('field', 'Поле для статистики: result, place, year')
class CompetitionStatistics(Resource):
    @api.doc('get_statistics')
    def get(self, field):
        """
        Получить минимальное, максимальное и среднее значение по указанному полю.
        Доступные поля: result, place, year
        """
        if field not in ['result', 'place', 'year']:
            api.abort(400, f'Поле {field} недоступно. Используйте: result, place, year')

        values = [comp[field] for comp in COMPETITIONS]
        return {
            'field': field,
            'min': min(values),
            'max': max(values),
            'avg': round(sum(values) / len(values), 2)
        }
