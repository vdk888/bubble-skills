#!/usr/bin/env python3
"""List the clients due for their annual review, from the firm's client file (CSV or XLSX).

Usage:
  due_reviews.py --fichier <clients.csv|clients.xlsx> [--mois AAAA-MM] [--delai-mois 12]
                 [--colonne-client "Référence"] [--colonne-date "Dernière revue"]
                 [--feuille <nom>] [--aujourdhui AAAA-MM-JJ]

Rule: a review is due when the last review date + N months (default 12) falls in
the month examined (default: the current month). Due in an earlier month = late.
A missing, unreadable, two-digit-year or future date, or a number that gives a
date before 1990, goes to « À vérifier », with the value read. Prints, in French Markdown, the rule, the table of listed clients
and the lists; prints a count on stderr. Reads only the two configured columns.
Exit 0 = ok, 2 = usage/IO error, 3 = column not found or file not readable as a table.
Standard library only (XLSX read with zipfile + xml), no network. XLSX parts are
read with a size cap and refused if not UTF-8 or if they declare a DOCTYPE
(zip / entity bombs).
"""
import calendar
import csv
import datetime as dt
import io
import os
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "p": "http://schemas.openxmlformats.org/package/2006/relationships"}
PART_CAP = 50 * 1024 * 1024    # uncompressed bytes per XLSX part read
TOTAL_CAP = 100 * 1024 * 1024  # uncompressed bytes for all parts read
XML_DECL_ENCODING = re.compile(rb"(?:\xef\xbb\xbf)?\s*<\?xml[^>]*?encoding\s*=\s*[\"']([^\"']*)")
FIRST_YEAR = 1990              # an Excel number giving an earlier date is not taken as a date


class TableError(Exception):
    pass


def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def plural(n, one, many):
    return f"{n} {one if n <= 1 else many}"


# ---------- reading the file ----------

def read_csv(path):
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    first = text.splitlines()[0] if text.strip() else ""
    delim = max(";,\t", key=first.count) if first else ";"
    rows = list(csv.reader(io.StringIO(text), delimiter=delim))
    return [[("text", c) for c in r] for r in rows]


def col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for c in letters:
        n = n * 26 + ord(c) - 64
    return n - 1


class PartReader:
    """Reads XLSX parts with a cap on uncompressed size (per part and in total)."""

    def __init__(self, z):
        self.z, self.total = z, 0

    def xml(self, name):
        with self.z.open(name) as f:
            data = f.read(PART_CAP + 1)
        self.total += len(data)
        if len(data) > PART_CAP or self.total > TOTAL_CAP:
            raise TableError(f"XLSX part {name} too large once uncompressed (cap {PART_CAP // 2**20} MB per part, "
                             f"{TOTAL_CAP // 2**20} MB in total): not read, export the sheet as CSV")
        # Excel writes UTF-8: refuse anything else first, so the DOCTYPE byte check cannot be dodged by
        # another encoding (UTF-16/32 has a BOM or NUL bytes; any other one is named in the XML declaration).
        decl = XML_DECL_ENCODING.match(data)
        if (data.startswith((b"\xff\xfe", b"\xfe\xff")) or b"\x00" in data
                or (decl and decl.group(1).lower() not in (b"utf-8", b"utf8"))):
            raise TableError(f"XLSX part {name} is not UTF-8 (not a normal Excel file): not read")
        if b"<!DOCTYPE" in data:
            raise TableError(f"XLSX part {name} declares a DOCTYPE (not a normal Excel file): not read")
        return ET.fromstring(data)


def read_xlsx(path, sheet=None):
    try:
        z = zipfile.ZipFile(path)
        parts = PartReader(z)
        wb = parts.xml("xl/workbook.xml")
        rels = parts.xml("xl/_rels/workbook.xml.rels")
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as e:
        raise TableError(f"not a readable XLSX file ({e})")
    pr = wb.find("m:workbookPr", NS)
    date1904 = pr is not None and pr.get("date1904") in ("1", "true")
    sheets = wb.findall("m:sheets/m:sheet", NS)
    if not sheets:
        raise TableError("no sheet in the workbook")
    if sheet is None:
        target = sheets[0]
    else:
        target = next((s for s in sheets if s.get("name") == sheet), None)
        if target is None:
            raise TableError(f"no sheet named '{sheet}' (sheets: {', '.join(s.get('name') for s in sheets)})")
    rid = target.get(f"{{{NS['r']}}}id")
    href = next((r.get("Target") for r in rels.findall("p:Relationship", NS) if r.get("Id") == rid), None)
    if href is None:
        raise TableError("sheet target not found")
    href = href.lstrip("/") if href.startswith("/") else "xl/" + href
    shared = []
    try:
        if "xl/sharedStrings.xml" in z.namelist():
            for si in parts.xml("xl/sharedStrings.xml").findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
        ws = parts.xml(href)
    except (KeyError, ET.ParseError, zipfile.BadZipFile) as e:
        raise TableError(f"sheet not readable ({e})")
    rows = []
    for row in ws.iter(f"{{{NS['m']}}}row"):
        cells = {}
        for i, c in enumerate(row.findall("m:c", NS)):
            idx = col_index(c.get("r")) if c.get("r") else i
            t, v = c.get("t", "n"), c.find("m:v", NS)
            if t == "s" and v is not None:
                cells[idx] = ("text", shared[int(v.text)])
            elif t == "inlineStr":
                cells[idx] = ("text", "".join(x.text or "" for x in c.iter(f"{{{NS['m']}}}t")))
            elif t == "n" and v is not None and v.text:
                cells[idx] = ("number", v.text)
            elif v is not None:
                cells[idx] = ("text", v.text or "")
        width = max(cells) + 1 if cells else 0
        rows.append([cells.get(i, ("text", "")) for i in range(width)])
    return rows, date1904


