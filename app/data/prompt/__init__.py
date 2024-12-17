import sys
from pathlib import Path

sys.path.append(Path(__file__).parents[2])
from app.data.prompt.system_prompts import *
from app.data.prompt.answer_prompts import *
from app.data.prompt.question_prompts import *
from app.data.prompt.search_prompts import *