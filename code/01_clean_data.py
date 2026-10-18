"""01_clean_data.py — Build the processed analysis data (thin wrapper around ck94_utils)."""
from ck94_utils import load_clean_data, OUT_PROCESSED

df = load_clean_data()
print(f"Saved processed data: {OUT_PROCESSED}")
print("Rows:", len(df), "| NJ:", int(df.STATE.sum()), "| PA:", int((df.STATE == 0).sum()))
print("\nKey validation counts:")
print("FTE1 nonmissing:", int(df.FTE1.notna().sum()), "| FTE2 nonmissing:", int(df.FTE2.notna().sum()))
print("Balanced (FTE1&FTE2):", int((df.FTE1.notna() & df.FTE2.notna()).sum()))
print("Closed stores (FTE2=0):", int((df.STATUS2 == 3).sum()),
      "| Temp/renov missing:", int(df.STATUS2.isin({2, 4, 5}).sum()),
      "| Refusal:", int((df.STATUS2 == 0).sum()))
