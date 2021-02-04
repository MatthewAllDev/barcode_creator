# Main settings
barcode_images_folder: str = 'images'
pdf_documents_folder: str = 'pdf'
remove_barcode_images: bool = True

# Barcode settings
code_width: int = 40
code_height: int = 10
font_size: int = 20
quiet_zone: int = 3
text_distance: int = 2

# PDF settings
num_grouping_characters: int = 4
document_orientation: str = 'L' # P or L
create_title_page: bool = True
title_page_orientation: str = 'L'  # P or L
title_font_size: int = 300
left_margin: int = 7
top_margin: int = 7
row_count: int = 10
columns_count: int = 6
horizontal_space: int = 1
vertical_space: int = 1
