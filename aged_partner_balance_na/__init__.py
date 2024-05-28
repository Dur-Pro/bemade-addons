from . import models


def post_init(env):
    new_receivable_report =  env.ref('account_reports.aged_receivable_report').copy()
    new_payable_report = env.ref('account_reports.aged_payable_report').copy()
    new_receivable_report.line_ids.mapped('expression_ids').write({
        'formula': '_report_custom_engine_aged_receivable_na'
    })
    new_payable_report.line_ids.mapped('expression_ids').write({'formula': '_report_custom_engine_aged_payable_na'})
