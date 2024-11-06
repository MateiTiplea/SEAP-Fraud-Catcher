import pandas as pd
import tabula


def extract_unique_strings_from_pdf(pdf_path, column_index=0):
    # Read the PDF file and extract tables into a list of DataFrames
    tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)

    unique_strings = set()

    # Iterate through each DataFrame (table)
    for table in tables:
        if len(table.columns) <= column_index:
            continue

        if len(table) > 0:
            column = table.iloc[:, column_index]
            for cell in column:
                if pd.notnull(cell):
                    # the cell may contain multiple strings separated by newlines
                    # combine the lines into a single string separated by spaces
                    cell = " ".join(cell.splitlines())
                    unique_strings.add(cell)

    return unique_strings


# Path to the PDF file
pdf_path = "Reclasificare-coduri-CPV.PDF"
column_index = 3  # 4th column (0-based index)

# Extract unique strings from the specified column
unique_strings = extract_unique_strings_from_pdf(pdf_path, column_index)

with open("unique_strings.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(unique_strings))
