import datetime
import json
import os
import unittest

from tests.seeder import fake

from models.payment import PaymentFile


class TestSuspensionReport(unittest.TestCase):
    def setUp(self) -> None:
        self.fake = fake
        start = datetime.datetime.now()
        print("Starting seed.....")
        payments = {}
        for i in range(0, 5):
            payment_id = self.fake.random_int()
            # this will give us 3 payments less than 90 days ago, and 2 greater than
            # hence we should expect 3 non-suspended users at the top of the list
            # and 2 at the bottom
            created_at = datetime.datetime.now() - datetime.timedelta(days=35 * i)
            payments[payment_id] = {
                "id": payment_id,
                "payment_type": self.fake.payment_type(),
                "payment_amount": self.fake.payment_amount(),
                "payment_signature_image": self.fake.image_url(),
                "payment_photo": self.fake.image_url(),
                "created": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": self.fake.status(),
                "notes": self.fake.text(),
                "agent_user_id": self.fake.random_int(),
                "device_id": self.fake.random_int(),
            }
        self.payments = payments
        self.payments_file = PaymentFile(self.fake.uuid4(), "output_folder")
        self.payments_file.read_payment_file(self.payments)
        self.payments_file.parse_payment_data()
        end = datetime.datetime.now()
        print(f"Done. Time elapsed: {end-start}")

    def test_suspension_report(self):
        print("Beginning suspension report test...")
        start = datetime.datetime.now()
        suspension_report = self.payments_file.create_suspension_report()
        self.assertGreater(suspension_report[0][1], 0)
        self.assertEqual(suspension_report[-1][1], 0)
        end = datetime.datetime.now()
        print(f"Done. Time elapsed: {end - start}")


class TestAgentCollectionReport(unittest.TestCase):
    def setUp(self) -> None:
        self.fake = fake
        start = datetime.datetime.now()
        print("Starting seed.....")
        self.payments = {}

        for p_type in ["DEBIT_ORDER", "CASH", "CLIENT_REFERRAL", "BANK_DEPOSIT"]:
            agent_id = self.fake.random_int()
            created_at = self.fake.date_time_ad(
                start_datetime=datetime.datetime(2020, 1, 1, 1, 0, 0)
            ).strftime("%Y-%m-%d %H:%M:%S")
            for i in range(0, 3):
                payment_id = self.fake.random_int()
                self.payments[payment_id] = {
                    "id": payment_id,
                    "payment_type": p_type,
                    "payment_amount": 100,  # hard coding an amount, so we have something to assert against when testing
                    "payment_signature_image": self.fake.image_url(),
                    "payment_photo": self.fake.image_url(),
                    "created": created_at,
                    "status": self.fake.status(),
                    "notes": self.fake.text(),
                    "agent_user_id": agent_id,
                    "device_id": self.fake.random_int(),
                }

        self.payments_file = PaymentFile(self.fake.uuid4(), "output_folder")
        self.payments_file.read_payment_file(self.payments)
        self.payments_file.parse_payment_data()
        end = datetime.datetime.now()
        print(f"Done. Time elapsed: {end-start}")

    def test_agent_collection_report(self):
        print("Beginning agent collection report test...")
        start = datetime.datetime.now()
        collection_report = self.payments_file.create_agent_collection_report()
        for line in collection_report:
            self.assertEqual(line[3], 300.0)
        end = datetime.datetime.now()
        print(f"Done. Time elapsed: {end - start}")


class TestPaymentTypeReport(unittest.TestCase):
    def setUp(self) -> None:
        self.fake = fake
        start = datetime.datetime.now()
        print("Starting seed.....")
        self.payments = {}

        for p_type in ["DEBIT_ORDER", "CASH", "CLIENT_REFERRAL", "BANK_DEPOSIT"]:
            agent_id = self.fake.random_int()
            for i in range(0, 5):
                payment_id = self.fake.random_int()
                self.payments[payment_id] = {
                    "id": payment_id,
                    "payment_type": p_type,
                    "payment_amount": 100,
                    "payment_signature_image": self.fake.image_url(),
                    "payment_photo": self.fake.image_url(),
                    "created": self.fake.date_time_ad(
                        start_datetime=datetime.datetime(2020, 1, 1, 1, 0, 0)
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "status": self.fake.status(),
                    "notes": self.fake.text(),
                    "agent_user_id": agent_id,
                    "device_id": self.fake.random_int(),
                }

        self.payments_file = PaymentFile(self.fake.uuid4(), "output_folder")
        self.payments_file.read_payment_file(self.payments)
        self.payments_file.parse_payment_data()
        end = datetime.datetime.now()
        print(f"Done. Time elapsed: {end-start}")

    def test_payment_type_report(self):
        start = datetime.datetime.now()
        print("Starting seed.....")
        payment_type_report = self.payments_file.create_payment_type_report()
        for line in payment_type_report:
            self.assertEqual(line[-1], 500)
        end = datetime.datetime.now()
        print(f"Done. Time elapsed: {end - start}")


class LoadTestPayment(unittest.TestCase):
    def seedLoadTest(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.payments = {}
        try:
            with open(f"{dir_path}/seeds/loadtest.json") as datafile:
                if datafile:
                    print("Seed file found, loading data...")
                    self.payments = json.load(datafile)
        except Exception as e:
            print(f"Error loading seed file data.\n{e}\nGenerating new seed.....")
            # project spec stated max of 100000 payments per file
            for i in range(0, 100000):
                payment_id = self.fake.random_int()
                self.payments[payment_id] = {
                    "id": payment_id,
                    "payment_type": self.fake.payment_type(),
                    "payment_amount": self.fake.payment_amount(),
                    "payment_signature_image": self.fake.image_url(),
                    "payment_photo": self.fake.image_url(),
                    "created": self.fake.date_time_ad(
                        start_datetime=datetime.datetime(2020, 1, 1, 1, 0, 0)
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "status": self.fake.status(),
                    "notes": self.fake.text(),
                    "agent_user_id": self.fake.random_int(),
                    "device_id": self.fake.random_int(),
                }
        with open(f"{dir_path}/seeds/loadtest.json", "w") as savefile:
            json.dump(self.payments, savefile)

    def setUp(self) -> None:
        self.fake = fake
        start = datetime.datetime.now()
        print("Starting seed.....")
        self.seedLoadTest()
        self.payments_file = PaymentFile(self.fake.uuid4(), "output_folder")
        end = datetime.datetime.now()
        print(f"Done. Time elapsed: {end-start}")

    def tearDown(self) -> None:
        folder = "output_folder"
        print("Cleaning up output files.")
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                os.unlink(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))
        print("Test completed.")

    def test_payment_data(self):
        print("Beginning load test. Parsing payment data...")
        start = datetime.datetime.now()
        self.payments_file.read_payment_file(self.payments)
        self.payments_file.write_reports()
        end = datetime.datetime.now()
        print(f"Done. Time elapsed: {end - start}")
