import pandas as pd

def drop_invalid_tools (df: pd.DataFrame, toolings_list: list):
    """
    Function to drop toolings items which are invalid

    Params:
    - df: DataFrame to be used
    - toolings_list: List of ID's for all toolings which to be deleted

    Returns:
    - DataFrame without all those toolings
    """

    df_cleaned = df.copy()

    df_cleaned = df_cleaned[~df_cleaned['ToolID'].isin(df_cleaned)]

    return df_cleaned