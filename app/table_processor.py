import mammoth
import re
from bs4 import BeautifulSoup

from app.exceptions import TableDataError, TriloDocsError


class TableProcessor:

    pattern_table_number = re.compile(r'\d+(?:\.\d+)+')
    pattern_sae_short = re.compile(rf'\b{"sae"}\b', re.IGNORECASE)
    pattern_sae_full = re.compile(rf'\b{"serious adverse events"}\b',
                                  re.IGNORECASE)

    def __init__(self, file_path):
        self.file_path = file_path

    def process_tables(self):
        try:
            all_extracted_tables = self._extract_tables_from_docx()
            target_tables = self._check_target_tables(all_extracted_tables)
            if not target_tables:
                result = {
                    "table_number": None,
                    "table_title": None,
                    "summary": ["No serious adverse events were reported."]
                }
                return result
            results = self._compute_table_data(target_tables)
        except TriloDocsError as e:
            results = {
                "status": "error",
                "details": e.args[0]
            }

        return results

    def _extract_tables_from_docx(self):
        # Convert .docx to HTML
        with open(self.file_path, "rb") as docx_file:
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
            match = self.pattern_table_number.search(raw_title)
            if match:
                table_number = (match.group())
                title = raw_title[match.regs[0][1]:].strip()
            else:
                table_number = None
                title = None

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

    def _check_target_tables(self, tables_list):
        target_tables = []
        for table in tables_list:
            table_title = table["title"]
            found_short = bool(self.pattern_sae_short.search(table_title))
            found_full = bool(self.pattern_sae_full.search(table_title))

            if any((found_short, found_full)):
                target_tables.append(table)

        return target_tables

    def _compute_table_data(self, target_tables):
        results = []
        for table in target_tables:
            participants_total = self._compute_participants_total_number(table)
            report_data = self._process_data_in_table(table)
            summary = [
                f"There were {participants_total} total serious adverse events "
                f"reported."
            ]
            summary.extend(report_data)

            results.append(
                {
                    "table_number": table["table_number"],
                    "table_title": table["title"],
                    "summary": summary
                }
            )
        return results

    @staticmethod
    def _compute_participants_total_number(table):
        last_row = table["data"][-1]
        try:
            total_number = int(last_row[1]) + int(last_row[2])
        except ValueError:
            raise TableDataError()
        return total_number

    @staticmethod
    def _process_data_in_table(table):
        results = []

        for idx, row in enumerate(table["data"]):

            # loop_stop_condition
            if idx == len(table["data"]) - 1:
                break

            try:
                part_1 = int(row[1])
                whole_1 = int(table["data"][-1][1])
                percent_1 = (part_1 / whole_1) * 100
                symptom_1 = (f"{percent_1:.2f}% of {table['columns'][1]} "
                             f"participants experienced {row[0].lower()}.")

                part_2 = int(row[2])
                whole_2 = int(table["data"][-1][2])
                percent_2 = (part_2 / whole_2) * 100
                symptom_2 = (f"{percent_2:.2f}% of {table['columns'][2]} "
                             f"participants experienced {row[0].lower()}.")
            except ValueError:
                raise TableDataError()

            results.append(symptom_1)
            results.append(symptom_2)

        return results
