# %%
import pandas as pd

def create_entities(sheet: str) -> None:
    """
    Creates the initial entities as a dict from an excel sheet.
    """
    df = pd.read_excel(sheet)
    if validate_data(df):
        return df.to_dict("records")
    else:
        raise ValueError("Boot file does not contain msisdn")

def validate_data(df: pd.DataFrame) -> bool:
    """
    Validates that the body includes msisdn.
    """
    return "msisdn" in df.columns