# -*- coding: utf-8 -*-
from config import mode
import scraper

if __name__ == '__main__':
    if mode == "NewBills":
        scraper.main()