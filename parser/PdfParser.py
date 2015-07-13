from PyPDF2.pdf import PdfFileReader
import sys
import subprocess

class Indexer(object):
    def __init__(self, path):
        self.path = path
        self.pages = None
        self.meta_data = None
        try: 
            with open(self.path,'rb') as fp:
                pdf = PdfFileReader(fp)
                self.meta_data =  pdf.getDocumentInfo()
                self.pages = pdf.getNumPages()
        except (IOError,TypeError) as e:
                print(e)
        except:
                print("Unexpected error:", sys.exc_info()[0])

    def get_content(self):
        if not self.pages:
            args = ['pdftotext', '-raw', '-q', self.path, '-']
            return [subprocess.check_output(args).decode('utf-8')]

        result = []

        for page in range(0,self.pages):
            p = str(page+1)
            arg = ['pdftotext', '-f', p, '-l', p, '-raw', '-q', self.path, '-']
            result.append(subprocess.check_output(arg).decode('utf-8'))

        return result

    def get_metadata(self):
        return self.meta_data

