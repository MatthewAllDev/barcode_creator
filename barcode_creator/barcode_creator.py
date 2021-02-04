from barcode import Code128
from barcode.writer import ImageWriter
from fpdf import FPDF
import os
import multiprocessing
import config
from progress_bar import ProgressBar


class BarcodeCreator:
    def __init__(self):
        self.barcodes_dict: dict = {}

    def create_barcodes(self, barcodes_list: list):
        progress: ProgressBar = ProgressBar(len(barcodes_list))
        if not os.path.exists(config.barcode_images_folder):
            os.mkdir(config.barcode_images_folder)
        pool: multiprocessing.Pool = multiprocessing.Pool()
        results: list = []
        print('\nCreating barcodes...')
        progress.show()
        for barcode in barcodes_list:
            results.append(pool.apply_async(self.create_barcode_file, (barcode,)))
        for result in results:
            file: str = result.get(timeout=10)
            key: str = os.path.basename(file)[0:config.num_grouping_characters]
            if not key:
                key = 'barcodes'
            if key not in self.barcodes_dict:
                self.barcodes_dict[key] = [file]
            else:
                self.barcodes_dict[key].append(file)
            progress.inc()
            progress.show()

    @staticmethod
    def create_barcode_file(barcode_text):
        bc: Code128 = Code128(barcode_text, writer=ImageWriter())
        code_list: list = bc.build()
        code_size: int = len(code_list[0])
        options: dict = dict(font_size=config.font_size,
                             text_distance=config.text_distance,
                             module_width=config.code_width / code_size,
                             module_height=config.code_height,
                             quiet_zone=config.quiet_zone)
        return bc.save(f'{config.barcode_images_folder}/{barcode_text}', options)

    @staticmethod
    def format_int(number: int, length=4):
        number_str: str = str(number)
        for i in range(1, length - len(number_str) + 1):
            number_str = f'0{number_str}'
        return number_str

    def create_pdf_documents(self):
        pool: multiprocessing.Pool = multiprocessing.Pool()
        results: list = list()
        print('\nCreating PDF...')
        progress: ProgressBar = ProgressBar(len(self.barcodes_dict.keys()))
        progress.show()
        for key in self.barcodes_dict.keys():
            if config.create_title_page and key != 'barcodes':
                title: str or None = key
            else:
                title = None
            staging_folders: str = ''
            for i in range(1, config.num_grouping_characters):
                staging_folders += f'{key[0:i]}/'
            path: str = f'{config.pdf_documents_folder}/{staging_folders}{key}.pdf'
            folder_path: str = os.path.split(path)[0]
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            results.append(pool.apply_async(self.create_pdf_document, (self.barcodes_dict[key], path, title,)))
        for result in results:
            result.get(timeout=60)
            progress.inc()
            progress.show()
        self.barcodes_dict.clear()

    @staticmethod
    def create_pdf_document(barcodes_list: list, path: str, title: str = None):
        files_to_remove: list = list()
        pdf = FPDF(orientation=config.document_orientation, unit='mm', format='A4')
        if title:
            if config.title_page_orientation.upper() == 'P':
                cell_height: int = 266
            else:
                cell_height: int = 179
            pdf.add_page(config.title_page_orientation)
            pdf.set_font('Arial', size=config.title_font_size)
            pdf.cell(0, cell_height, txt=title, ln=1, align='C')
        image_width: float = config.code_width + config.quiet_zone * 2
        image_height: float = config.code_height + config.font_size * 0.35275 + config.text_distance
        row: int = 0
        column: int = 0
        pdf.add_page()
        for bc in barcodes_list:
            if row == config.row_count - 1 and column == config.columns_count:
                pdf.add_page()
                row = 0
                column = 0
            elif column == config.columns_count:
                row += 1
                column = 0
            y: float = image_height * row + config.vertical_space * row + config.top_margin
            x: float = image_width * column + config.horizontal_space * column + config.left_margin
            pdf.image(bc, x=x, y=y, w=image_width, h=image_height)
            column += 1
            if config.remove_barcode_images:
                try:
                    os.remove(bc)
                except PermissionError:
                    print(f'File {bc} busy with another process')
                    files_to_remove.append(bc)
        pdf.output(path)
        for file in files_to_remove:
            try:
                os.remove(file)
            except PermissionError:
                print(f'File {file} not deleted')
