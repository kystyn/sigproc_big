from image_process import *
from obj_search import *
import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Использование: python main.py path/to/image')
        exit(0)

    try:
        img, img_edges, lines = prepare_img(sys.argv[1])
        print("Файл: " + sys.argv[1])
    except FileNotFoundError:
        print("Файл " + sys.argv[1] + " не найден")
        exit(1)

    edges = find_edges(lines, img_edges)
    tabletop = find_table(edges, img_edges)
    chair_pos, estimated_line_list = find_chair_position(edges, img_edges)
    if make_decision(tabletop, chair_pos, estimated_line_list):
        print("Стул проходит под стол")
    else:
        print("Стул не проходит под стол")
    show_processed_img(img, img_edges, lines)
