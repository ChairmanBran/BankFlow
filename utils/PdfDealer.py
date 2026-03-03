from pypdf import PdfReader, PdfWriter
from pathlib import Path

class PdfCutter:
   def __init__(self, pdf_routine: str, pdf_dir_name:str) -> None:
      path = Path(pdf_dir_name)
      path.mkdir(parents=True, exist_ok=True)
      self.pdf_dir_name = pdf_dir_name  #pdf文件夹，分割成单独页面的PDF文件将存入这里
      if self._is_pdf_file(pdf_routine):
         self.pdf_routine = pdf_routine  #原始待处理的银行流水PDF文件
      else:
         raise TypeError("文件必须得是PDF，暂不支持其它格式，请检查输入文件格式。")
      self.reader = PdfReader(self.pdf_routine)
      self.pdfs = []  #所有分割成单独页面的PDF文件合集

   def _is_pdf_file(self, file_path: str) -> bool:
      """
      判断是否为PDF文件（检查扩展名 + 文件头）
      PDF文件的魔术数字（Magic Number）：
      - 前4个字节：%PDF (25 50 44 46)
      """
      path = Path(file_path)
      if not path.exists():
         return False
      if not path.is_file():
         return False
      if path.suffix.lower() != '.pdf':
         return False
      try:
         with open(path, 'rb') as f:
               header = f.read(4)
               # PDF文件以 %PDF 开头（字节：25 50 44 46）
               pdf_bool = header == b'%PDF'
               if pdf_bool:
                  print("该文件是PDF！")
               else:
                  print("文件不是PDF！")
               return pdf_bool
      except (IOError, PermissionError):
         # 无法读取文件，仅根据扩展名判断
         return True

   def cut_pdf(self):
      # 分割为单独的页面，并存入pdf_dir_name
      for page_num in range(len(self.reader.pages)):
         writer = PdfWriter()
         writer.add_page(self.reader.pages[page_num])
         pdf_name = f"{self.pdf_dir_name}page_{page_num + 1}.pdf"
         self.pdfs.append(pdf_name)
         with open(pdf_name, "wb") as output:
            writer.write(output)

if __name__ == "__main__":
   pdf_routine = "ChinaMerchantsBankAccounting.pdf"
   dir_name = "pdfs/"
   cutter = PdfCutter(pdf_routine, dir_name)
   cutter.cut_pdf()
