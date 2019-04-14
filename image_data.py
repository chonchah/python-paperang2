#!/usr/bin/python3
# -*-coding:utf-8-*-

import numpy as np
import skimage.color, skimage.transform, skimage.filters, skimage.feature
import skimage as ski


def _pack_block(bits_str: str) -> bytearray:
    # bits_str are human way (MSB:LSB) of representing binary numbers (e.g. "1010" means 12)
    if len(bits_str) % 8 != 0:
        raise ValueError("bits_str should have the length of ")
    partitioned_str = [bits_str[i:i + 8] for i in range(0, len(bits_str), 8)]
    int_str = [int(i, 2) for i in partitioned_str]
    return bytes(int_str)


def binimage2bitstream(bin_image: np.ndarray):
    # bin_image is a numpy int array consists of only 1s and 0s
    # input follows thermal printer's mechanism: 1 is black (printed) and 0 is white (left untouched)
    assert bin_image.max() <= 1 and bin_image.min() >= 0
    return _pack_block(''.join(map(str, bin_image.flatten())))


def im2binimage(im, conversion="threshold"):
    # convert standard numpy array image to bin_image
    fixed_width = 384
    if (len(im.shape) != 2):
        im = ski.color.rgb2gray(im)
    im = ski.transform.resize(im, (round( fixed_width /im.shape[1]  * im.shape[0]), fixed_width))
    if conversion == "threshold":
        ret = (im < ski.filters.threshold_li(im)).astype(int)
    elif conversion == "edge":
        ret = 1- (1 - (ski.feature.canny(im, sigma=2)))
    else:
        raise ValueError("Unsupported conversion method")
    return ret


