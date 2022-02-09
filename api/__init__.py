from fastapi import FastAPI
from .settings import Config_settings
from logging.config import dictConfig
import logging
from .config_logs import LogConfig

# initial settings
settings = settings.Config_settings()

# initial app
app = FastAPI()



# initial logger
dictConfig(LogConfig().dict())
logger = logging.getLogger("pushka")

from api.routes import api_routes, click_stat_routes
from api.utils.mergin_rec_files import merging_files
from .db import engine, tarantool_db, SessionLocal
from . import models
from .tarantool_loader import check_creating_spaces
from starlette.requests import Request
from starlette.responses import Response

models.Base.metadata.create_all(bind=engine)

# Add router in app
app.include_router(api_routes.router, prefix='/api/v1', tags=["api"])
app.include_router(click_stat_routes.router, prefix='/click_stat', tags=["click_stat"])


# Список файлов с региональными рекомендациями

regional_rec_files = [
    # 'bashkortostan_rec.json',
    'dagestan_rec.json',
    'kemerov_rec.json',
    'novosib_rec.json',
    'perm_rec.json',
    'rec_test.json',
    'rostov_rec.json',
    'samara_rec.json',
    'sverdlov_rec.json',
    'tatarstan_rec.json',
    'volgograd_rec.json',
]

# Список спейсов Тарантула для каждого типа рекомендаций, а также исходных файлов.

spaces = [
    ['regional_rec', 'events.csv', 'regional_rec.json'],
    ['3day_recs_from_filtered_events', 'events.csv', '3day_recs_from_filtered_events_final.json'],
    # ['3day_recs_from_filtered_top', 'events.csv', '3day_recs_from_filtered_top_final.json'],
    # ['user_rec_without_filter', 'events.csv', 'User_rec_without_filter_final.json'],
]
# Объединяем json файлы региональных рекомендаций

merging_files(regional_rec_files)

# Проверка инициализации спейса для каждой рекомендации. Если его нет, то создаем в Тарантуле

check_creating_spaces(spaces)


@app.middleware('http')
async def db_session_middleware(request: Request, call_next):
    response = Response('Internet server error', status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response