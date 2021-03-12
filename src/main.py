from src.image_process import *
from src.obj_search import *

if __name__ == '__main__':
    img, img_edges, lines = prepare_img('../data/photo_2021-02-11_21-55-54.jpg')
    edges = find_edges(lines, img_edges)
    find_table(edges, img_edges)
    show_processed_img(img, img_edges, lines)

    #img, img_edges, lines = prepare_img('../data/photo_2021-02-11_21-55-55.jpg')
    #detect_needed_lines(lines, img_edges)
    #show_processed_img(img, img_edges, lines)