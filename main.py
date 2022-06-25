from fakturownia_com import FaktTalker
from odoo_com import OdooTalker
from datetime import datetime


def synchronize_dbs():
    ft = FaktTalker()
    ot = OdooTalker()

    ot.get_last_order()
    ot.get_last_invoice()

    ord_date = ot.last_order_date
    inv_date = ot.last_invoice_date

    ord_date_dt = datetime.strptime(ord_date, "%Y-%m-%d")
    inv_date_dt = datetime.strptime(inv_date, "%Y-%m-%d")

    if ord_date_dt < inv_date_dt:
        date = ord_date
    else:
        date = inv_date

    ft.get_documents(date)

    ft.prepare_estimates()
    ot.get_estimates(ft.estimates_to_odoo)
    ot.upload_estimates()

    ft.prepare_invoices()
    ot.get_invoices(ft.invoices_to_odoo)
    ot.upload_invoices()
