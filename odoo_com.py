import xmlrpc.client
import os

url = os.environ.get("ODOO_URL")
db = os.environ.get("ODOO_DB")
username = os.environ.get("ODOO_USERNAME")
password = os.environ.get("ODOO_PASSWORD")


class OdooTalker:
    def __init__(self):
        self.connect()

    def connect(self):
        print("Connecting to odoo...")
        self.common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(url))
        self.uid = self.common.authenticate(db, username, password, {})
        self.models = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(url))
        print("Connected to odoo")

    def get_last_order(self):
        print("Getting last order...")
        self.last_order = self.models.execute_kw(
            db,
            self.uid,
            password,
            "x_zamowienie_fakturownia",
            "search_read",
            [],
            {
                "fields": [
                    "x_name",
                    "x_numer",
                    "x_data_wystawienia",
                    "x_studio_status_1",
                ],
                "limit": 1,
                "order": "x_name desc",
            },
        )[0]
        self.last_order_date = self.last_order["x_data_wystawienia"]
        self.last_order_num = self.last_order["x_numer"]
        print(f"Last order date: {self.last_order_date}, number: {self.last_order_num}")

    def get_last_invoice(self):
        print("Getting last invoice...")
        self.last_invoice = self.models.execute_kw(
            db,
            self.uid,
            password,
            "x_faktura_sprzedazowa",
            "search_read",
            [],
            {
                "fields": ["x_name", "x_data_wystawienia"],
                "limit": 1,
                "order": "x_data_wystawienia desc",
            },
        )[0]
        self.last_invoice_date = self.last_invoice["x_data_wystawienia"]
        self.last_invoice_num = self.last_invoice["x_name"]
        print(
            f"Last invoice date: {self.last_invoice_date}, number: {self.last_invoice_num}"
        )

    def get_estimates(self, estimates):
        last_index = next(
            (
                index
                for index, estimate in enumerate(estimates)
                if estimate["fields"]["x_numer"] == self.last_order_num
            ),
            None,
        )
        print(last_index)
        # print(estimates[last_index]['fields']['x_numer'])
        self.estimates = estimates[:last_index]
        for num, estimate in enumerate(self.estimates):
            print(f"{num}. {estimate}")

    def get_invoices(self, invoices):
        self.invoices = invoices
        last_day_invoices = self.models.execute_kw(
            db,
            self.uid,
            password,
            "x_faktura_sprzedazowa",
            "search_read",
            [[["x_data_wystawienia", "=", self.last_invoice_date]]],
            {"fields": ["x_name"]},
        )
        print(len(self.invoices))
        last_day_invoice_numbers = [invoice["x_name"] for invoice in last_day_invoices]
        # print(last_day_invoice_numbers)
        self.invoices = [
            invoice
            for invoice in self.invoices
            if invoice["fields"]["x_name"] not in last_day_invoice_numbers
        ]
        print(len(self.invoices))

    def upload_estimates(self):
        for estimate in self.estimates[::-1]:
            print(f"creating new estimate: {estimate['fields']['x_numer']}")
            print(estimate["fields"])
            self.models.execute_kw(
                db,
                self.uid,
                password,
                "x_zamowienie_fakturownia",
                "create",
                [estimate["fields"]],
            )

            for position in estimate["positions"]:
                print(f"Creating new position: {position}")
                self.models.execute_kw(
                    db,
                    self.uid,
                    password,
                    "x_pozycja_zamowienia_fakturownia",
                    "create",
                    [position],
                )

    def upload_invoices(self):
        for invoice in self.invoices[::-1]:
            print(f"creating new invoice: {invoice['fields']['x_name']}")
            print(invoice["fields"])
            self.models.execute_kw(
                db,
                self.uid,
                password,
                "x_faktura_sprzedazowa",
                "create",
                [invoice["fields"]],
            )

            for position in invoice["positions"]:
                print(f"Creating new position: {position}")
                self.models.execute_kw(
                    db,
                    self.uid,
                    password,
                    "x_pozycja_faktury_sprzedazowej",
                    "create",
                    [position],
                )
