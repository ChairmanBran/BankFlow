from typing import Any

import json



class JsonToExcelRowValue:
   def __init__(self, bank_statement_sample: dict[str, Any]) -> None:
      self.headers = []
      self.headers_dict = {}
      self._build_new_headers(bank_statement_sample=bank_statement_sample)
      self.operate_lists = []

   def _build_new_headers(self, bank_statement_sample: dict[str, Any]):
      """
      建立新excel表的表头；
      """
      for key in bank_statement_sample:
         self.headers.append(key)
      self.headers.extend(
         ["交易日期", "收支类型", "收支项目", "金额", "账户名称", "标签", "备注"]
      )
      for index, key_value in enumerate(self.headers):
         self.headers_dict[key_value] = index + 1
   
   def deal_single_json(self, bank_statement: dict[str, Any]) -> list:
      """
      Args:
         bank_statement：银行流水的单条dict
      Returns:
         operate_list：存在先后顺序的、对应表头的单row数据
         self.operate_lists：每一个row的值将作为一项存入总列表；
      """
      headers_length = len(self.headers)
      operate_list = ["" for _ in range(headers_length)]
      for key, value in bank_statement.items():
         if key == "记账日期":
            value = value.replace("-", "/")  #将2025-11-20的日期字符串转换为2025/11/20的格式；
            operate_list_index = self.headers_dict["交易日期"] - 1  #匹配该字段所在列索引值；
            operate_list[operate_list_index] = value
         elif key == "交易金额":
            value = float(value.replace(",", ""))  #处理数字字符串中的逗号分隔，并转换为浮点数；
            operate_list_index = self.headers_dict["金额"] - 1  #匹配该字段所在列索引值；
            operate_list[operate_list_index] = abs(value)  #貔貅记账金额字段为绝对值；
            if value > 0:  #如为正数，收支类型为收入；
               operate_list_index = self.headers_dict["收支类型"] - 1
               operate_list[operate_list_index] = "收入"
            else:  #如为负数，收支类型为支出；
               operate_list_index = self.headers_dict["收支类型"] - 1
               operate_list[operate_list_index] = "支出"
         elif key == "联机余额":
            value = float(value.replace(",", ""))  #处理数字字符串中的逗号分隔，并转换为浮点数；
         elif key == "对手信息":
            operate_list_index = self.headers_dict["备注"] - 1
            operate_list[operate_list_index] = value
         #上方根据字段对值做特殊处理，处理完毕以后，下方正常将值赋予原始字段；
         operate_list_index = self.headers_dict[key] - 1  #寻找当前字段的列索引值；
         operate_list[operate_list_index] = value  #根据列索引值将value填充到新加行的对应位置；
      self.operate_lists.append(operate_list)
      return operate_list

   @staticmethod
   def wash_raw_json(raw_json_file_routine) -> list:
      """
      输入json文件路径，输出处理后的包含多个字典的列表。
      Args:
         raw_json_file_routine: 单页银行流水PDF所转换的json文件的路径
      Returns:
         dealed_json_list：返回一个列表，这个列表中的每一项为单条银行流水的字典
      """
      with open(raw_json_file_routine, "r", encoding="utf-8") as f:
         raw_json = json.load(f)
      try:
         dealed_json_list = raw_json["Data"]
         return dealed_json_list
      except Exception as e:
         print(f"错误：{e}")
         raise Exception(f"发生错误：{e}") from e
