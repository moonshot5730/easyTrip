from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.lifecycle.bootstrap import boostrap
from app.core.lifecycle.env_setting import load_env
from app.core.lifecycle.validate_key_setting import (validate_env_keys,
                                                     validate_llm_keys)

app = boostrap()
