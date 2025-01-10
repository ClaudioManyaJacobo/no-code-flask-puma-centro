import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'abc-proyect-2025')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'mssql+pyodbc://sa:GrupoHexagonal#0112@172.22.15.132/Electro_Puma?driver=ODBC+Driver+17+for+SQL+Server')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
