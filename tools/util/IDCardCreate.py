# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: IDCardCreate.py

# @Software: PyCharm
import json
import random
import time

from RootDirectory import PROJECT_PATH
from api_test.utils import response


def get_address(code, data, address):
    if isinstance(data, dict):
        if code in list(data.keys()):
            if isinstance(data[code], dict):
                return address + data[code]['name']
            else:
                return address + data[code]
        else:
            _adb = address
            for key, value in data.items():
                address = _adb
                if isinstance(value, dict):
                    if value.get('child'):
                        address = get_address(code, value.get('child'), address + value['name'])
                        if address:
                            break
                else:
                    address = ''
    return address


def address_key(data, _list=[]):
    if isinstance(data, dict):
        for key, value in data.items():
            if key.isdigit():
                _list.append(key)
            address_key(value, _list)
    return _list


def generate_id(id_location=None, number=1, birthday=None, gender=None):
    """
    :param id_location: 区域code码
    :param birthday: 出身年月
    :param number: 数量
    :param gender: 控制性别，None为随机, 1:男，2：女
    :return: 身份证号码
    """
    _id_cards = dict()
    with open(PROJECT_PATH + '/Config/city.json', mode='r', encoding='utf-8') as f:
        districtcodes = json.load(f)
    address_code = address_key(districtcodes)
    loca = id_location
    for i in range(number):
        id_location = loca
        address = ''
        if not id_location:
            id_location = random.choice(address_code)
        address = get_address(id_location, districtcodes, address)
        if not address:
            return False, response.CITY_CODE_NOT_FIND
        if not birthday:
            # 8位生日编码
            date_start = time.mktime((1900, 1, 1, 0, 0, 0, 0, 0, 0))
            date_end = time.mktime((2019, 8, 1, 0, 0, 0, 0, 0, 0))

            date_int = random.randint(date_start, date_end)
            id_date = time.strftime("%Y%m%d", time.localtime(date_int))
        else:
            id_date = birthday
        # 3位顺序码，末尾奇数-男，偶数-女
        id_order = 0
        if not gender:
            id_order = random.randint(0, 999)
        elif gender == 1:
            id_order = random.randint(0, 499) * 2 + 1
        elif gender == 2:
            id_order = random.randint(0, 499) * 2

        if id_order >= 100:
            id_order = str(id_order)
        elif id_order >= 10:
            id_order = "0" + str(id_order)
        else:
            id_order = "00" + str(id_order)

        id_former = id_location + id_date + id_order

        # 验证码
        weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]  # 权重项
        check_code = {
            '0': '1',
            '1': '0',
            '2': 'X',
            '3': '9',
            '4': '8',
            '5': '7',
            '6': '6',
            '7': '5',
            '8': '5',
            '9': '3',
            '10': '2'}  # 校验码映射

        _sum = 0
        for n, num in enumerate(id_former):
            _sum += int(num) * weight[n]
        id_check = check_code[str(_sum % 11)]

        id_card = id_former + id_check
        _id_cards[id_card] = address
    return True, _id_cards


if __name__ == '__main__':
    # for i in range(10):
    print(generate_id(id_location='640502', number=50, birthday=None, gender=1))
