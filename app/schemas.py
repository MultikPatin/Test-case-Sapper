from pydantic import UUID4, BaseModel, Field, field_validator, root_validator


class NewGameRequest(BaseModel):
    width: int = Field(ge=2, le=30, description="Ширина игрового поля")
    height: int = Field(ge=2, le=30, description="Высота игрового поля")
    mines_count: int = Field(le=899, description="Количество мин на поле")

    @root_validator(skip_on_failure=True)
    def check_amount(cls, values):
        if values["mines_count"] >= values["width"] * values["height"]:
            raise ValueError(
                "Значение поля mines_count "
                "не могут быть больше или равно количеству клеток поля"
            )
        return values


class IdMixin(BaseModel):
    game_id: UUID4 = Field(description="Идентификатор игры")

    @field_validator("game_id")
    def game_id_cannot_be_null(cls, value):
        if value == "":
            raise ValueError("game_id не может быть пустым!")
        return value


class GameTurnRequest(IdMixin):
    col: int = Field(
        ge=0, le=29, description="Колонка проверяемой ячейки (нумерация с нуля)"
    )
    row: int = Field(
        ge=0, le=29, description="Ряд проверяемой ячейки (нумерация с нуля)"
    )


class GameInfoResponse(IdMixin, NewGameRequest):
    completed: bool = Field(description="Завершена ли игра")
    field: list[list[str]] = Field(
        description="Строки минного поля (количество равно высоте height)"
    )
