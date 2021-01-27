import numpy as np
import copy
import cv2
import pywt
from multiprocessing.dummy import Pool as ThreadPool

class WaterMark:
    def __init__(self,password_wm = 1,password_img = 1,block_shape = (4,4),cores = None):
        self.block_shape = np.array(block_shape)
        self.password_wm, self.password_img = password_wm,password_img  # 打乱水印和打乱原图分块的随机种子
        self.d1,self.d2 = 36 , 20                                       # d1/d2 越大鲁棒性越强,但输出图片的失真越大

        # 初始数据
        self.img,self.img_YUY = None,None
        self.ca,self.hvd, = [np.array([])] * 3, [np.array([])] * 3      # 每个通道 dct 的结果
        self.ca_block = [np.array([])] * 3                              # 每个 channel 存一个四维 array，代表四维分块后的结果
        self.ca_part = [np.array([])] * 3                               # 四维分块后，有时因不整除而少一部分，self.ca_part 是少这一部分的 self.ca
        self.wm_size, self.block_num = 0, 0                             # 水印的长度，原图片可插入信息的个数
        self.pool = ThreadPool(processes=cores)                         # 水印插入分块多进程
