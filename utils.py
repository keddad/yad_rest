from datetime import date
from json import dumps

collection_filter = {"name": {"$regex": r"^(?!system\.)"}}


def month(wtf: str) -> str:
    wtf = wtf.split(".")[1]
    if wtf == "10":
        return wtf
    else:
        return wtf.strip("0")


def birthdays_counter(dataset: list) -> dict:
    out, tmp = dict(), dict()

    for citizen in dataset:
        citizen_month = month(citizen["birth_date"])
        if citizen_month not in tmp:
            tmp[citizen_month] = dict()
            out[citizen_month] = list()
        for rel in citizen["relatives"]:
            if rel not in tmp[citizen_month]:
                tmp[citizen_month][rel] = 1
            else:
                tmp[citizen_month][rel] = +1

    for (m, value) in tmp.items():
        for (key, presents) in value.items():
            out[m].append(
                (
                    {
                        "citizen_id": key,
                        "presents": presents
                    }
                )
            )

    for i in range(1, 13):
        if str(i) not in out:
            out[str(i)] = list()

    return out


def broken_relatives(citizens: list) -> bool:
    try:
        for citizen in citizens:
            for relative in citizen["relatives"]:  # проверка на соответствие родственников
                if not citizen["citizen_id"] in \
                       list(
                           filter(
                               lambda person: person['citizen_id'] == relative, citizens))[0]["relatives"]:
                    return True
    except (KeyError, IndentationError, IndexError):
        return True
    return False


def next_collection(db) -> int:
    current_collections = [int(name) for name in db.list_collection_names(filter=collection_filter)]
    if len(current_collections):
        return max(current_collections) + 1
    else:
        return 1


def datetime_correct(dat: str) -> bool:
    ds = dat.split(".")
    if len(ds[0]) != 2 or len(ds[1]) != 2 or len(ds[2]) != 4:
        return False
    try:
        null = date.fromisoformat(f"{dat[6:10]}-{dat[3:5]}-{dat[0:2]}")
        return True
    except ValueError:
        return False


def jsonify(element) -> str:
    return dumps(element, ensure_ascii=False).encode("utf-8")
