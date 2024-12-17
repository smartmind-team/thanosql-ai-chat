import sys
from pathlib import Path

from thanosql import ThanoSQL

(str(Path(__file__).parents[3]))
from utils import settings

thanosql_client = ThanoSQL(
    api_token=settings.thanosql.api_token,
    engine_url=settings.thanosql.engine_url
)