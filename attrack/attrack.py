import cv2

'''
亮度调低攻击
'''
def bright_att(input_file_path,output_file_path,ratio = 0.8):
    input_file = cv2.imread(input_file_path)
    output_file = input_file * ratio
    output_file[output_file > 255] = 255
    cv2.imread(output_file_path,output_file)

