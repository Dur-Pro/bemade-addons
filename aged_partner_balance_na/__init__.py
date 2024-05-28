from . import models


def post_init(env):
    env.['account.report'].search([('name', 'ilike', 'aged_%_report_na')]).unlink()
    new_receivable_report =  env.ref('account_reports.aged_receivable_report').copy()
    new_payable_report = env.ref('account_reports.aged_payable_report').copy()
    new_receivable_report.line_ids.mapped('expression_ids').write({
        'formula': '_report_custom_engine_aged_receivable_na'
    })
    new_payable_report.line_ids.mapped('expression_ids').write({'formula': '_report_custom_engine_aged_payable_na'})
    new_receivable_report.write({
        'name': 'Aged Receivable - North America',
        'root_report_id': env.ref('account_reports.aged_receivable_report').id,
        'availability_condition': 'always',
    })
    new_payable_report.write({
        'name': 'Aged Payable - North America',
        'root_report_id': env.ref('account_reports.aged_payable_report').id,
        'availability_condition': 'always',
    })
    col_name_mapping = [
        ('At Date', '0-29'),
        ('1-30', '30-59'),
        ('31-60', '60-89'),
        ('61-90', '90-119'),
        ('91-120', '120-159'),
        ('Older', 'Later'),
    ]
    for old_name, new_name in col_name_mapping:
        ((new_payable_report | new_receivable_report)
         .mapped('column_ids')
         .filtered(lambda col: col.name == old_name)).write({'name': new_name})
