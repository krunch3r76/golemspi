import textwrap

# from .rows_occupied import rows_occupied


def _get_printable_range_wrapped(
    lines,
    k_last_line_offset=None,
    countRows=None,
    countCols=None,
    win=None,
    padding=None,
):
    """return range of lines that can be printed to the window without overrunning
    Args:
        lines: line buffer
        k_last_line_offset: last line that should be displayed from lines
        [countCols]: window length
        [countRows]: window height
        [win]: target window *deprecated*

    Returns:
        None if there are no lines
        (offset to the highest visible line, offset to the bottom line)

    """
    if len(lines) == 0:
        return None
    if k_last_line_offset is None:
        k_last_line_offset = len(lines) - 1
    if all(map(lambda ele: ele is None, [countCols, countRows, win])):
        raise UnboundLocalError("no display parameters provided")
    if k_last_line_offset < 0 or k_last_line_offset > (len(lines) - 1):
        raise IndexError(
            f"only non-negative or existing offsets allowed; k_last_line_offset: {k_last_line_offset}, len(lines)-1: {len(lines)-1}"
        )

    top_offset = k_last_line_offset
    next_effective_row_count = 0
    count_rows_occupied = 0
    while top_offset >= 0 and next_effective_row_count <= countRows:
        # Calculate rows occupied by the line when it's wrapped
        wrapped_line = textwrap.wrap(lines[top_offset], countCols)
        count_rows_occupied = len(wrapped_line)
        next_effective_row_count += count_rows_occupied
        top_offset -= 1
    top_offset += 1
    if next_effective_row_count > countRows:
        top_offset += 1
    if top_offset < 0:
        top_offset = 0

    return (top_offset, k_last_line_offset)


# def _get_printable_range(
#     lines,
#     k_last_line_offset=None,
#     countRows=None,
#     countCols=None,
#     win=None,
#     padding=None,
# ):
#     """return range of lines that can be printed to the window without overrunning
#     Args:
#         lines: line buffer
#         k_last_line_offset: last line that should be displayed from lines or None for up to end
#         [countCols]: window length
#         [countRows]: window height
#         [win]: target window *deprecated*

#     Returns:
#         None if there are no lines
#         (start, end) where end is the offset to last line

#     """
#     if len(lines) == 0:
#         return None
#     if k_last_line_offset is None:
#         k_last_line_offset = len(lines) - 1
#     if all(map(lambda ele: ele is None, [countCols, countRows, win])):
#         raise UnboundLocalError("no display parameters provided")
#     if k_last_line_offset < 0 or k_last_line_offset > (len(lines) - 1):
#         raise IndexError(
#             f"only non-negative or existing offsets allowed; k_last_line_offset: {k_last_line_offset}, len(lines)-1: {len(lines)-1}"
#         )

#     top_offset = k_last_line_offset
#     next_effective_row_count = 0
#     count_rows_occupied = 0
#     while top_offset >= 0 and next_effective_row_count <= countRows:
#         count_rows_occupied = rows_occupied(countCols, lines[top_offset])
#         next_effective_row_count += count_rows_occupied
#         top_offset -= 1

#     # rows_occupied_by_last_line = rows_occupied(countCols, lines[save_k_last_line_offset])
#     if next_effective_row_count > countRows:
#         top_offset += 2  # why 2?
#     if top_offset < 0:
#         top_offset = 0

#     return (top_offset, k_last_line_offset + 1)


def get_printable_range(
    lines,
    last_line_offset=None,
    countRows=None,
    countCols=None,
    win=None,
    padding=None,
    wrapped=True,
):
    # get printable range up to end less scroll_off_current
    # printable_range = None
    if len(lines) == 0:
        return None

    if last_line_offset is None:
        linecount = len(lines)
        if linecount == 0:
            return None
        last_line_offset = linecount - 1

    if all(map(lambda ele: ele is None, [countCols, countRows, win])):
        raise UnboundLocalError("no display parameters provided")
    if last_line_offset < 0 or last_line_offset > (len(lines) - 1):
        raise IndexError(
            f"only non-negative or existing offsets allowed; last_line_offset: {last_line_offset}, len(lines): {len(lines)}"
        )

    if wrapped:
        return _get_printable_range_wrapped(
            lines,
            last_line_offset,
            countRows=countRows,
            countCols=countCols,
            win=win,
        )
    # else:
    #     return _get_printable_range(
    #         lines,
    #         last_line_offset,
    #         countRows=countRows,
    #         countCols=countCols,
    #         win=win,
    #     )
