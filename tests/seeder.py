import decimal
import random

from faker import Faker
from faker.providers import BaseProvider

fake = Faker()


class PaymentDataProvider(BaseProvider):
    @staticmethod
    def payment_type():
        return random.choice(["DEBIT_ORDER", "CASH", "CLIENT_REFERRAL", "BANK_DEPOSIT"])

    @staticmethod
    def payment_amount():
        return random.uniform(20, 500)

    @staticmethod
    def status():
        return random.choice(["SUCCESSFUL", "FAILURE", "CANCELLED"])


fake.add_provider(PaymentDataProvider)
