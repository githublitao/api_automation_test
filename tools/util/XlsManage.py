# -*- coding: utf-8 -*-


# @Author  : litao

# @Project : api_automation_test

# @FileName: XlsManage.py

# @Software: PyCharm
import sys

import xlrd


class ReadExcel:
    def __init__(self, file_path):
        self.workbook = xlrd.open_workbook(file_path)
        self.data = self.workbook.sheet_by_index(0)
        self.nrows = ""
        self.ncols = ""

    def __enter__(self):
        self.nrows = self.data.nrows
        self.ncols = self.data.ncols
        if self.nrows < 2 or self.ncols < 8:
            return False
        elif not self.check_format(self.data.row_values(0)):
            return False
        else:
            return self

    @staticmethod
    def check_format(value):
        expect = ['目录', '用例名称', '摘要', '关键字', '用例级别', '预置条件', '操作步骤', '预期结果']
        for i in range(0, 7):
            if value[i] != expect[i]:
                return False
        return True

    def nrow_value(self):
        _list = list()
        for n in range(1, int(self.nrows)):
            print()
            _dict = {
                "testsuiteid": self.data.cell_value(n, 0),
                "testcasename": self.data.cell_value(n, 1),
                "summary": self.data.cell_value(n, 2),
                "keyword": self.data.cell_value(n, 3),
                "level": self.data.cell_value(n, 4) if self.data.cell_value(n, 4) in ["低", "中", "高"] else "中",
                "preconditions": self.data.cell_value(n, 5),
                "step": self.data.cell_value(n, 6),
                "except": self.data.cell_value(n, 7),
            }
            _list.append(_dict)
        return _list

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


if __name__ == "__main__":
    with ReadExcel(r"123.xlsx") as b:
        if isinstance(b, bool):
            print(False)
        else:
            print(b.nrow_value())

