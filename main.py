from barcode_creator import BarcodeCreator


# function for generation list of barcode texts
def generate_barcodes():
    barcodes: list = []
    for i in range(1, 100):
        barcodes.append(f'OB01{BarcodeCreator.format_int(i)}')
    return barcodes


if __name__ == '__main__':
    barcode_creator: BarcodeCreator = BarcodeCreator()
    barcode_creator.create_barcodes(generate_barcodes())
    barcode_creator.create_pdf_documents()
