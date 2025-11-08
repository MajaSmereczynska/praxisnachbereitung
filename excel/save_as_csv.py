import pandas as pd
from datetime import datetime
xlsx_path = "Aufgabe3.xlsx"
sheet = "A3c" # Blattname mit finalen Daten
out_path = f"gesamttabelle_{datetime.now():%Y-%m-%d}.csv"
df = pd.read_excel(xlsx_path, sheet_name=sheet)
df.columns = [c.strip() for c in df.columns]
df.to_csv(out_path, index=False, sep=";", encoding="utf-8")
print(f"Export ok → {out_path}")
