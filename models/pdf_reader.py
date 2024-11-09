import PyPDF2 # type: ignore

class PDFReader:
    def read_pdf(self, file_path):
        text = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfFileReader(file)
            for page in range(reader.numPages):
                text += reader.getPage(page).extract_text() + "\n"
        return text
