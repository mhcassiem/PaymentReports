import json
from datetime import datetime
from abc import ABC
from typing import Any, Union

import consts
from utils.file_utils import read_file, write_file


class Payment:
    """
    Payment class, ideally this would be a database migration. For the purposes of the task, creating it so that if
    this feature needs to fit in a larger web app it can be added easily and Django will automatically generate
    the migration for it. It just needs to inherit from the base db model class
    """

    def __init__(
        self,
        payment_id: int,
        payment_type: str,
        payment_amount: float,
        payment_signature_image: str or None,
        payment_photo: str or None,
        created: datetime,
        status: str,
        notes: str or None,
        agent_user_id: int,
        device_id: int,
    ):
        self.id = payment_id
        self.payment_type = payment_type
        self.payment_amount = payment_amount
        self.payment_signature_image = payment_signature_image
        self.payment_photo = payment_photo
        self.created = created
        self.status = status
        self.notes = notes
        self.agent_user_id = agent_user_id
        self.device_id = device_id


class PaymentFile:
    """
    Class to interface with file upload of transactions. Not intended to be a database model
    but can be adapted to point to a file upload in AWS S3.
    """

    def __init__(self, filename: str, output_folder: str):
        self.report_types = {
            consts.SUSPENSION_REPORT: self.create_suspension_report,
            consts.AGENT_COLLECTION_REPORT: self.create_agent_collection_report,
            consts.PAYMENT_TYPE_REPORT: self.create_payment_type_report,
        }
        self.filename = filename
        self.output_folder = output_folder
        self.payments = []
        self.client_accounts = {}
        self.agent_summaries = {}
        self.payments_report = {}

    def read_payment_file(self, data: dict or None = None):
        """
        Reads file data, packages into list of payments
        :return list:
        """
        data = read_file(self.filename) if not data else data
        result = []
        for id in data:
            pmnt = data[id]
            payment = Payment(
                int(id),
                pmnt["payment_type"],
                float(pmnt["payment_amount"]),
                pmnt["payment_signature_image"],
                pmnt["payment_photo"],
                datetime.strptime(pmnt["created"], "%Y-%m-%d %H:%M:%S"),
                pmnt["status"],
                pmnt["notes"],
                int(pmnt["agent_user_id"]),
                int(pmnt["device_id"]),
            )
            result.append(payment)
        self.payments = result

    def parse_payment_data(self):
        if len(self.payments) == 0:
            print("Payment data not loaded.")
            return

        today = datetime.now()
        # using dictionaries for time complexity efficiency
        # single key lookup is O(1)
        client_accounts = {}
        agent_summaries = {}
        payment_types = {}

        # Build up report data in a single pass through file rows
        for payment in self.payments:
            created_date = payment.created.date().strftime("%Y-%m-%d")
            days_from_suspension = (payment.created - today).days + 91
            client_accounts[payment.device_id] = (
                days_from_suspension if days_from_suspension > 0 else 0
            )
            agent_summary = agent_summaries.get(payment.agent_user_id, {})
            date_summary = agent_summary.get(created_date, {})
            date_summary[payment.payment_type] = (
                date_summary.get(payment.payment_type, 0) + payment.payment_amount
            )
            agent_summary[created_date] = date_summary
            agent_summaries[payment.agent_user_id] = agent_summary

            payment_types[payment.payment_type] = (
                payment_types.get(payment.payment_type, 0) + payment.payment_amount
            )

        # storing report results
        # this would be analogous to a database insert
        # to generate the actual report we just need to sort, like a select statement
        self.client_accounts, self.agent_summaries, self.payments_report = (
            client_accounts,
            agent_summaries,
            payment_types,
        )

    def create_suspension_report(self) -> list:
        data = []
        for account, days_since_payment in sorted(
            self.client_accounts.items(), key=lambda kv: -kv[1]
        ):
            data.append([account, days_since_payment])
        return data

    def create_agent_collection_report(self) -> list:
        data = []
        for agent_id, dates in sorted(self.agent_summaries.items(), key=lambda a: a[0]):
            for date, payment_types in sorted(dates.items(), key=lambda k: k[0]):
                for p_type in payment_types:
                    data.append([agent_id, date, p_type, payment_types[p_type]])
        return data

    def create_payment_type_report(self) -> list:
        data = []
        for p_type, total in sorted(self.payments_report.items(), key=lambda p: p[0]):
            data.append([p_type, total])
        return data

    def write_reports(self):
        if (
            not bool(self.payments_report)
            and not bool(self.agent_summaries)
            and not bool(self.client_accounts)
        ):
            self.parse_payment_data()
        for report in self.report_types:
            write_file(
                self.output_folder, f"{report}_report.csv", self.report_types[report]()
            )
