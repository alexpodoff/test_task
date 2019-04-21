import os
import random

from helper.db import DbWorker


db = DbWorker("z:/tmp/test_data.db")
unic_id = db.get_uniq_id()
test_path = 'z:/tmp'


def test_get_expected_value():
    assert db.get_expected_value({'a': [1, 1, 1, 2, 3]}) == {"a": 1.6}


def test_get_percentile():
    assert db.get_percentile({'a': [1, 1, 1, 2, 3]}) == {'a': 2.8}


def test_get_std_dev_value():
    assert db.get_std_dev_value({'a': [1, 1, 1, 2, 3]}) == {'a': 0.8}


def test_get_data_for_graphs():
    lst = [('1', 1), ('1', 1), ('1', 1), ('1', 2), ('1', 3), ('2', 2), ('2', 2)]
    assert db.get_data_for_graphs(lst) == [['1', '2'], [1.6, 2.0]]


def test_build_graph_by_id():
    _id = random.choice(unic_id)
    db.build_graph_by_id(_id, test_path)
    assert os.path.exists(f'{test_path}/graphic_{_id}.png')
    os.remove(f'{test_path}/graphic_{_id}.png')


def test_build_histogram_by_id():
    _id = random.choice(unic_id)
    db.build_histogram_by_id(_id, test_path)
    assert os.path.exists(f'{test_path}/histogram_{_id}.png')
    os.remove(f'{test_path}/histogram_{_id}.png')


def test_get_value():
    _id = unic_id[65]
    assert db.get_value([_id], 'opt_sess_contents') == {'Июньский Марж.Амер.Put.57500 Фьюч.контр Si-6.18': [20, 20, 20]}


def test_get_deal_count_in_seconds():
    assert len(db.get_deal_count_in_second("2018-05-04 15:00:00")) == 11


def test_get_uniq_id():
    assert len(db.get_uniq_id()) == 79


if __name__ == "__main__":

    test_get_expected_value()
    test_get_percentile()
    test_get_std_dev_value()
    test_get_data_for_graphs()
    test_build_graph_by_id()
    test_build_histogram_by_id()
    test_get_value()
    test_get_deal_count_in_seconds()
    test_get_uniq_id()
