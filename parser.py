import os
import fitz  # PyMuPDF
from PIL import Image

def convert_pdfs_to_images(input_dir, output_dir):
    """
    Converts PDF files containing "qp" in their filename from a directory 
    to images (PNG format) and saves them in a specified output directory.

    Args:
        input_dir (str): The path to the directory containing PDF files.
        output_dir (str): The path to the directory where images will be saved.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Create the output directory if it doesn't exist

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf") and "qp" in filename:
            filepath = os.path.join(input_dir, filename)
            try:
                pdf_document = fitz.open(filepath)  # Open the PDF with PyMuPDF
                for page_number in range(pdf_document.page_count):
                    page = pdf_document.load_page(page_number)
                    pix = page.get_pixmap() # Get the image of the page
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                    # Construct the output filename (e.g., "filename_page1.png")
                    base_filename = os.path.splitext(filename)[0]
                    output_filename = f"{base_filename}_page{page_number + 1}.png"
                    output_filepath = os.path.join(output_dir, output_filename)
                    img.save(output_filepath, "PNG")

                pdf_document.close()
                print(f"Converted {filename} to images in {output_dir}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")


# --- Example Usage ---
input_directory = r"D:\Papers Code\9701\Paper 1"  # Replace with the actual path to your PDF directory
output_directory = r"D:\Papers Code\9701\Paper 1_images" # Specify the output directory

convert_pdfs_to_images(input_directory, output_directory)

print("Conversion process complete.")