import pandas as pd

# Load Excel file
xls = pd.ExcelFile("Gen_AI Dataset.xlsx")

print("Sheet names:")
print(xls.sheet_names)

print("\n--- First 20 rows of first sheet ---\n")

df = pd.read_excel("Gen_AI Dataset.xlsx")
print(df.head(20))

print("\nColumns:")
print(df.columns)