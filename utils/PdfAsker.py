import asyncio
from pathlib import Path
import aiohttp

from configs import Config

class PdfClaudeAsker:
   def __init__(self) -> None:
      self.schema = Config().schema
      self.api_key = Config().get("models.claude.api_key")
      self.base_url = Config().get("models.claude.base_url", "https://api.anthropic.com")
      self.pdf_files_json_list = []
      self.out_jsons = []
   
   def _build_files_api_header(self):
      print("正在构建文件请求头！")
      return {
         "x-api-key": self.api_key,
         "anthropic-version": "2023-06-01",
         "anthropic-beta": "files-api-2025-04-14",
      }
   
   def _build_files_message_api_header(self, file_name):
      print(f"正在构建文件{file_name}的消息请求头！")
      return {
         "content-type": "application/json",
         "x-api-key": self.api_key,
         "anthropic-version": "2023-06-01",
         "anthropic-beta": "files-api-2025-04-14"
      }
   
   def _build_files_message_api_data(self, file_id, file_name):
      print(f"正在构建文件{file_name}消息请求体！")
      content = [
         {
            "type": "document",
            "source": {
               "type": "file",
               "file_id": file_id
            }
         },
         {
            "type": "text",
            "text": "请你识别PDF中的信息，并根据要求输出为JSON格式。"
         }
      ]
      messages = [
         {
            "role": "user",
            "content": content
         }
      ]
      output_config = {
         "format": {
            "type": "json_schema",
            "schema": self.schema
         }
      }
      # ✅ 修正：使用正确的模型名称
      return {
         "model": "claude-sonnet-4-5",  # 或其他有效的模型名，如 "claude-3-5-haiku-latest"
         "max_tokens": 20480,
         "messages": messages,
         "output_config": output_config
      }

   async def _upload_pdf_to_claude(self, session: aiohttp.ClientSession, pdf_routine: str, semaphore: asyncio.Semaphore, max_retries: int = 3):
      """
      上传PDF文件到Claude API，返回文件ID。PDF文件名和文件ID会被存储在类实例的pdf_files_json_list属性中。

      Args:
         session: 复用的aiohttp ClientSession
         pdf_routine: PDF文件路径
         semaphore: 并发控制信号量
         max_retries: 最大重试次数
      """
      async with semaphore:  # 控制并发数量
         headers = self._build_files_api_header()
         url = f"{self.base_url}/v1/files"

         for attempt in range(max_retries):
            try:
               data = aiohttp.FormData()
               with open(pdf_routine, "rb") as file:
                  data.add_field('file',
                        file,
                        filename=Path(pdf_routine).name,
                        content_type='application/pdf')

                  print(f"正在上传文件: {Path(pdf_routine).name} (尝试 {attempt + 1}/{max_retries})")
                  async with session.post(url, headers=headers, data=data) as response:
                     response.raise_for_status()
                     file_response_json = await response.json()
                     self.pdf_files_json_list.append({
                        "pdf_file_name": pdf_routine,
                        "file_id": file_response_json["id"]
                     })
                  print(f"上传文件成功: {Path(pdf_routine).name}")
                  return  # 成功后返回

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
               if attempt < max_retries - 1:
                  wait_time = 2 ** attempt  # 指数退避
                  print(f"上传失败，{wait_time}秒后重试: {Path(pdf_routine).name}, 错误: {str(e)}")
                  await asyncio.sleep(wait_time)
               else:
                  print(f"上传失败，已达最大重试次数: {Path(pdf_routine).name}")
                  raise

   async def _get_pdf_reply(self, session: aiohttp.ClientSession, pdf_file_name=None, file_id=None, semaphore: asyncio.Semaphore = None, max_retries: int = 3):
      """
      获取PDF解析回复

      Args:
         session: 复用的aiohttp ClientSession
         pdf_file_name: PDF文件名
         file_id: 上传后的文件ID
         semaphore: 并发控制信号量
         max_retries: 最大重试次数
      """
      url = f"{self.base_url}/v1/messages"
      headers = self._build_files_message_api_header(Path(pdf_file_name).name)
      data = self._build_files_message_api_data(file_id=file_id, file_name=Path(pdf_file_name).name)

      async with semaphore if semaphore else asyncio.Semaphore(1):
         for attempt in range(max_retries):
            try:
               print(f"正在请求回复: {Path(pdf_file_name).name} (尝试 {attempt + 1}/{max_retries})")
               async with session.post(url=url, headers=headers, json=data) as response:
                  # 在错误时打印响应内容
                  if response.status != 200:
                     error_text = await response.text()
                     print(f"Error response: {error_text}")
                  response.raise_for_status()
                  pdf_message_response_json = await response.json()

                  for item in pdf_message_response_json["content"]:
                     if item["type"] == "text":
                        pdf_json_data = item["text"]
                        json_file_name = Path(pdf_file_name).stem
                        Path("outJsons").mkdir(parents=True, exist_ok=True)
                        with open(f"outJsons/{json_file_name}.json", "w") as f:
                           f.write(pdf_json_data)
                           self.out_jsons.append(f"outJsons/{json_file_name}.json")
                     else:
                        raise Exception(f"PDF文件{pdf_file_name}解析失败，错误信息：{item}")

                  print(f"回复成功: {Path(pdf_file_name).name}")
                  return  # 成功后返回

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
               if attempt < max_retries - 1:
                  wait_time = 2 ** attempt
                  print(f"请求回复失败，{wait_time}秒后重试: {Path(pdf_file_name).name}, 错误: {str(e)}")
                  await asyncio.sleep(wait_time)
               else:
                  print(f"请求回复失败，已达最大重试次数: {Path(pdf_file_name).name}")
                  raise

   async def pdf_main(self, pdfs_files: list, max_concurrent_uploads: int = 10, max_concurrent_replies: int = 10):
      """
      主要的PDF处理流程

      Args:
         pdfs_files: PDF文件路径列表
         max_concurrent_uploads: 最大并发上传数量（默认10）
         max_concurrent_replies: 最大并发请求回复数量（默认10）
      """
      # 创建超时配置
      timeout = aiohttp.ClientTimeout(total=600, connect=60, sock_read=120)

      # 创建TCP连接器，配置连接池
      connector = aiohttp.TCPConnector(
         limit=10,  # 总连接数限制
         limit_per_host=5,  # 每个主机的连接数限制
         ttl_dns_cache=300  # DNS缓存时间
      )

      # 使用同一个session处理所有请求
      async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
         # 上传阶段
         upload_tasks = []
         upload_semaphore = asyncio.Semaphore(max_concurrent_uploads)

         print(f"准备上传任务池！文件总数: {len(pdfs_files)}, 最大并发数: {max_concurrent_uploads}")
         for pdf_file in pdfs_files:
            upload_tasks.append(self._upload_pdf_to_claude(session, pdf_file, upload_semaphore))

         print("上传任务池准备完毕，开始进行并发执行阶段！")
         await asyncio.gather(*upload_tasks, return_exceptions=False)
         print(f"上传任务池并发执行完毕！成功上传 {len(self.pdf_files_json_list)} 个文件")

         # 回复阶段
         reply_tasks = []
         reply_semaphore = asyncio.Semaphore(max_concurrent_replies)

         print("准备回复任务池！")
         for item in self.pdf_files_json_list:
            reply_tasks.append(self._get_pdf_reply(session, semaphore=reply_semaphore, **item))

         print(f"回复任务池准备完毕，开始进入并发执行阶段！最大并发数: {max_concurrent_replies}")
         await asyncio.gather(*reply_tasks, return_exceptions=False)
         print("回复任务池并发执行完毕！")

