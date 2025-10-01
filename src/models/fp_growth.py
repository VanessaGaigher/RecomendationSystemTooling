import pandas as pd
from mlxtend.frequent_patterns import fpgrowth

def get_frequent_itemsets(df_encoded: pd.DataFrame, min_support: float = 0.01) -> pd.DataFrame:
    """
    Finds frequent itemsets in a one-hot encoded transaction DataFrame
    using the FP-Growth algorithm.

    Parameters
    ----------
    df_encoded : pd.DataFrame
        One-hot encoded DataFrame of transactions.
    min_support : float, default=0.01
        Minimum support threshold for the itemsets.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the frequent itemsets and their support.
    
    Example
    -------
    >>> df_encoded = pd.DataFrame({
    ...     'A': [1, 0, 1],
    ...     'B': [1, 1, 0],
    ...     'C': [0, 1, 1],
    ...     'D': [0, 1, 0]
    ... })
    >>> get_frequent_itemsets(df_encoded, min_support=0.5)
       support     itemsets
    0     0.5         (A,)
    1     0.5         (B,)
    2     0.5         (C,)
    """
    frequent_itemsets = fpgrowth(df_encoded, min_support=min_support, use_colnames=True)
    
    return frequent_itemsets
