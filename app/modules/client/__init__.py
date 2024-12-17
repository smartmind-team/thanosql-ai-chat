import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[3]))
from app.modules.client.openai_client import *
from app.modules.client.thanosql_client import *
