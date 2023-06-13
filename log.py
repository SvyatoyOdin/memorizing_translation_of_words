import json
from json.decoder import JSONDecodeError
from datetime import datetime


def append_bot_operation_data(type_data: str, data: str = None, exception_number: int = None) -> None:
    """append bot operation data to file json"""
    datetime_now = datetime.now()
    time_now: str = f"{datetime_now.hour}" \
                    f":{datetime_now.minute}:{datetime_now.second}"

    with open("log.txt", "a+") as file:
        if exception_number and data:
            file.write(
                f"{type_data}; TIME - {time_now}; DATA - {data}; EXCEPTION NUMBER - {exception_number}\n")
        elif data:
            file.write(
                f"{type_data}; TIME - {time_now}; DATA - {data}\n")
        else:
            file.write(f"{type_data}; TIME - {time_now}\n")


def sorted_exception_data(ex: BaseException) -> dict:
    """sorting exception data to dict and returned them"""
    trace = []
    tb = ex.__traceback__
    while tb is not None:
        trace.append({
            "filename": tb.tb_frame.f_code.co_filename,
            "name": tb.tb_frame.f_code.co_name,
            "lineno": tb.tb_lineno
        })
        tb = tb.tb_next

    return {
        'type': type(ex).__name__,
        'message': str(ex),
        'all_exception': trace
    }


def append_exception_data(ex: BaseException) -> int:
    """append exception data to file json and return exception number """
    new_exception_data = sorted_exception_data(ex)

    try:
        with open("exception_data.json", "r") as file:
            exception_data: dict = json.load(file)
    except (FileNotFoundError, JSONDecodeError):
        exception_data: bool = False

    with open("exception_data.json", "w") as file:
        number = 1
        if exception_data:
            number = int(list(exception_data)[0])  # -> last exception number
            number += 1
            exception_data[number] = new_exception_data
        else:
            exception_data = {number: new_exception_data}

        json.dump(exception_data, file, ensure_ascii=False, indent=4)

    return number
