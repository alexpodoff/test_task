import os
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class DbWorker:

    def __init__(self, database):
        self.connection = sqlite3.connect(database=database)
        self.deal = "deal"
        self.fut_sess_contents = "fut_sess_contents"
        self.opt_sess_contents = "opt_sess_contents"

    def count_lines(self, table):
        """
        Returns line count in table
        :param table: str
        :return: int
        """
        cursor = self.connection.cursor()
        cursor.execute(f"select count(*) from {table}")
        return cursor.fetchall()[0][0]

    def get_deal_by_sec(self):
        """
        Returns dictionary filled by second as key, number of deals as value
        :return: dict
        """
        cursor = self.connection.cursor()
        cursor.execute("select strftime('%H:%M:%S', moment),count(id_deal) from deal group by id_deal")
        lst = [row for row in cursor]
        dic = {}
        for i in range(0, len(lst)):
            if lst[i][0] not in dic:
                dic[lst[i][0]] = lst[i][1]
            else:
                dic[lst[i][0]] += lst[i][1]
        cursor.close()
        return dic

    def get_deal_count_in_second(self, date):
        """
        Returns deal count list for specific second if needed
        takes string this kind: '%H:%M:%S'
        :param date: str
        :return: list
        """
        time = date.split(' ')[1].split(':')
        start = datetime(2018, 5, 4, int(time[0]), int(time[1]), int(time[2]))
        step = timedelta(seconds=1)
        stop = str(start + step)
        lst = []
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                f"select id_deal from deal where moment >= '{start}' and moment < '{stop}'")
            lst = [row[0] for row in cursor]
        finally:
            cursor.close()
            return lst

    def get_order_sum(self, val):
        """
        Returns sum of values. Used for counting xamount and price
        :param val: str
        :return: float
        """
        order_sum = 0
        cursor = self.connection.cursor()
        try:
            order_sum = cursor.execute(f"select sum({val}) from deal").fetchall()[0][0]
        finally:
            cursor.close()
            return order_sum

    def get_uniq_id(self):
        """
        Returns list of uniq ids from deal
        :return: list
        """
        unic_id = []
        cursor = self.connection.cursor()
        try:
            cursor.execute("select distinct isin_id from deal")
            unic_id = [row[0] for row in cursor]
        finally:
            cursor.close()
            return unic_id

    def get_value(self, unic_id, table):
        """
        Returns dict with name of instrument as key and list of prices
        for this instrument as value from specified table
        :param unic_id: list
        :param table: str
        :return: dict
        """
        dic = {}
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                f"select o.isin_id,o.name,d.price from {table} o inner join deal d on o.isin_id=d.isin_id")
            lst = [row for row in cursor]
            for i in range(0, len(lst)):

                for j in unic_id:
                    if lst[i][0] == j:
                        if lst[i][1] in dic:
                            dic[lst[i][1]].append(lst[i][2])
                        else:
                            dic[lst[i][1]] = [lst[i][2]]
        finally:
            cursor.close()
            return dic

    def build_histogram_by_id(self, _id, path, show=False):
        """
        Creates PNG file with histogram of price probabilit for specified id
        Puts it in path dir. With show=True shows picture instead
        :param _id: int
        :param path: str
        :param show: bool
        :return: None
        """
        self.mkdir(path)
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"select strftime('%H:%M:%S', moment),price from deal where isin_id={_id}")
            data = self.get_data_for_graphs([row for row in cursor])
        finally:
            cursor.close()
        name = self.get_name_by_id(_id)
        plt.hist(data[1], rwidth=0.8, bins=15)
        plt.title(f"Распределение цены на \n{name[0]}")
        plt.ylabel('Probability')
        plt.xlabel('Price')
        if show is True:
            plt.show()
        plt.savefig(f'{path}/histogram_{str(_id)}')
        plt.close()

    def build_graph_by_id(self, _id, path, show=False):
        """
        Creates PNG file with graphic of price by time for specified id
        Puts it in path dir. With show=True shows picture instead
        :param _id:
        :param path:
        :param show:
        :return:
        """
        self.mkdir(path)
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"select strftime('%H', moment),price from deal where isin_id={_id}")
            data = self.get_data_for_graphs([row for row in cursor])
        finally:
            cursor.close()
        name = self.get_name_by_id(_id)
        plt.plot(data[0], data[1])
        plt.title(f'Цена на {name[0]}')
        plt.ylabel('Price')
        plt.xlabel('Time')
        if show is True:
            plt.show()
        plt.savefig(f'{path}/graphic_{str(_id)}')
        plt.close()

    def build_histograms(self, unic_id, table, path):
        """
        Builds histograms for instruments from table. Puts them in path dir
        :param unic_id: list
        :param table: str
        :param path: str
        :return: NOne
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                f"select o.isin_id,o.name,d.price from {table} o inner join deal d on o.isin_id=d.isin_id")
            lst = [row for row in cursor]
            for i in range(0, len(lst)):
                for j in unic_id:
                    if lst[i][0] == j:
                        self.build_histogram_by_id(j, path)
        finally:
            cursor.close()

    def build_graphics(self, unic_id, table, path):
        """
        Builds graphics for instruments from table. Puts them in path dir
        :param unic_id: list
        :param table: str
        :param path: str
        :return: None
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                f"select o.isin_id,o.name,d.price from {table} o inner join deal d on o.isin_id=d.isin_id")
            lst = [row for row in cursor]
            for i in range(0, len(lst)):
                for j in unic_id:
                    if lst[i][0] == j:
                        self.build_graph_by_id(j, path)
        finally:
            cursor.close()

    def get_name_by_id(self, _id):
        """
        Returns name of instrument by its id.
        First searches in opt_sess_contents, if not - searches in fut_sess_contents
        :param _id: int
        :return: tuple
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"select name from opt_sess_contents where isin_id={_id}")
            lst = [row for row in cursor]
            if len(lst) == 0:
                cursor.execute(f"select name from fut_sess_contents where isin_id={_id}")
                name = [row for row in cursor][0]
            else:
                name = lst[0]
        finally:
            cursor.close()
        return name

    @staticmethod
    def get_data_for_graphs(lst):
        """
        Gets list of [(moment, price)] values
        Returns list of mean values fo each hour
        :param lst: list
        :return: list
        """
        dic = {}
        for i in range(0, len(lst)):
            if lst[i][0] in dic:
                dic[lst[i][0]].append(lst[i][1])
            else:
                dic[lst[i][0]] = [lst[i][1]]

        for i in dic.keys():
            dic[i] = np.mean(dic[i])
        x = [*dic]
        y = [dic[i] for i in dic]
        return [x, y]

    @staticmethod
    def get_expected_value(dic):
        """
        Gets dict of name as key and list of ints as value
        Returns dict of name as key and float of mean value of list as value
        :param dic: dict
        :return: dict
        """
        new_dic = {}
        for i in dic.keys():
            new_dic[i] = np.mean(dic[i])
        return new_dic

    @staticmethod
    def get_std_dev_value(dic):
        """
        Gets dict of name as key and list of ints as value
        Returns dict of name as key and float of standard deviation value of list as value
        :param dic: dict
        :return: dict
        """
        new_dic = {}
        for i in dic.keys():
            new_dic[i] = np.std(dic[i])
        return new_dic

    @staticmethod
    def get_percentile(dic):
        """
        Gets dict of name as key and list of ints as value
        Returns dict of name as key and float of percentile 95% of list as value
        :param dic: dict
        :return: dict
        """
        new_dic = {}
        for i in dic.keys():
            new_dic[i] = np.percentile(dic[i], 95)
        return new_dic

    @staticmethod
    def mkdir(path):
        """
        Checks if dir exists. Creates one if not
        :param path: str
        :return:
        """
        if not os.path.exists(path):
            os.makedirs(path)
