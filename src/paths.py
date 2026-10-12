"""Repository paths shared by every pipeline step, resolved from the repo root
so scripts work from any working directory."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

RAW_HS2 = DATA / "raw" / "census_hs2"      # one gzip of API JSON per month
INTERIM = DATA / "interim"                  # tidy tables built from raw
PANEL_HS2 = INTERIM / "imports_hs2_panel.csv"
ANOMALIES_KG = INTERIM / "anomalies_kg.csv"
