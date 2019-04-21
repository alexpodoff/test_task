import os
import xlwt
from PIL import Image
from helper.db import DbWorker


class ReportWorker:

    def __init__(self, report):
        self.report = report
        self.book = xlwt.Workbook(encoding="utf-8")
        self.sheet1 = self.book.add_sheet("Main")
        self.sheet2 = self.book.add_sheet("Scope")
        self.sheet3 = self.book.add_sheet("Deals")
        self.sheet4 = self.book.add_sheet("Diagrams")

    def create_report(self):
        self.sheet1.write(0, 0, 'Сделок за день:')
        self.sheet1.write(1, 0, 'суммарный объем сделок:')
        self.sheet1.write(2, 0, 'суммарный объем сделок в руб.:')

        self.sheet2.write(0, 0, "Финансовый инструмент")
        self.sheet2.write(0, 1, "Матиматическое ожидание цены")
        self.sheet2.write(0, 2, "Стандартное отклонение")
        self.sheet2.write(0, 3, "Перцентиль 95%")

        self.sheet3.write(0, 0, "Момент времени")
        self.sheet3.write(0, 1, "Кол-во сделок")

    def fill_sheet1(self, db):
        self.sheet1.write(0, 1, db.count_lines(db.deal))
        self.sheet1.write(1, 1, db.get_order_sum("xamount"))
        self.sheet1.write(2, 1, db.get_order_sum("price"))

    def fill_sheet2(self, dic1, dic2, dic3):
        row = 1
        for i in dic1:
            self.sheet2.write(row, 0, i)
            self.sheet2.write(row, 1, dic1[i])
            self.sheet2.write(row, 2, dic2[i])
            self.sheet2.write(row, 3, dic3[i])
            row += 1

    def fill_sheet3(self, dic):
        row = 1
        for i in dic:
            self.sheet3.write(row, 0, i)
            self.sheet3.write(row, 1, dic[i])
            row += 1

    def fill_sheet4(self, hist, graph):
        row = 0
        for i in os.listdir(hist):
            self.sheet4.insert_bitmap(hist+'/'+i, row, 0)
            row += 30
        row = 0
        for i in os.listdir(graph):
            self.sheet4.insert_bitmap(graph+'/'+i, row, 12)
            row += 30

    def save_report(self):
        self.book.save(self.report)

    @staticmethod
    def convert_and_save_image(image, path):
        """
        Converted PNG image file into BMP and puts it in path dir
        :param image: str
        :param path: str
        :return: None
        """
        img = Image.open(image)
        r, g, b, a = img.split()
        img = Image.merge("RGB", (r, g, b))
        image_name = image.split(".")[0].split('/')[-1]
        img.save(f'{path}/{image_name}.bmp')
        img.close()

    def convert_all_in_bmp(self, path, new_path):
        """
        Converted all PNG images from path into BMP and puts it in new_path
        :param path: str
        :param new_path: srt
        :return: None
        """
        DbWorker.mkdir(new_path)
        for i in os.listdir(path):
            self.convert_and_save_image(path+'/'+i, new_path)
