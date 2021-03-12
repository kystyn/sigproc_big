from math import fabs, sqrt, inf


def find_table(lines, img_edges):
    """
    :param lines: list of tuples ((y_start, y_end), edge_length)
    :return: horizontal line, 2 vertical lines
    """
    # need 1 horizontal line and 2 vertical

    # horizontal
    estimated_tabletop = []
    estimated_tableleg = []
    for key in lines.keys():
        for start, end in lines.get(key):
            tga = (start[0] - end[0]) / (start[1] - end[1]) if start[1] != end[1] else inf
            ctga = (start[1] - end[1]) / (start[0] - end[0]) if start[0] != end[0] else inf

            line_len = sqrt((start[1] - end[1]) ** 2 + (start[0] - end[0]) ** 2)
            tg15 = 0.267 # tangents 15 deg, cotangents 75

            if fabs(tga) < tg15 and line_len > 0.2 * img_edges.shape[1]:
                estimated_tabletop.append((start, end))
            elif fabs(ctga) < tg15 and line_len > 0.15 * img_edges.shape[0]:
                estimated_tableleg.append((start, end))
    return estimated_tabletop, estimated_tableleg