from flask import Flask
from flask_restx import Api

app = Flask(__name__)

api = Api(
    app=app,
    title='Спортивные состязания API',
    version='1.0',
    description='API для управления данными о спортивных соревнованиях',
    doc='/swagger/'
)

from part.part import api as sports_api
api.add_namespace(sports_api)

if __name__ == '__main__':
    print("=" * 50)
    print("🏅 Сервер спортивных состязаний запущен!")
    print("📖 Swagger: http://127.0.0.1:5000/swagger/")
    print("=" * 50)
    app.run(debug=True)
