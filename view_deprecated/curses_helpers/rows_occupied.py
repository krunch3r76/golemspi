def rows_occupied(countCol, line, newline=True):
    # determine how many rows a text (or length of text) would occupy
    if isinstance(line, str):
        line_length = len(line) + 1 if newline else 0
    elif isinstance(line, int):
        raise Exception("not supported")
        line_length = line
    else:
        raise TypeError
    whole_measures = line_length // countCol
    if line_length % countCol > 0:
        rowsOccupied = whole_measures + 1
    else:
        rowsOccupied = whole_measures
    return rowsOccupied
