from pathlib import Path
from openpyxl import Workbook

class DataToExcel:
    def __init__(self, data: list, save_routine: str, headers: list=None) -> None:
        self.headers = headers
        self.data = data
        self.save_routine = save_routine
    
    def _create_workbook(self):
        self.workbook = Workbook()
        self.active_worksheet = self.workbook.active
    
    def add_row(self, row_data: list):
        self.data.append(row_data)
    
    def save_xl(self):
        try:
            self._create_workbook()
            Path(self.save_routine).parent.mkdir(parents=True, exist_ok=True)
            self.active_worksheet.append(self.headers)
            for row in self.data:
                self.active_worksheet.append(row)
            self.workbook.save(self.save_routine)
            return True, f"成功将excel保存到：{self.save_routine}"
        except Exception as e:
            return False, f"错误: {e}"