# ---------- dates ----------

def add_months(d, n):
    y, m = divmod(d.month - 1 + n, 12)
    y, m = d.year + y, m + 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def parse_date(kind, value, date1904):
    """Return (date or None, shown value, reason if not readable)."""
    value = value.strip()
    if kind == "number":
        shown = value
        try:
            serial = float(value)
        except ValueError:
            return None, shown, "date illisible"
        if not 1 <= serial < 2958466:
            return None, shown, "date illisible"
        base = dt.date(1904, 1, 1) if date1904 else dt.date(1899, 12, 30)
        d = base + dt.timedelta(days=int(serial))
        if d.year < FIRST_YEAR:
            return None, shown, f"nombre qui ne donne pas une date plausible (avant {FIRST_YEAR})"
        return d, f"{d.strftime('%d/%m/%Y')} (date Excel {value})", None
    if not value:
        return None, "", "date manquante"
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?", value)
    if m:
        y, mo, d = map(int, m.groups())
    else:
        m = re.fullmatch(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{2}|\d{4})(?: \d{1,2}:\d{2}(?::\d{2})?)?", value)
        if not m:
            return None, value, "date illisible"
        d, mo, y = int(m.group(1)), int(m.group(2)), m.group(3)
        if len(y) == 2:
            return None, value, "année sur deux chiffres"
        y = int(y)
    try:
        return dt.date(y, mo, d), value, None
    except ValueError:
        return None, value, "date illisible"


# ---------- rule ----------

def find_column(header, wanted, label):
    keys = [norm(h) for _, h in header]
    if norm(wanted) in keys:
        return keys.index(norm(wanted))
    names = ", ".join(f"« {h} »" for _, h in header if h.strip()) or "aucune"
    raise TableError(f"{label} column « {wanted} » not found (columns: {names})")


def classify(rows, col_client, col_date, month, delay, today, date1904):
    if not rows:
        raise TableError("empty file")
    header = rows[0]
    ci = find_column(header, col_client, "client")
    di = find_column(header, col_date, "date")
    start = dt.date(month[0], month[1], 1)
    out, refs = [], {}
    for n, row in enumerate(rows[1:], 2):
        get = lambda i: row[i] if i < len(row) else ("text", "")
        if all(not v.strip() for _, v in row):
            continue
        kind, ref = get(ci)
        ref = ref.strip()
        if kind == "number" and re.fullmatch(r"\d+\.0", ref):
            ref = ref[:-2]
        d, shown, reason = parse_date(*get(di), date1904)
        due = add_months(d, delay) if d else None
        if d and d > today:
            reason = "date postérieure à aujourd'hui"
        if reason:
            status = "check"
        elif (due.year, due.month) == month:
            status = "due"
        elif due < start:
            status = "late"
        else:
            status = "later"
        out.append({"line": n, "ref": ref, "shown": shown, "date": d, "due": due,
                    "status": status, "reason": reason})
        refs.setdefault(ref, []).append(out[-1])
    for ref, recs in refs.items():
        for r in recs:
            if not ref:
                r["status"], r["reason"] = "check", "référence client vide"
            elif len(recs) > 1:
                r["status"], r["reason"] = "check", "référence présente sur plusieurs lignes"
    return out


# ---------- output ----------



def label(r):
    return r["ref"] if r["ref"] and r["reason"] != "référence présente sur plusieurs lignes" \
        else (f"{r['ref']} (ligne {r['line']})" if r["ref"] else f"ligne {r['line']} (référence vide)")


def cell(s):
    return s.replace("|", "\\|")


def shown(r):
    return f"« {r['shown']} »" if r["shown"] else "(vide)"


