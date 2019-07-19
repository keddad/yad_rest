"""
Not my best code
But is still (probably) works!
"""


def month(wtf: str) -> str:
    wtf = wtf.split(".")[1]
    if wtf == "10":
        return wtf
    else:
        return wtf.strip("0")


def birthdays_counter(dataset: list) -> dict:
    needed_keys = [False for _ in range(13)]
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
    for key in out.keys():
        needed_keys[key] = True

    for i in range(1, 13):
        if not out[needed_keys[i]]:
            out[needed_keys] = list()

    return out
