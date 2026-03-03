# BankFlow

基于 Claude API 的招商银行流水 PDF 自动识别工具。将招商银行流水 PDF 文件通过 AI 识别提取交易数据，并输出为结构化的 Excel 表格，适配貔貅记账等记账软件导入格式。

## 功能特点

- **PDF 智能识别**：调用 Claude API 的 Files API，自动识别招商银行流水 PDF 中的交易信息
- **JSON Schema 约束输出**：通过 JSON Schema 确保 AI 返回结构化、规范的交易数据
- **异步并发处理**：使用 `asyncio` + `aiohttp` 异步并发上传和请求，高效处理多页 PDF
- **自动数据映射**：将银行原始字段（记账日期、交易金额等）自动映射为记账软件所需格式（交易日期、收支类型、金额等）
- **失败自动重试**：API 请求支持指数退避重试机制

## 项目结构

```
accounting/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖列表
├── configs/
│   ├── config.py           # 配置管理类（单例模式）
│   ├── config.example.json # 配置文件模板（复制为 config.json 后填入自己的 API Key）
│   └── schema.json         # Claude 输出的 JSON Schema 定义
└── utils/
    ├── PdfDealer.py        # PDF 分割：将多页 PDF 拆分为单页
    ├── PdfAsker.py         # Claude API 交互：上传 PDF 并获取识别结果
    ├── JsonDealer.py       # JSON 数据处理：清洗并映射为 Excel 行数据
    └── ExcelDealer.py      # Excel 生成：将处理后的数据写入 xlsx 文件
```

## 处理流程

```
银行流水 PDF → 按页拆分 → 上传至 Claude API → AI 识别返回 JSON → 数据清洗与映射 → 输出 Excel
```

## 安装与使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

复制配置模板并填入你的 API Key：

```bash
cp configs/config.example.json configs/config.json
```

然后编辑 `configs/config.json`，填入你的 API 信息：

| 字段 | 说明 |
|------|------|
| `models.claude.base_url` | Claude API 地址，默认为 Anthropic 官方地址 |
| `models.claude.api_key` | 你的 Claude API Key |
| `paths.pdf_dir` | PDF 分页文件的存放目录 |
| `paths.excel_dir` | 生成的 Excel 文件的存放目录 |
| `excel.default_filename` | 输出的 Excel 文件名 |

### 3. 运行

将招商银行流水 PDF 文件重命名为 `bank.pdf` 并放置在项目根目录下，然后运行：

```bash
python main.py
```

生成的 Excel 文件将保存到 `excels/` 目录下。

## Excel 输出字段

| 原始字段 | 映射字段 | 说明 |
|---------|---------|------|
| 记账日期 | 交易日期 | 日期格式转换为 `yyyy/mm/dd` |
| 交易金额 | 金额 / 收支类型 | 正数为收入，负数为支出，金额取绝对值 |
| 联机余额 | — | 保留原始值 |
| 交易摘要 | — | 保留原始值 |
| 对手信息 | 备注 | 同时映射到备注字段 |

## 依赖

- **pypdf** — PDF 读取与分割
- **aiohttp** — 异步 HTTP 请求
- **openpyxl** — Excel 文件生成
