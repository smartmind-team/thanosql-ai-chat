import sys
from pathlib import Path

sys.path.append(Path(__file__).parents[2])
from app.resource.prompt.system_prompts import *
from app.resource.prompt.answer_prompts import *
from app.resource.prompt.question_prompts import *
from app.resource.prompt.search_prompts import *