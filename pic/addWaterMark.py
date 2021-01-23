import cv2
import numpy as np
import argparse
import random

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

'''
获取构造参数
'''
def option_value():
    parser = create_parser()
    options = parser.parse_args()
    sImage = options.sourceImage
    wImage = options.wmImage
    rImage = options.resImage
    return sImage,wImage,rImage

'''
在图片中加水印
'''
def encode(sImage,wImage,rImage,alpha):
    sImg = cv2.imread(sImage)
    sImg_f = np.fft.fft2(sImg)                  # 对原图计算二维的傅里叶变换
    sHeight,sWidth,sChannel = np.shape(sImg)
    wImg = cv2.imread(wImage)
    wImg_f = np.fft.fft2(wImg)                  # 对水印计算二维的傅里叶变换
    wHeight,wWigth,wChannel = np.shape(wImg)
    x,y = range(sHeight / 2),range(sWidth)
    random.seed(sHeight + sWidth)
    random.shuffle(x)
    random.shuffle(y)
    temp = np.zeros(sImg.shape)
    for i in range(sHeight / 2):
        for j in range(sWidth):
            if x[i] < wHeight and y[j] <wWigth:
                temp[i][j] = wImg[x[i]][y[j]]
                temp[sHeight - 1 - i][sWidth - 1 - j] = temp[i][j]
    rImg_f = sImg_f + alpha * temp
    rImg = np.fft.ifft2(rImg_f)
    rImg = np.real(rImg)
    cv2.imwrite(rImage,rImg,[int(cv2.IMWRITE_JPEG_QUALITY), 100])
