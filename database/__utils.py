from . import tables


def add_data(table: str, data: dict):
    tables.insert(table, data)


def get_data(
    table: str, columns: list, wh_data: dict | None = None, comparison_operator: str = "="
) -> list:
    d = tables.select(table, columns, wh_data, comparison_operator)
    if d and d[0]:
        return d[0] if len(d) == 1 else d


def get_all_data(table: str, wh_data: dict | None = None, comparison_operator: str = "="):
    return get_data(table, ["*"], wh_data, comparison_operator)
    # d = tables.select_all(data)
    # if d and d[0]:
    #     return d[0]


def is_data_in(table: str, data: dict, comparison_operator: str = "="):
    return True if get_all_data(table, data, comparison_operator) else False


def update_data(table: str, new_data: dict, wh_data: dict, comparison_operator: str = "="):
    tables.update(table, new_data, wh_data, comparison_operator)


def remove_data(table: str, data: str, wh_data: dict, comparison_operator: str = "="):
    update_data(table, {data: None}, wh_data, comparison_operator)


def remove_from_table(table: str, wh_data: dict, comparison_operator: str = "="):
    tables.delete_value(table, *wh_data.keys(), *wh_data.values(), comparison_operator=comparison_operator)
