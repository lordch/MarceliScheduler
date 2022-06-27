from fakturownia_com import FaktTalker
from odoo_com import OdooTalker


def synchronize_dbs():
    ft = FaktTalker()
    ot = OdooTalker()

    ft.get_documents()

    ft.prepare_estimates()
    ot.get_estimates(ft.estimates_to_odoo)
    ot.upload_estimates()

    ft.prepare_invoices()
    ot.get_invoices(ft.invoices_to_odoo)
    ot.upload_invoices()
