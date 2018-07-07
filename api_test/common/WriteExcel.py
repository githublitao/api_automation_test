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
        self.worksheet.write(0, 5, "请求方式", bold)
        self.worksheet.write(0, 6, "请求头", bold)
        self.worksheet.write(0, 7, "参数", bold)
        self.worksheet.write(0, 8, "校验方式", bold)
        self.worksheet.write(0, 9, "预期HTTP状态", bold)
        self.worksheet.write(0, 10, "预期结果", bold)
        self.worksheet.write(0, 11, "实际结果", bold)
        self.worksheet.write(0, 12, "创建人", bold)
        self.worksheet.write(0, 13, "最近修改时间", bold)
        self.worksheet.set_column(1, 3, 15)
        self.worksheet.set_column(4, 4, 20)
        self.worksheet.set_column(6, 7, 30)
        self.worksheet.set_column(10, 11, 30)

    def write_case(self, data=None):
        if not data:
            return True
        row = 1
        case_row = 1
        module_row = 1
        merge_format = self.workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
        })
        # self.worksheet.write(row, 0, row)
        # self.worksheet.write(row, 1, i["automationGroupLevelFirst"])
        for i in data:
            for n in i["api"]:
                self.worksheet.write(row, 0, row)
                self.worksheet.write(row, 3, n["name"])
                self.worksheet.write(row, 4, n["httpType"].lower()+"://xxxx"+n["apiAddress"])
                self.worksheet.write(row, 5, n["requestType"])
                header = {}
                try:
                    for m in n["header"]:
                        header[m["name"]] = m["value"]
                except Exception as e:
                    logging.exception(e)
                self.worksheet.write(row, 6, str(header))
                try:
                    if n["requestParameterType"] == "form-data":
                        param = {}
                        for m in n["parameterList"]:
                            param[m["name"]] = m["value"]
                    else:
                        param = n["parameterRaw"][0]["data"]
                except Exception as e:
                    logging.exception(e)
                    param = ""
                self.worksheet.write(row, 7, str(param))
                check = {
                    'no_check': '不校验',
                    'only_check_status': '校验http状态',
                    'json': 'JSON校验',
                    'entirely_check': '完全校验',
                    'Regular_check': '正则校验',
                }
                self.worksheet.write(row, 8, check[n["examineType"]])
                if n["httpCode"]:
                    self.worksheet.write(row, 9, n["httpCode"])
                if n["responseData"]:
                    self.worksheet.write(row, 10, n["responseData"])
                self.worksheet.write(row, 12, i["user"])
                self.worksheet.write(row, 13, i["updateTime"])
                row = row+1
            self.worksheet.merge_range(module_row, 1, module_row + row-2, 1, i["automationGroupLevelFirst"], merge_format)
        for j in data:
            self.worksheet.merge_range(case_row, 2, case_row+len(j["api"])-1, 2, j["caseName"], merge_format)
            case_row = case_row + len(j["api"])
        self.workbook.close()
        return True

