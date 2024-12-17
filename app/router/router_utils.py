import sys
from pathlib import Path
from typing import Any, Callable, Optional, Union

from fastapi import HTTPException

sys.path.append(Path(__file__).parents[2])
from utils.logger import logger

async def exception_handler(
    func: Union[Callable, dict],
    func_params: Optional[Any] = None,
    e_code: Optional[int] = None,
    e_msg: Optional[object] = None,
    additonal_error_handle: Optional[Callable] = None,
):
    try:
        if callable(func) and func_params:
            if hasattr(func, "__await__"): # if func is async
                result = await func(func_params)
            else:
                result = func(func_params)
        elif callable(func):
            if hasattr(func, "__await__"): # if func is async
                result = await func()
            else:
                result = func()
        else:  # type(func) is dict
            result = func
        return result
    except Exception as e:
        if additonal_error_handle:
            additonal_error_handle(e)
        e_msg = e_msg if e_msg else str(e)
        logger.error(e_msg)
        raise HTTPException(status_code=e_code if e_code else 500, detail=e_msg)