import pandas as pd
from docx.api import Document


def get_schedule(file_name):
    document = Document(file_name)
    table = document.tables[0]
    #print(table)

    data = []

    keys = None
    for i, row in enumerate(table.rows):
        text = (cell.text for cell in row.cells)

        if i == 0:
            keys = tuple(text)
            continue
        row_data = dict(zip(keys, text))
        data.append(row_data)

    #print(data)
    return data