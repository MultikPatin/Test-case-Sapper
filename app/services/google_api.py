from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings

FORMAT = "%Y/%m/%d %H:%M:%S"

SHEETS_ROWS_COUNT = 100

SHEETS_COLUMN_COUNT = 11

TABLE_NAME = "Отчет от {}"

SPREADSHEET_BODY = {
    "properties": {"locale": "ru_RU"},
    "sheets": [
        {
            "properties": {
                "sheetType": "GRID",
                "sheetId": 0,
                "title": "Лист1",
                "gridProperties": {
                    "rowCount": SHEETS_ROWS_COUNT,
                    "columnCount": SHEETS_COLUMN_COUNT,
                },
            }
        }
    ],
}

HEADER = [
    ["Отчет от", ""],
    ["Топ проектов по скорости закрытия"],
    ["Название проекта", "Время сбора", "Описание"],
]


async def spreadsheets_create(
    wrapper_services: Aiogoogle, spreadsheet_body: dict | None
) -> str:
    """
    Создание Google таблицы
    :param wrapper_services: Main entry point for Aiogoogle.
    :param spreadsheet_body: Данные для настройки создаваемой таблицы
    :return: Идентификатор созданной таблицы
    """
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover("sheets", "v4")

    if not spreadsheet_body:
        spreadsheet_body = SPREADSHEET_BODY.copy()
    spreadsheet_body["properties"]["title"] = TABLE_NAME.format(
        str(now_date_time)
    )
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response["spreadsheetId"]
    return spreadsheet_id


async def set_user_permissions(
    spreadsheet_id: str, wrapper_services: Aiogoogle
) -> None:
    """
    Выдача прав на доступ к Google таблице
    :param spreadsheet_id: Идентификатор таблицы
    :param wrapper_services: Main entry point for Aiogoogle.
    """
    permissions_body = {
        "type": "user",
        "role": "writer",
        "emailAddress": settings.email,
    }
    service = await wrapper_services.discover("drive", "v3")
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id, json=permissions_body, fields="id"
        )
    )


async def spreadsheets_update_value(
    spreadsheet_id: str, projects: list, wrapper_services: Aiogoogle
) -> None:
    """
    Обновление данных в Google таблице
    :param spreadsheet_id: Идентификатор таблицы
    :param projects: Данные для обновления в Google таблице
    :param wrapper_services: Main entry point for Aiogoogle.
    """
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover("sheets", "v4")
    table_head = HEADER.copy()
    table_head[0].append(now_date_time)

    table_values = [
        *table_head,
        *[list(map(str, project.values())) for project in projects],
    ]

    update_body = {"majorDimension": "ROWS", "values": table_values}
    table_rows = len(table_values)

    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f"A1:C{table_rows}",
            valueInputOption="USER_ENTERED",
            json=update_body,
        )
    )
