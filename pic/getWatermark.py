import numpy as np
import cv2
import random
import argparse
import os

ALPHA = 3

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

'''
解出水印
'''
def decode(sImage,mImage,rImage,alpha):
    sImg = cv2.imread(sImage)
    sImg_f = np.fft.fft2(sImg)
    mImg = cv2.imread(mImage)
    mImg_f = np.fft.fft2(mImg)
    sHeight,sWidth,sChannel = np.shape(sImg)
    watermark = (sImg_f - mImg_f) / alpha
    watermark = np.real(watermark)                  # 返回watermark的实部
    res = np.zeros(watermark.shape)
    random.seed(sHeight + sWidth)
    x = list(range(sHeight // 2))
    y = list(range(sWidth))
    random.shuffle(x)
    random.shuffle(y)
    for i in range(sHeight // 2):
        for j in range(sWidth):
            res[x[i]][y[j]] = watermark[i][j]
    cv2.imwrite(rImage,res,[int(cv2.IMWRITE_JPEG_QUALITY), 100])

def main():
    sImage,mImage,rImage,alpha,parser = option_value()
    if not os.path.isfile(sImage):
        parser.error("original image %s does not exist." % sImage)
    if not os.path.isfile(mImage):
        parser.error("image %s does not exist." % mImage)
    decode(sImage,mImage,rImage,alpha)