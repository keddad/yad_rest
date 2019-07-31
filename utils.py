from datetime import datetime

collection_filter = {"name": {"$regex": r"^(?!system\.)"}}


def month(wtf: str) -> str:
    wtf = wtf.split(".")[1]
    if wtf == "10":
        return wtf
    else:
        return wtf.strip("0")


def birthdays_counter(dataset: list) -> dict:
    citizen_data, out = dict(), dict()
    for element in dataset:
        for relative in element["relatives"]:
            relative_month = month(element["birth_date"])
            if not citizen_data[relative_month]:
                citizen_data[relative_month] = dict()
            if not citizen_data[relative_month][relative]:
                citizen_data[relative_month][relative] = 1
            else:
                citizen_data[relative_month][relative] += 1

    for (key, value) in citizen_data.items():
        if not out[key]:
            out[key] = list()
        for (nested_key, nested_value) in value.items():
            out[key].insert(
                {
                    "citizen_id": nested_key,
                    "presents": value
                }
            )
    for i in range(1, 13):
        if not out[str(i)]:
            out[str(i)] = list()

    return out


def broken_relatives(citizens: list) -> bool:
    try:
        checked = list()
        for citizen in citizens:
            for rel in citizen["relatives"]:
                if rel in checked:
                    continue
                # noinspection PyTypeChecker
                if not citizen["citizen_id"] in citizens[rel]["relatives"]:
                    return True
            checked.insert(citizen["citizen_id"])
    except (KeyError, IndentationError):
        return True
    return False


def next_collection(db) -> int:
    current_collections = db.list_collection_names(filter=collection_filter)
    return len(current_collections) + 1


def datetime_correct(dat: str) -> bool:
    try:
        null = datetime(*[int(x) for x in dat.split(".")[::-1]])
        null = str.split(".")
        if len(null) != 3:
            return False
        if len(null[0]) != 2 or len(null[1) != 2 or len(null[2]) != 4:
            return False
        return True
    except ValueError:
        return False
