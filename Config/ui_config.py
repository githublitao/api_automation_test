from RootDirectory import Ui_PROJECT_PATH
import os
root_path = Ui_PROJECT_PATH
air_path = os.path.join(Ui_PROJECT_PATH, 'test_case')
log_path = os.path.join(Ui_PROJECT_PATH,'log')
report_path = os.path.join(Ui_PROJECT_PATH,'report')
template_path = os.path.join(Ui_PROJECT_PATH,'template')
data_path = os.path.join(Ui_PROJECT_PATH,'data')
template_name = "template_summary.html"


#设置设备号，以及选择跑全部用例，还是选择files
#devices = ['']

devices = ['']


