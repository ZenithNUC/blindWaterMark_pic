import numpy
import cv2
import random
import argparse

ALPHA = 5

'''
构造参数语句
'''
def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='sourceImage', required=True)            # 原图
    parser.add_argument('-m', dest='markedImage', required=True)            # 加注过水印的图片
    parser.add_argument('-r', dest='resImage', required=True)               # 提取结果
    parser.add_argument('--a', dest='alphaValue', default=ALPHA)
    return parser

'''
获取构造参数
'''
def option_value():
    parser = create_parser()
    options = parser.parse_args()
    sImage = options.sourceImage
    mImage = options.markedImage
    rImage = options.resImage
    alpha = float(options.alphaValue)
    return sImage,mImage,rImage,alpha,parser

