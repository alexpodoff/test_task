import os
import random

from helper.db import DbWorker


db = DbWorker("z:/tmp/test_data.db")
unic_id = db.get_uniq_id()


def test1():
    assert db.get_expected_value({'a': [1, 1, 1, 2, 3]}) == {"a": 1.6}


def test2():
    assert db.get_percentile({'a': [1, 1, 1, 2, 3]}) == {'a': 2.8}


def test3():
    assert db.get_std_dev_value({'a': [1, 1, 1, 2, 3]}) == {'a': 0.8}


def test4():
    lst = [('1', 1), ('1', 1), ('1', 1), ('1', 2), ('1', 3), ('2', 2), ('2', 2)]
    assert db.get_data_for_graphs(lst) == [['1', '2'], [1.6, 2.0]]


def test5():
    _id = random.choice(unic_id)
    db.build_graph_by_id(_id, 'z:/tmp')
    assert os.path.exists(f'z:/tmp/graphic_{_id}.png')


def test6():
    _id = random.choice(unic_id)
    db.build_histogram_by_id(_id, 'z:/tmp')
    assert os.path.exists(f'z:/tmp/histogram_{_id}.png')


def test7():
    _id = unic_id[65]
    assert db.get_value([_id], 'opt_sess_contents') == {'Июньский Марж.Амер.Put.57500 Фьюч.контр Si-6.18': [20, 20, 20]}


if __name__ == "__main__":

    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()
