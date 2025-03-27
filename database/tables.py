from typing import Optional
from .__tables_utils import format_values
from .connect import cursor, conn
from .constants import QUERIES


queries = QUERIES["tables"]


def create(name: str, columns: list, condition: str = ""):
    f_cols = ",\n".join(columns)
    query = "create"
    kwargs = {"name": name, "columns": f_cols, "condition": condition + " "}

    query_wrapper(query, **kwargs)


def delete(name: str):
    query = "delete"
    kwargs = {"name": name}
    query_wrapper(query, **kwargs)


def delete_value(table: str, column: str, value: str, comparison_operator: str = "="):
    query = "delete_value"
    kwargs = {"column": column, "comp_op": comparison_operator, "value": value}
    query_wrapper(query, table, **kwargs)


def insert(table: str, columns: dict[str]):
    cols = ", ".join(columns.keys())
    vals = format_values(columns)

    query = "insert"
    kwargs = {"columns": cols, "values": vals}
    query_wrapper(query, table, **kwargs)


def update(
    table: str,
    columns: dict,
    wh_columns: dict[str] = None,
    comparison_operator: str = "=",
):
    column = "".join(columns.keys())
    value = format_values(columns)

    query = "update"
    kwargs = {"column": column, "value": value}

    if wh_columns is None:
        query_wrapper(query, table, **kwargs)
        return

    kwargs.setdefault("comp_op", comparison_operator)
    wh_qwrapper(query, wh_columns, table, **kwargs)


def select(
    table: str,
    columns: list[str],
    wh_columns: dict[str] = None,
    comparison_operator: str = "=",
):
    query = "select"
    kwargs = {"columns": ", ".join(columns)}

    if wh_columns is None:
        return query_wrapper(query, table, **kwargs)

    kwargs.setdefault("comp_op", comparison_operator)
    return wh_qwrapper(query, wh_columns, table, **kwargs)


def select_all(
    table: str,
    wh_columns: dict[str] = None,
    comparison_operator: str = "=",
):
    kwargs = {"columns": "*"}

    if wh_columns is None:
        return query_wrapper("selec table,t", **kwargs)

    kwargs.setdefault("comp_op", comparison_operator)
    return wh_qwrapper("select", wh_columns, table, **kwargs)


def query_wrapper(query: str, table: Optional[str] = None, **kwargs):
    template = queries[query]
    operation = template.format(table=table, **kwargs)
    cursor.execute(operation)
    conn.commit()

    try:
        return cursor.fetchall()
    except TypeError:
        return


def wh_qwrapper(query: str, wh_columns: dict, table: str, **kwargs):
    query += "_wh"
    wh_name = "".join(wh_columns.keys())
    wh_value = format_values(wh_columns)

    return query_wrapper(query, table, wh_columns=wh_name, wh_value=wh_value, **kwargs)
