import pandas as pd; xl = pd.ExcelFile("agents/mali-report.xlsx"); print("Sheet names:", xl.sheet_names); [print(f"
=== {sheet} ===
", pd.read_excel("agents/mali-report.xlsx", sheet_name=sheet).columns.tolist()) for sheet in xl.sheet_names]