def bullet(r, delay):
    s = f"- **{label(r)}** — date lue {shown(r)}"
    if r["date"]:
        s += f", comprise comme le {r['date'].isoformat()}"
    if r["status"] in ("due", "late"):
        s += f" ; échéance {r['due'].isoformat()} (dernière revue + {delay} mois)"
    else:
        s += f" ; {r['reason']}"
    return s


def render(recs, path, col_client, col_date, month, delay, sheet):
    mname = f"{MOIS[month[1] - 1]} {month[0]}"
    src = os.path.basename(path) + (f", feuille « {sheet} »" if sheet else "")
    out = ["## Règle appliquée", "",
           f"Une revue est due quand la date de la dernière revue + {delay} mois tombe dans le mois examiné. "
           f"Mois examiné : {mname} ({month[0]}-{month[1]:02d}). "
           f"Fichier : {src} ; colonnes lues : « {col_client} » (client) et « {col_date} » (dernière revue). "
           "Les autres colonnes ne sont pas lues.", "",
           "## Clients retenus", "",
           "| Client | Date lue | Date comprise | Échéance | Liste |",
           "|--------|----------|---------------|----------|-------|"]
    status_label = {"due": f"due en {mname}", "late": "en retard", "check": "à vérifier"}
    listed = [r for r in recs if r["status"] != "later"]
    order = {"due": 0, "late": 1, "check": 2}
    listed.sort(key=lambda r: (order[r["status"]], r["due"] or dt.date.max, r["line"]))
    for r in listed:
        st = status_label[r["status"]] + (f" : {r['reason']}" if r["reason"] else "")
        out.append(f"| {cell(label(r))} | {cell(shown(r))} | {r['date'].isoformat() if r['date'] else '—'} | "
                   f"{r['due'].isoformat() if r['due'] and r['status'] != 'check' else '—'} | {st} |")
    if not listed:
        out.append("| (aucun client retenu) | — | — | — | — |")
    for status, title, empty in (("due", f"Revues dues en {mname}", f"Aucune revue due en {mname} d'après le fichier."),
                                 ("late", "Revues en retard", "Aucune revue en retard d'après le fichier."),
                                 ("check", "À vérifier", "Aucune ligne à vérifier.")):
        out += ["", f"## {title}", ""]
        rs = [r for r in listed if r["status"] == status]
        out += [bullet(r, delay) for r in rs] or [empty]
    c = {k: sum(r["status"] == k for r in recs) for k in ("due", "late", "check", "later")}
    summary = (f"{plural(len(recs), 'ligne client lue', 'lignes client lues')} : "
               f"{plural(c['due'], 'revue due', 'revues dues')} en {mname}, "
               f"{plural(c['late'], 'revue en retard', 'revues en retard')}, "
               f"{plural(c['check'], 'ligne à vérifier', 'lignes à vérifier')}, "
               f"{plural(c['later'], 'client pas encore dû', 'clients pas encore dus')}")
    return "\n".join(out) + "\n", summary


def main(argv):
    args = argv[1:]
    if len(args) % 2:
        print(__doc__, file=sys.stderr)
        return 2
    opts = dict(zip(args[::2], args[1::2]))
    known = {"--fichier", "--mois", "--delai-mois", "--colonne-client", "--colonne-date", "--feuille", "--aujourdhui"}
    if "--fichier" not in opts or set(opts) - known:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        today = dt.date.fromisoformat(opts.get("--aujourdhui", dt.date.today().isoformat()))
        if "--mois" in opts:
            y, m = re.fullmatch(r"(\d{4})-(\d{2})", opts["--mois"]).groups()
            month = (int(y), int(m))
            dt.date(month[0], month[1], 1)
        else:
            month = (today.year, today.month)
        delay = int(opts.get("--delai-mois", "12"))
        if not 1 <= delay <= 120:
            raise ValueError
    except (ValueError, AttributeError):
        print("error: --mois AAAA-MM, --aujourdhui AAAA-MM-JJ, --delai-mois between 1 and 120", file=sys.stderr)
        return 2
    path = opts["--fichier"]
    col_client = opts.get("--colonne-client", "Référence")
    col_date = opts.get("--colonne-date", "Dernière revue")
    try:
        if path.lower().endswith((".xlsx", ".xlsm")):
            rows, date1904 = read_xlsx(path, opts.get("--feuille"))
        elif path.lower().endswith((".csv", ".txt")):
            rows, date1904 = read_csv(path), False
        else:
            raise TableError("expected a .csv or .xlsx file (.xls: save it as .xlsx or .csv first)")
        recs = classify(rows, col_client, col_date, month, delay, today, date1904)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except TableError as e:
        print(f"file error: {e}", file=sys.stderr)
        return 3
    text, summary = render(recs, path, col_client, col_date, month, delay, opts.get("--feuille"))
    sys.stdout.write(text)
    print(summary, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
