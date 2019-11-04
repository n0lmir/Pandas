import logging
import math
import time


path = "D:\\Python\\Test\\log.txt"
path2 = "D:\\Python\\Test\\logWithLogger.txt"

try:
    def my_func(num):
        num2 = math.sqrt(num)
        return num2

    input1 = input()
    my_func(input1)
except Exception as e:
    f = open(path, 'a')
    f.write("Error! {0}, ocurreed on {1}".format(str(e), time.asctime()))
    f.write("\n")
    f.close()
    logging.basicConfig(filename=path2, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger=logging.getLogger(__name__)
    logger.error(e)