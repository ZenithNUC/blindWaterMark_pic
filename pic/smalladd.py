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
        self.img,self.img_YUV = None,None
        self.ca,self.hvd, = [np.array([])] * 3, [np.array([])] * 3      # 每个通道 dct 的结果
        self.ca_block = [np.array([])] * 3                              # 每个 channel 存一个四维 array，代表四维分块后的结果
        self.ca_part = [np.array([])] * 3                               # 四维分块后，有时因不整除而少一部分，self.ca_part 是少这一部分的 self.ca
        self.wm_size, self.block_num = 0, 0                             # 水印的长度，原图片可插入信息的个数
        self.pool = ThreadPool(processes=cores)                         # 水印插入分块多进程

    def init_block_index(self):
        self.block_num = self.ca_block_shape[0] * self.ca_block_shape[1]
        assert self.wm_size < self.block_num,IndexError('最多可嵌入{}kb信息，多于水印的{}kb信息，溢出'.format(self.block_num / 1000, self.wm_size / 1000))
        # self.part_shape 是取整后的ca二维大小,用于嵌入时忽略右边和下面对不齐的细条部分。
        self.part_shape = self.ca_block_shape[:2] * self.block_shape
        self.block_index = [(i, j) for i in range(self.ca_block_shape[0]) for j in range(self.ca_block_shape[1])]

    '''
    读入图片->YUV化->加白边使像素变偶数->四维分块
    '''
    def read_img(self,filename):
        self.img = cv2.imread(filename).astype(np.float32)
        self.img_shape = self.img.shape[:2]
        # 如果不是偶数，那么补上白边
        self.img_YUV = cv2.copyMakeBorder(cv2.cvtColor(self.img, cv2.COLOR_BGR2YUV),0, self.img.shape[0] % 2, 0, self.img.shape[1] % 2,cv2.BORDER_CONSTANT, value=(0, 0, 0))
        self.ca_shape = [(i + 1) // 2 for i in self.img_shape]
        self.ca_block_shape = (self.ca_shape[0] // self.block_shape[0], self.ca_shape[1] // self.block_shape[1],self.block_shape[0], self.block_shape[1])
        strides = 4 * np.array([self.ca_shape[1] * self.block_shape[0], self.block_shape[1], self.ca_shape[1], 1])
        for channel in range(3):
            self.ca[channel], self.hvd[channel] = pywt.dwt2(self.img_YUV[:, :, channel], 'haar')
            # 转为4维度
            self.ca_block[channel] = np.lib.stride_tricks.as_strided(self.ca[channel].astype(np.float32),self.ca_block_shape, strides)

    '''
    读取水印图片
    
    '''
    def read_img_wm(self,filename):
        self.wm = cv2.imread(filename)[:,:,0]                       # 读入图片格式的水印，并转为一维 bit 格式
        self.wm_bit = self.wm.flatten() > 128                       # 加密信息只用bit类，抛弃灰度级别

    '''
    读取水印
    '''
    def read_wm(self,wm_content,mode = 'img'):
        if mode == 'img':
            self.read_img_wm(filename=wm_content)
        elif mode == 'str':
            byte = bin(int(wm_content.encode('utf-8').hex(),base=16))[2:]
            self.wm_bit = (np.array(list(byte)) == '1')
        else:
            self.wm_bit = np.array(wm_content)
        self.wm_size = self.wm_bit.size
        np.random.RandomState(self.password_wm).shuffle(self.wm_bit)

    '''
    分块添加水印
    '''
    def block_add_wm(self,arg):
        block,shuffler,i = arg
        # dct->flatten->加密->逆flatten->svd->打水印->逆svd->逆dct
        wm_1 = self.wm_bit[i % self.wm_size]
        block_dct = cv2.dct(block)              # 对块进行离散余弦变换
        block_dct_shuffled = block_dct.flatten()[shuffler].reshape(self.block_shape)        # 打乱顺序
        U,s,V = np.linalg.svd(block_dct_shuffled)
        s[0] = (s[0] // self.d1 + 1 / 4  + 1 / 2 *wm_1) * self.d1
        if self.d2:
            s[1] = (s[1] // self.d2 + 1 / 4  + 1 / 2 *wm_1) * self.d2
        block_dct_flatten = np.dot(U,np.dot(np.diag(s),V)).flatten()
        block_dct_flatten[shuffler] = block_dct_flatten.copy()
        return cv2.idct(block_dct_flatten.reshape(self.block_shape))