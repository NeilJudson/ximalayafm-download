import sys

sys.path.append('../')

from ximalayafm_analyze import *


def main():
    ximalaya = Ximalaya('https://www.ximalaya.com/renwen/11021595/')
    ximalaya.download_list()


if __name__ == '__main__':
    main()
