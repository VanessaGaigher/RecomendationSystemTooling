import pandas as pd
from mlxtend.preprocessing import TransactionEncoder

def group_movements_ids_into_list(
    df: pd.DataFrame, 
    group_key: str = "MOVEMENTID", 
    value_column: str = "Tool"
) -> list:
    """
    Groups the values of a specified column into lists, 
    based on a grouping key column.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing the data to be grouped.
    group_key : str, default="MOVEMENTID"
        Column name used as the grouping key.
    value_column : str, default="Tool"
        Column name whose values will be grouped into lists.

    Returns
    -------
    list
        A list of lists, where each sublist contains the grouped values 
        corresponding to a group in the grouping key.
    
    Example
    -------
    >>> data = {
    ...     "MOVEMENTID": [1, 1, 2, 2, 2],
    ...     "Tool": ["A", "B", "C", "D", "E"]
    ... }
    >>> df = pd.DataFrame(data)
    >>> group_movements_ids_into_list(df)
    [['A', 'B'], ['C', 'D', 'E']]
    """
    list_grouped = df.groupby(group_key)[value_column].apply(list).tolist()

    return list_grouped


def get_matrix_encoded(list_of_movements: list) -> pd.DataFrame:
    """
    Encodes a list of transactions into a one-hot encoded DataFrame
    using TransactionEncoder from mlxtend.

    Parameters
    ----------
    list_of_movements : list
        A list of lists, where each sublist contains items of a transaction.

    Returns
    -------
    pd.DataFrame
        A one-hot encoded DataFrame representing the transactions.
    
    Example
    -------
    >>> transactions = [['A', 'B'], ['B', 'C', 'D'], ['A', 'C']]
    >>> get_matrix_encoded(transactions)
       A  B  C  D
    0  1  1  0  0
    1  0  1  1  1
    2  1  0  1  0
    """
    te = TransactionEncoder()
    te_ary = te.fit(list_of_movements).transform(list_of_movements)
    df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
    
    return df_encoded