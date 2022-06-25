import datetime
import os
import requests


FAKTUROWNIA_TOKEN = os.environ.get("FAKTUROWNIA_TOKEN")
FAKTUROWNIA_ENDPOINT = os.environ.get("FAKTUROWNIA_ENDPOINT")
FAKTUROWNIA_PARAMETERS = {
    "include_positions": "true",
    "period": "more",
    "date_from": "2021-09-15",
    "date_to": "2021-10-15",
    "per_page": 200,
    "api_token": FAKTUROWNIA_TOKEN,
}
odoo_parameters = {
    # "id": "id",
    # "osoba wystawiajaca": "seller_person",
    "x_numer": "number",
    "x_nabywca": "buyer_name",
    "x_nip_nabywcy": "buyer_tax_no",
    "x_data_wystawienia_tekst": "issue_date",
    "x_wartosc_netto_pln": "price_net",
    "x_vat": "price_tax",
    "x_waluta": "currency",
    "x_numer_zamowienia": "oid",
    "x_uwagi": "description",
}

invoice_parameters = {
    "x_name": "number",
    "x_typ": "kind_text",
    "x_nabywca_fakturownia": "buyer_name",
    "x_nip_nabywcy": "buyer_tax_no",
    "x_data_wystawienia_tekst": "issue_date",
    "x_wartosc_netto": "price_net",
    "x_wartosc_brutto": "price_gross",
    "x_vat": "price_tax",
    "x_waluta": "currency",
    "x_numer_zamowienia_fakturownia": "oid",
    "x_uwagi": "description",
}

estimate_position_parameters = {
    "x_name": "name",
    "x_ilosc": "quantity",
    "x_cena_netto": "price_net",
    "x_wartosc_netto": "total_price_net",
}


class FaktTalker:
    def __init__(self):
        self.document_list = None
        self.estimates = None
        self.invoices = None
        self.parameters = FAKTUROWNIA_PARAMETERS

    def get_documents(self, date):
        print(f"Getting documents since {date}")
        self.parameters["date_from"] = date
        self.parameters["date_to"] = datetime.datetime.today().strftime("%Y-%m-%d")
        print(self.parameters["date_from"])
        print(self.parameters["date_to"])
        response = requests.get(FAKTUROWNIA_ENDPOINT, self.parameters)
        self.document_list = response.json()
        print(len(self.document_list))
        self.categorize_docs()
        # print(self.parameters['date_to'])

    def categorize_docs(self):
        types = ["vat", "final", "export_products", "correction", "receipt", "wdt"]
        print("Categorizing documents")
        self.estimates = [
            doc for doc in self.document_list if doc["kind"] == "estimate"
        ]
        print(f"liczba zamowien: {len(self.estimates)}")
        self.invoices = [doc for doc in self.document_list if doc["kind"] in types]
        print(self.invoices[0])

    def print_docs(self):
        for num, doc in enumerate(self.document_list):
            print(f"{num}. date: {doc['issue_date']} = {doc['number']}")

    def prepare_estimates(self):
        print("Preparing estimates to upload to odoo")
        estimates_to_odoo = []
        for estimate in self.estimates:
            ex_rate = float(estimate["exchange_rate"])
            fields_dict = {
                key: estimate[value] for key, value in odoo_parameters.items()
            }
            fields_dict["x_wartosc_netto_pln"] = float(
                fields_dict["x_wartosc_netto_pln"]
            )
            fields_dict["x_wartosc_netto_pln"] *= ex_rate
            num = estimate["number"].split("ZAM ")[1]
            positions = []
            for item in estimate["positions"]:
                position_dict = {
                    key: item[value]
                    for key, value in estimate_position_parameters.items()
                }
                position_dict["x_numer"] = estimate["number"]
                position_dict["x_ilosc"] = float(position_dict["x_ilosc"])
                positions.append(position_dict)
            pos_names = [position["x_name"] for position in positions]
            name = num + " " + ", ".join(pos_names)
            fields_dict["x_name"] = name
            estimate_dict = {
                "fields": fields_dict,
                "positions": positions,
            }

            estimates_to_odoo.append(estimate_dict)
        self.estimates_to_odoo = estimates_to_odoo

    def prepare_invoices(self):
        print("Preparing invoices to upload to odoo")
        invoices_to_odoo = []
        for invoice in self.invoices:
            ex_rate = float(invoice["exchange_rate"])
            fields_dict = {
                key: invoice[value] for key, value in invoice_parameters.items()
            }
            fields_dict["x_wartosc_netto"] = float(fields_dict["x_wartosc_netto"])
            fields_dict["x_wartosc_netto"] *= ex_rate
            fields_dict["x_studio_kurs_wymiany"] = ex_rate
            positions = []
            for item in invoice["positions"]:
                position_dict = {
                    key: item[value]
                    for key, value in estimate_position_parameters.items()
                }
                position_dict["x_numer_faktury"] = invoice["number"]
                position_dict["x_ilosc"] = float(position_dict["x_ilosc"])

                if (
                    "rozliczenie" not in position_dict["x_name"].lower()
                    and "zaliczki" not in position_dict["x_name"].lower()
                ):
                    positions.append(position_dict)

            invoice_dict = {
                "fields": fields_dict,
                "positions": positions,
            }

            invoices_to_odoo.append(invoice_dict)
        self.invoices_to_odoo = invoices_to_odoo

    def print_est_to_odoo(self):
        for n, est in enumerate(self.estimates_to_odoo):
            print(f"{n}. {est}")

    def print_inv_to_odoo(self):
        for n, inv in enumerate(self.invoices_to_odoo):
            print(f"{n}. {inv}")
