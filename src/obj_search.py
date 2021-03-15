from math import fabs, sqrt, inf
from enum import Enum


class ChairPosition(Enum):
    VERTICAL = 1
    HORIZONTAL_ALONG_BACK_ON_FLOOR = 2
    HORIZONTAL_ALONG_BACK_ORTHO_FLOOR = 3
    HORIZONTAL_ACROSS = 4
    STILL_UNKNOWN = 5


def dist(dot1, dot2):
    return sqrt((dot1[0] - dot2[0]) ** 2 + (dot1[1] - dot2[1]) ** 2)


# may be different directions of found edges
def dist_top_leg(tabletop_corner, tableleg):
    return min(
        dist(tabletop_corner, tableleg[0]),
        dist(tabletop_corner, tableleg[1]))


# line == (y0, y1)
def tg_line(imgw, line):
    return (line[1] - line[0]) / imgw if line[1] != line[0] else inf


def find_table(lines, img_edges):
    """
    :param lines: list of tuples ((y_start, y_end), edge_length)
    :return: horizontal line, 2 vertical lines
    """
    # need 1 horizontal line and 2 vertical

    # horizontal
    estimated_tabletop = {}
    estimated_tableleg = {}
    for key in lines.keys():
        check_tabletop = True
        check_tableleg = True

        # do not add too near lines
        for key_tabletop in estimated_tabletop.keys():
            if fabs(key[0] - key_tabletop[0]) < 30 or fabs(key[1] - key_tabletop[1]) < 30:
                check_tabletop = False
                break

        for key_tableleg in estimated_tableleg.keys():
            if fabs(key[0] - key_tableleg[0]) < 30 or fabs(key[1] - key_tableleg[1]) < 30:
                check_tableleg = False
                break

        if not check_tabletop and not check_tableleg:
            continue

        for start, end in lines.get(key):
            tga = (start[1] - end[1]) / (start[0] - end[0]) if start[0] != end[0] else inf
            ctga = (start[0] - end[0]) / (start[1] - end[1]) if start[1] != end[1] else inf

            line_len = sqrt((start[1] - end[1]) ** 2 + (start[0] - end[0]) ** 2)
            tg15 = 0.267  # tangents 15 deg, cotangents 75

            if fabs(tga) < tg15 and line_len > 0.2 * img_edges.shape[1] \
                    and key[0] < 0.3 * img_edges.shape[0]:
                if check_tabletop:
                    if estimated_tabletop.get(key) is None:
                        estimated_tabletop[key] = []
                    estimated_tabletop[key].append((start, end))
            elif fabs(ctga) < tg15 and line_len > 0.15 * img_edges.shape[0]:
                if check_tableleg:
                    if estimated_tableleg.get(key) is None:
                        estimated_tableleg [key] = []
                    estimated_tableleg[key].append((start, end))


    #print(f"top {estimated_tabletop} leg {estimated_tableleg}")

    estimated_tabletop_sorted = []

    for key in estimated_tabletop.keys():
        estimated_tabletop_sorted.append((key, estimated_tabletop.get(key)))

    estimated_tabletop_sorted.sort(key=lambda x: x[0][0])

    # detected front top, front bottom, back bottom
    # detected front top, back bottom
    # in both cases use it
    out_idx = -1 #len(estimated_tabletop_sorted) - 1
    if len(estimated_tabletop_sorted) == 0:
        return None
    in_idx = min(len(estimated_tabletop_sorted[out_idx]) - 1, 1)
    tabletop = \
        max(estimated_tabletop_sorted[out_idx][in_idx], key=lambda x: fabs(x[1][0] - x[0][0]))

    # redirect tabletop from left to right
    if tabletop[0][0] > tabletop[1][0]:
        tabletop[0], tabletop[1] = tabletop[1], tabletop[0]

    tableleg_left = max(estimated_tableleg.items(), key= lambda x:
                        min(x[1], key=lambda y: dist_top_leg(tabletop[0], y)))

    tableleg_right = max(estimated_tableleg.items(), key=lambda x:
                        max(x[1], key=lambda y: dist_top_leg(tabletop[1], y)))

    return tabletop, tableleg_left, tableleg_right


def find_chair_position(edges, img_edges):
    """
    :param edges:
    :param img_edges:
    :return: ChairPosition exemplar
    """
    status, estimated_line_list = detect_horizontal(img_edges.shape[1], img_edges.shape[0], edges)
    if status != ChairPosition.STILL_UNKNOWN:
        return status, estimated_line_list

    status, estimated_line_list = detect_vertical(img_edges.shape[1], img_edges.shape[0], edges)
    if status != ChairPosition.STILL_UNKNOWN:
        return status, estimated_line_list

    return ChairPosition.HORIZONTAL_ACROSS, []


def detect_vertical(imgw, imgh, edges):
    estimated_chair = []
    for line in edges.keys():
        if fabs(line[1] - line[0]) < imgh * 0.1 and max(line[0], line[1]) > 0.75 * imgh:
            chair = max(edges.get(line), key=lambda x: dist(x[0], x[1]))
            if 0.25 * imgw < dist(chair[0], chair[1]):
                estimated_chair.append(chair)

    return ChairPosition.HORIZONTAL_ACROSS, estimated_chair


def detect_horizontal(imgw, imgh, edges):
    # list of potential pairs
    estimated_line_list = []
    tg10 = 0.17
    tg15 = 0.27
    tg30 = 0.58
    tg45 = 1
    tg60 = 1.73

    ordered_keys = [key for key in edges.keys()]
    for i in range(len(ordered_keys)):
        line1 = ordered_keys[i]
        tgline1 = tg_line(imgw, line1)
        if tg15 < fabs(tgline1) < tg60:
            for j in range(i + 1, len(ordered_keys)):
                line2 = ordered_keys[j]
                tgline2 = tg_line(imgw, line2)
                if tg30 < fabs(tgline2) < tg45 and tgline1 * tgline2 > 0:
                    if tg10 < fabs((tgline2 - tgline1) / (1 + tgline1 * tgline2)) < tg30 and\
                            -0.3 * imgh < line1[0] < 1.3 * imgh and\
                            -0.3 * imgh < line1[1] < 1.3 * imgh and\
                            -0.3 * imgh < line2[1] < 1.3 * imgh and\
                            -0.3 * imgh < line2[1] < 1.3 * imgh:
                        estimated_line_list.append((line1, line2))

    low_horizontal_lines_count = 0
    for l in edges.keys():
        low_horizontal_lines_count +=\
            (imgh * 0.75 < l[0] < imgh and
             imgh * 0.75 < l[1] < imgh and
             l[1] - l[0] < 0.1 * imgw)

    status = ChairPosition.STILL_UNKNOWN

    if len(estimated_line_list) > 0:
        if low_horizontal_lines_count >= 3:
            status = ChairPosition.HORIZONTAL_ALONG_BACK_ON_FLOOR
        else:
            status = ChairPosition.HORIZONTAL_ALONG_BACK_ORTHO_FLOOR

    if low_horizontal_lines_count >= 2:
        status = ChairPosition.HORIZONTAL_ALONG_BACK_ON_FLOOR

    return status, estimated_line_list


def make_decision(tabletop, chair_pos, estimated_line_list):
    if chair_pos == ChairPosition.VERTICAL:
        return False
    if chair_pos == ChairPosition.HORIZONTAL_ACROSS:
        return False
    if chair_pos == ChairPosition.HORIZONTAL_ALONG_BACK_ORTHO_FLOOR:
        return True
    if chair_pos == ChairPosition.HORIZONTAL_ALONG_BACK_ON_FLOOR:
        return True
