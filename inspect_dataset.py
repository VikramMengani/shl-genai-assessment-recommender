import pandas as pd

# Load Excel file
df = pd.read_excel("Gen_AI Dataset.xlsx")
df = df.dropna()
df = df[df["Query"].str.len() > 10]

# Show first 5 rows
print("\nFirst 5 rows:\n")
print(df.head())

# Show column names
print("\nColumns:\n")
print(df.columns)

# Show total rows
print("\nTotal Rows:", len(df))