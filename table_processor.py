import mammoth
import re
from bs4 import BeautifulSoup


def extract_tables_from_docx(docx_path):
    pattern = re.compile(r'\d+(?:\.\d+)+')
    # Convert .docx to HTML
    with open(docx_path, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file)
        html = result.value  # the HTML content

    # Parse the HTML
    soup = BeautifulSoup(html, "lxml")

    # Collect tables info
    tables_info = []
    for table in soup.find_all("table"):

        # Determine table title: first look for <h1>, then for title in <p>
        title_tag = table.find_previous("h1")
        if title_tag:
            raw_title = title_tag.get_text(strip=True)
        else:
            raw_title = None
            prev_p = table.find_previous_sibling("p")
            if prev_p:
                txt = prev_p.get_text(strip=True)
                if txt.lower().startswith("table"):
                    raw_title = txt
            if not raw_title:
                # fallback title if none is found
                raw_title = f"Table at position {len(tables_info) + 1}"

        # Determine table number
        match = pattern.search(raw_title)
        if match:
            table_number = (match.group())
            title = raw_title[match.regs[0][1]:].strip()
        else:
            table_number = None

        # Parse the table rows
        rows = table.find_all("tr")
        if not rows:
            continue

        # Get column names from the first row
        header_cells = rows[0].find_all(["th", "td"])
        columns = [cell.get_text(strip=True) for cell in header_cells]

        # Data from all subsequent rows
        data = []
        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            row_data = [cell.get_text(strip=True) for cell in cells]
            data.append(row_data)

        tables_info.append(
            {
                "table_number": table_number,
                "title": title,
                "columns": columns,
                "data": data
            }
        )

    return tables_info


def check_target_tables(tables_list):
    target_tables = []
    pattern_short = re.compile(rf'\b{"sae"}\b', re.IGNORECASE)
    pattern_full = re.compile(rf'\b{"serious adverse events"}\b', re.IGNORECASE)
    for table in tables_list:
        table_title = table["title"]
        found_short = bool(pattern_short.search(table_title))
        found_full = bool(pattern_full.search(table_title))

        if any((found_short, found_full)):
            target_tables.append(table)

    return target_tables


def compute_participants_total_number(table):
    a=1
    last_row = table["data"][-1]
    try:
        total_number = int(last_row[1]) + int(last_row[2])
    except ValueError:
        print("\nDATA ERROR!!!!!!!!!!!!!!!!!!!\n") # ADD OWN EXCEPTION LATER
    return total_number


def compute_problems(table, participants_total):
    a=1
    results = []

    for idx, row in enumerate(table["data"]):

        # stop_mark
        if idx == len(table["data"]) - 1:
            break

        part_1 = int(row[1])  # ADD TRY EXCEPT FOR INT
        whole_1 = int(table["data"][-1][1])
        percent_1 = (part_1 / whole_1) * 100
        problem_1 = f"{percent_1:.2f}% of {table['columns'][1]} participants experienced {row[0].lower()}."

        part_2 = int(row[2])
        whole_2 = int(table["data"][-1][2])
        percent_2 = (part_2 / whole_2) * 100
        problem_2 = f"{percent_2:.2f}% of {table['columns'][2]} participants experienced {row[0].lower()}."

        results.append(problem_1)
        results.append(problem_2)

    return results





def compute_table_data(target_tables):
    results = []
    for table in target_tables:
        paricipants_total = compute_participants_total_number(table)
        report_data = compute_problems(table, paricipants_total)
        summary = [f"There were {paricipants_total} total serious adverse events reported."]
        summary.extend(report_data)


        results.append(
            {
                "table_number": table["table_number"],
                "table_title": table["title"],
                "summary": summary
            }
        )
    return results


if __name__ == "__main__":
    all_tables = extract_tables_from_docx("client1_ae.docx")
    target_tables = check_target_tables(all_tables)
    if not target_tables:
        print("No serious adverse events were reported.") # PAY ATTENTION LATER
    results = compute_table_data(target_tables)
    a=1
