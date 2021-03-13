from math import fabs, sqrt, inf

def dist(dot1, dot2):
    return sqrt((dot1[0] - dot2[0]) ** 2 + (dot1[1] - dot2[1]) ** 2)

# may be different directions of found edges
def dist_top_leg(tabletop_corner, tableleg):
    return min(
        dist(tabletop_corner, tableleg[0]),
        dist(tabletop_corner, tableleg[1]))


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
            tg15 = 0.267 # tangents 15 deg, cotangents 75

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



    print(f"top {estimated_tabletop} leg {estimated_tableleg}")

    estimated_tabletop_sorted = []

    for key in estimated_tabletop.keys():
        estimated_tabletop_sorted.append((key, estimated_tabletop.get(key)))

    estimated_tabletop_sorted.sort(key=lambda x: x[0][0])

    # detected front top, front bottom, back bottom
    # detected front top, back bottom
    # in both cases use it
    tabletop = max(estimated_tabletop_sorted[1][1], key=lambda x: fabs(x[1][0] - x[0][0]))

    # redirect tabletop from left to right
    if tabletop[0][0] > tabletop[1][0]:
        tabletop[0], tabletop[1] = tabletop[1], tabletop[0]

    tableleg_list = [v for k, v in estimated_tableleg.items()]
    tableleg_left = max(estimated_tableleg.items(), key= lambda x:
                        min(x[1], key=lambda y: dist_top_leg(tabletop[0], y)))

    tableleg_right = max(estimated_tableleg.items(), key=lambda x:
                        max(x[1], key=lambda y: dist_top_leg(tabletop[1], y)))

    return tabletop, tableleg_left, tableleg_right
