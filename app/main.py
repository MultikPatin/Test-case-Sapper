import os

from dotenv import load_dotenv
from fastapi import FastAPI

from app.schemas import GameInfoResponse, GameTurnRequest, NewGameRequest
from app.services import Sapper

load_dotenv()

app = FastAPI(
    title=os.environ.get("APP_TITLE", default="APP_TITLE"),
    description=os.environ.get("APP_DESCRIPTION", default="APP_DESCRIPTION"),
)

game = Sapper()


@app.post(
    "/new",
    response_model=GameInfoResponse,
)
async def create_new_game(obj_in: NewGameRequest):
    return game.create_new_game(obj_in)


@app.post(
    "/turn",
    response_model=GameInfoResponse,
)
async def create_new_turn(obj_in: GameTurnRequest):
    return game.create_new_turn(obj_in)
