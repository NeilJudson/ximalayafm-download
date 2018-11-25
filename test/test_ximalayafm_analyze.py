import sys

sys.path.append('../')

from ximalayafm_analyze import *


def main():
    ximalaya = Ximalaya('https://www.ximalaya.com/renwen/6574791/')
    ximalaya.download_list()


if __name__ == '__main__':
    main()
