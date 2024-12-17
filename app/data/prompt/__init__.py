import sys
from pathlib import Path

sys.path.append(Path(__file__).parents[2])
from data.prompt.system_prompts import *
from data.prompt.answer_prompts import *
from data.prompt.question_prompts import *
from data.prompt.search_prompts import *