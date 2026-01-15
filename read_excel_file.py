import pandas as pd
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read the Excel file (try different engines)
try:
    xl = pd.ExcelFile(r'C:\Users\irfan\Downloads\weekly_stocks_all_2025-12-08.xls', engine='xlrd')
except:
    try:
        xl = pd.ExcelFile(r'C:\Users\irfan\Downloads\weekly_stocks_all_2025-12-08.xls', engine='openpyxl')
    except:
        print("Trying to read as .xls with different name...")
        # Maybe it's actually .xlsx despite the extension
        import openpyxl
        xl = pd.ExcelFile(r'C:\Users\irfan\Downloads\weekly_stocks_all_2025-12-08.xls', engine='openpyxl')

print(f"Sheet names: {xl.sheet_names}\n")

# Read Structure sheet
print("=" * 80)
print("STRUCTURE TAB")
print("=" * 80)
df_structure = pd.read_excel(xl, sheet_name='Structure')
print(df_structure.to_string())

print("\n\n")
print("=" * 80)
print("DATA TAB (First 10 rows)")
print("=" * 80)
# Read Data sheet
df_data = pd.read_excel(xl, sheet_name='Data', nrows=10)
print("\nColumn order in Data tab:")
for i, col in enumerate(df_data.columns, 1):
    print(f"{i}. {col}")

print("\n\nFirst 3 rows of data:")
print(df_data.head(3).to_string())
