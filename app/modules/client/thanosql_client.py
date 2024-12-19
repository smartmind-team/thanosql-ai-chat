from thanosql import ThanoSQL
from utils import settings

thanosql_client = ThanoSQL(
    api_token=settings.thanosql.api_token, engine_url=settings.thanosql.engine_url
)
