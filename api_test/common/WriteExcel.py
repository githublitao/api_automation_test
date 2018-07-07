import logging

import xlsxwriter

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


class Write:
    def __init__(self, project_name):
        self.workbook = xlsxwriter.Workbook(project_name)
        self.worksheet = self.workbook.add_worksheet()
        bold = self.workbook.add_format({'bold': True})
        self.worksheet.write(0, 0, "编号", bold)
        self.worksheet.write(0, 1, "模块", bold)
        self.worksheet.write(0, 2, "业务", bold)
        self.worksheet.write(0, 3, "接口名称", bold)
        self.worksheet.write(0, 4, "接口地址", bold)
        self.worksheet.write(0, 5, "请求头", bold)
        self.worksheet.write(0, 6, "请求方式", bold)
        self.worksheet.write(0, 7, "参数", bold)
        self.worksheet.write(0, 8, "预期结果", bold)
        self.worksheet.write(0, 9, "实际结果", bold)
        self.worksheet.write(0, 10, "创建人", bold)
        self.worksheet.write(0, 11, "最近修改时间", bold)
        self.worksheet.set_column(1, 3, 15)
        self.worksheet.set_column(4, 4, 20)
        self.worksheet.set_column(5, 6, 30)
        self.worksheet.set_column(7, 9, 30)
        self.worksheet.set_column(11, 11, 15)

    def write_case(self, data=None):
        row = 1
        _row = 1
        # self.worksheet.write(row, 0, row)
        # self.worksheet.write(row, 1, i["automationGroupLevelFirst"])
        for i in data:
            for n in i["api"]:
                self.worksheet.write(row, 0, row)
                self.worksheet.write(row, 3, n["name"])
                row = row+1
        for j in data:
            merge_format = self.workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
            })
            self.worksheet.merge_range(_row, 2, _row+len(j["api"])-1, 2, j["caseName"], merge_format)
            _row = _row + len(j["api"])
        self.workbook.close()
        return True

