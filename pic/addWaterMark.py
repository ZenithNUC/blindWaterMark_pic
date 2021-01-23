import cv2
import numpy as np
import argparse

ALPHA = 5

'''
构造命令行
'''
def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',dest='sourceImage',required=True)          # 需要加水印的原图
    parser.add_argument('-w',dest='wmImage',required=True)              # 水印图
    parser.add_argument('-r',dest='resImage',required=True)             # 输出结果
    parser.add_argument('--a',dest='alphaValue',default=ALPHA)          # ALPHA值
    return parser
