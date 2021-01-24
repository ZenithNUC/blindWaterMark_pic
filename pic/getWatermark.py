import numpy
import cv2
import argparse

ALPHA = 5

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='sourceImage', required=True)
    parser.add_argument('-m', dest='markedImage', required=True)
    parser.add_argument('-r', dest='resImage', required=True)
    parser.add_argument('--a', dest='alpha', default=ALPHA)
    return parser