import asyncio

from utils import PdfCutter, PdfClaudeAsker, DataToExcel, JsonToExcelRowValue
from configs import Config

def main(pdf_routine):
    dir_name = Config().get("paths.pdf_dir")
    cutter = PdfCutter(pdf_routine, dir_name)
    cutter.cut_pdf()
    asker = PdfClaudeAsker()
    all_json_list = []  #准备一个空列表，这个列表将装载所有的单条银行流水dict
    asyncio.run(asker.pdf_main(cutter.pdfs))
    for raw_json_file_routine in asker.out_jsons:
        dealed_json_list = JsonToExcelRowValue.wash_raw_json(raw_json_file_routine)
        all_json_list.extend(dealed_json_list)
    bank_statement_sample = all_json_list[0]
    json_dealer = JsonToExcelRowValue(bank_statement_sample)
    for bank_statement in all_json_list:
        json_dealer.deal_single_json(bank_statement)
    headers = json_dealer.headers
    save_routine = Config().get("paths.excel_dir") + Config().get("excel.default_filename")
    data = json_dealer.operate_lists
    excel_data = DataToExcel(data=data, save_routine=save_routine, headers=headers)
    done, do_info = excel_data.save_xl()
    print(do_info)

if __name__ == "__main__":
    pdf_routine = "bank.pdf"
    main(pdf_routine)
