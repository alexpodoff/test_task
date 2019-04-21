from helper.report import ReportWorker
from helper.db import DbWorker


db = DbWorker("z:/tmp/test_data.db")
uniq_id = db.get_uniq_id()
opt = db.get_value(uniq_id, db.opt_sess_contents)
fut = db.get_value(uniq_id, db.fut_sess_contents)
d = dict(opt)
d.update(fut)
exp_val = db.get_expected_value(d)
std_dev = db.get_std_dev_value(d)
percent_val = db.get_percentile(d)
deals_by_sec = db.get_deal_by_sec()

db.build_histograms(uniq_id, db.opt_sess_contents, 'z:/tmp/histograms/png')
db.build_graphics(uniq_id, db.opt_sess_contents, 'z:/tmp/graphics/png')

report = ReportWorker('z:/tmp/test_task.xlsx')
report.create_report()

report.fill_sheet1(db)
report.fill_sheet2(exp_val, std_dev, percent_val)
report.fill_sheet3(deals_by_sec)

report.convert_all_in_bmp("z:/tmp/histograms/png", "z:/tmp/histograms/bmp")
report.convert_all_in_bmp("z:/tmp/graphics/png", "z:/tmp/graphics/bmp")

report.fill_sheet4("z:/tmp/histograms/bmp", "z:/tmp/graphics/bmp")
report.save_report()
