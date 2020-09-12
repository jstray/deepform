import os

import numpy as np
import pandas as pd

from deepform.common import DATA_DIR

if os.path.exists(DATA_DIR / "3_year_manifest.csv"):
    os.remove(DATA_DIR / "3_year_manifest.csv")


df12 = pd.read_csv(
    DATA_DIR / "2012_manifest.tsv", sep="\t"
)  # Formerly called ftf-all-filings.tsv
df12.insert(0, "serial_num", np.nan)
df12.insert(0, "flight_from", np.nan)
df12.insert(0, "flight_to", np.nan)
df12.insert(0, "issues", np.nan)
df12_new = df12.filter(
    [
        "dc_slug",
        "serial_num",
        "gross_amount",
        "committee",
        "flight_from",
        "flight_to",
        "url",
        "issues",
    ],
    axis=1,
)
df12_new.insert(0, "year", "2012")
df12_new.columns = [
    "year",
    "file_id",
    "contract_num",
    "gross_amount",
    "advertiser",
    "flight_from",
    "flight_to",
    "url",
    "issues",
]

df14 = pd.read_csv(
    DATA_DIR / "2014_manifest.tsv", sep="\t"
)  # Formerly called 2014-orders.tsv
df14.insert(0, "gross_amount", np.nan)
df14.insert(0, "url", np.nan)
df14.insert(0, "issues", np.nan)
df14_new = df14.filter(
    [
        "id",
        "order_revision",
        "gross_amount",
        "advertiser",
        "flight_from",
        "flight_to",
        "url",
        "issues",
    ],
    axis=1,
)
df14_new.insert(0, "year", "2014")
df14_new.columns = [
    "year",
    "file_id",
    "contract_num",
    "gross_amount",
    "advertiser",
    "flight_from",
    "flight_to",
    "url",
    "issues",
]

df20 = pd.read_csv(
    DATA_DIR / "2020_manifest.csv"
)  # Formerly called fcc-data-2020-sample-updated.csv
df20_new = df20.filter(
    [
        "full_file_name",
        "serial_num",
        "gross_amount",
        "advertiser",
        "flight_from",
        "flight_to",
        "url",
        "Issues ('', Type, or Token)",
    ],
    axis=1,
)
df20_new.insert(0, "year", "2020")
df20_new.columns = [
    "year",
    "file_id",
    "contract_num",
    "gross_amount",
    "advertiser",
    "flight_from",
    "flight_to",
    "url",
    "issues",
]

df = pd.concat([df12_new, df14_new, df20_new])

# df.set_index(["year", "slug"]).count(level="year")

df.to_csv(DATA_DIR / "3_year_manifest.csv", index=False)
