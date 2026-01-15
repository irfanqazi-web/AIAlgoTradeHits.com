import sys
import io
import xlrd

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'C:\Users\irfan\Downloads\weekly_stocks_all_2025-12-08.xls'

print("=" * 100)
print("ANALYZING EXCEL FILE: weekly_stocks_all_2025-12-08.xls")
print("=" * 100)

try:
    # Open workbook
    wb = xlrd.open_workbook(file_path)

    print(f"\nSheet names found: {wb.sheet_names()}\n")

    # Analyze Structure sheet
    if 'Structure' in wb.sheet_names():
        ws_structure = wb.sheet_by_name('Structure')
        print("\n" + "=" * 100)
        print("STRUCTURE TAB (Schema Definition)")
        print("=" * 100)
        print(f"Total rows in Structure: {ws_structure.nrows}")
        print(f"Total columns in Structure: {ws_structure.ncols}\n")

        print("Field definitions (in order as defined in Structure tab):")
        print("-" * 100)
        structure_fields = []

        # Read structure (skip header row)
        for row_idx in range(1, min(ws_structure.nrows, 100)):
            row = ws_structure.row_values(row_idx)
            if row[1]:  # If Field Name exists
                field_num = int(row[0]) if row[0] else row_idx
                field_name = str(row[1]).strip()
                field_type = str(row[2]) if len(row) > 2 else ""
                field_mode = str(row[3]) if len(row) > 3 else ""

                structure_fields.append(field_name)
                print(f"{field_num:3}. {field_name:40} | Type: {field_type:10} | Mode: {field_mode}")

    # Analyze Data sheet
    if 'Data' in wb.sheet_names():
        ws_data = wb.sheet_by_name('Data')
        print("\n" + "=" * 100)
        print("DATA TAB (Actual Data)")
        print("=" * 100)
        print(f"Total rows in Data: {ws_data.nrows}")
        print(f"Total columns in Data: {ws_data.ncols}\n")

        # Get header row
        data_fields = []
        if ws_data.nrows > 0:
            header_row = ws_data.row_values(0)

            print("Column order in Data tab:")
            print("-" * 100)
            for i, col_name in enumerate(header_row, 1):
                if col_name:
                    col_name_str = str(col_name).strip()
                    data_fields.append(col_name_str)
                    print(f"{i:3}. {col_name_str}")

        # Compare Structure vs Data order
        print("\n" + "=" * 100)
        print("COMPARISON: Structure Tab vs Data Tab")
        print("=" * 100)

        print(f"\nTotal fields in Structure: {len(structure_fields)}")
        print(f"Total fields in Data:      {len(data_fields)}")

        if structure_fields == data_fields:
            print("\n✅ MATCH: Field order is IDENTICAL in both tabs")
        else:
            print("\n❌ MISMATCH: Field order is DIFFERENT between tabs\n")

            # Find differences
            print("Detailed comparison:")
            print("-" * 100)
            print(f"{'#':4} | {'Match':5} | {'Structure Tab':50} | {'Data Tab':50}")
            print("-" * 100)

            max_len = max(len(structure_fields), len(data_fields))

            for i in range(max_len):
                struct_field = structure_fields[i] if i < len(structure_fields) else "MISSING"
                data_field = data_fields[i] if i < len(data_fields) else "MISSING"

                match = "✓" if struct_field == data_field else "✗"

                print(f"{i+1:3}. | {match:^5} | {struct_field:50} | {data_field:50}")

            # Fields in Structure but not in Data
            missing_in_data = set(structure_fields) - set(data_fields)
            if missing_in_data:
                print(f"\n⚠️ Fields in Structure but NOT in Data ({len(missing_in_data)} fields):")
                for field in missing_in_data:
                    print(f"   - {field}")

            # Fields in Data but not in Structure
            extra_in_data = set(data_fields) - set(structure_fields)
            if extra_in_data:
                print(f"\n⚠️ Fields in Data but NOT in Structure ({len(extra_in_data)} fields):")
                for field in extra_in_data:
                    print(f"   - {field}")

        # Show sample data
        print("\n" + "=" * 100)
        print("SAMPLE DATA (First 3 rows)")
        print("=" * 100)
        for row_idx in range(1, min(4, ws_data.nrows)):
            row = ws_data.row_values(row_idx)
            print(f"\nRow {row_idx}:")
            for j, (col_name, value) in enumerate(zip(data_fields, row)):
                if j < 10:  # Show first 10 columns only
                    print(f"  {col_name}: {value}")

except Exception as e:
    print(f"\n❌ Error reading file: {e}")
    import traceback
    traceback.print_exc()
