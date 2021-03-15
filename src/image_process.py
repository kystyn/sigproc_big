from math import fabs
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from imageio import imread, imsave
from skimage.color import rgb2gray
from skimage.filters import gaussian
from skimage.feature import canny
from skimage.transform import (hough_line, hough_line_peaks)


def prepare_img(img_name):
    img = imread(img_name)

    # img = img0
    # # remove light
    # for y in range(img0.shape[0] // 2):
    #     for x in range(200, img0.shape[1] - 200):
    #         if img0[y, x][1] > img0[y, x + 200][1] + 70 and img[y][x + 200][1] < 80 and\
    #                 img0[y, x][1] > img0[y, x - 200][1] + 70 and img[y][x - 200][1] < 80:
    #             img[y, x] = img0[y, x + 200]

    img_gray = rgb2gray(img)
    img_edges = canny(img_gray, sigma=2.0, low_threshold=0.05)

    lines_y = []

    h, theta, d = hough_line(img_edges)
    for _, angle, dist in zip(*hough_line_peaks(h, theta, d)):
        y0 = int((dist - 0 * np.cos(angle)) / np.sin(angle))
        y1 = int((dist - img.shape[1] * np.cos(angle)) / np.sin(angle))
        lines_y.append((y0, y1))

    return img, img_edges, lines_y


def show_processed_img(img, img_edges, lines_y):
    f, ax = plt.subplots(1, 3, figsize=(10, 5))
    ax[0].set_title("Source")
    ax[1].set_title("Edges")
    ax[0].imshow(img)
    ax[1].imshow(img_edges, cmap="gray")

    ax[2].imshow(img_edges, cmap="gray")
    for y0, y1 in lines_y:
        ax[2].plot((0, img.shape[1]), (y0, y1), '-r')

        #tga = (y1 - y0) / img_edges.shape[1]
        #ax[2].plot((0, img.shape[1]), (y0, y1), '-r')
        #ax[2].plot((0, 1000), (y0 + 0 * tga, y0 + 1000 * tga), '-b')

    ax[2].set_xlim((0, img.shape[1]))
    ax[2].set_ylim((img.shape[0], 0))
    ax[2].set_axis_off()
    ax[2].set_title('Detected lines')
    plt.show()


def find_edges_per_xy(x, y, img_edges, start, lastpt, edges, min_edge_dist, neighbourhood):
    if y < neighbourhood // 2 or y > img_edges.shape[0] - neighbourhood // 2 - 1 or\
            x < neighbourhood // 2 or x > img_edges.shape[1] - neighbourhood // 2 - 1:
        return start, lastpt

    is_line_point = False
    for hy in range(y - neighbourhood // 2, y + neighbourhood // 2 + 1):
        for hx in range(x - neighbourhood // 2, x + neighbourhood // 2 + 1):
            if img_edges[hy, hx] is np.True_:
                is_line_point = True

    if is_line_point:
        if start == (-1, -1):
            start = (x, y)
            lastpt = (x, y)
        elif (x - lastpt[0]) ** 2 + (y - lastpt[1]) ** 2 > min_edge_dist ** 2:
            edges.append((start, lastpt))
            start = (-1, -1)
        else:
            lastpt = (x, y)

    return start, lastpt


def find_edge_length(y0, y1, img_edges, neighbourhood=12, min_edge_dist=20):
    tga = (y1 - y0) / img_edges.shape[1]
    tg75 = 3.7

    start = (-1, -1)
    lastpt = (-1, -1)

    edges = []

    # for horizontal lines
    if fabs(tga) < tg75:
        for x in range(neighbourhood, img_edges.shape[1] - neighbourhood):
            y = int(y0 + x * tga)
            start, lastpt = find_edges_per_xy(x, y, img_edges, start, lastpt, edges, min_edge_dist, neighbourhood)
    # for vertical lines
    else:
        for y in range(min(y0, y1), max(y0, y1)):
            x = int((y - y0) / tga)
            start, lastpt = find_edges_per_xy(x, y, img_edges, start, lastpt, edges, min_edge_dist, neighbourhood)

    edges.append((start, lastpt))
    return edges


def find_edges(lines_list, img_edges):
    edges = {}
    for y0, y1 in lines_list:
        #print(f"y0: {y0} y1: {y1}")
        res = find_edge_length(y0, y1, img_edges)
        edges[(y0, y1)] = res
        #for start, end in res:
        #    print(f"count: {sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)}")

    return edges
