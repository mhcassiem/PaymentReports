from models.payment import PaymentFile
import os

if __name__ == "__main__":

    filepath = os.getenv("FILE_PATH")
    output_folder = os.getenv("OUTPUT_PATH")

    if not filepath:
        filepath = input("Fully qualified file path:")
    if not output_folder:
        output_folder = input("Output location:")
    payments_data = PaymentFile(filepath, output_folder)
    payments_data.read_payment_file()
    payments_data.write_reports()
