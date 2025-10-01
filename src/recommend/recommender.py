import pandas as pd
from mlxtend.frequent_patterns import association_rules
from mlxtend.frequent_patterns import fpgrowth
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
from typing import List, Set
import numpy as np

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


def classify_rules(rules: pd.DataFrame) -> pd.DataFrame:
    """
    Classifies association rules into categories based on lift and confidence
    using vectorized operations (no nested function).

    Parameters
    ----------
    rules : pd.DataFrame
        DataFrame containing association rules with 'lift' and 'confidence' columns.

    Returns
    -------
    pd.DataFrame
        DataFrame with an additional column 'classe' indicating rule category:
        - "Compatibilidade forte" for strong compatibility
        - "Contextual" for contextual rules
        - "Incompatibilidade" for incompatible rules
    
    Example
    -------
    >>> df_rules = classify_rules(rules_df)
    >>> df_rules[['lift', 'confidence', 'classe']].head()
    """
    rules = rules.copy()
    
    conditions = [
        (rules['lift'] > 3) & (rules['confidence'] > 0.6),
        (rules['lift'] > 1) & (rules['lift'] <= 3),
        (rules['lift'] <= 1)
    ]
    
    choices = ["Compatibilidade forte", "Contextual", "Incompatibilidade"]
    
    rules['classe'] = np.select(conditions, choices, default="Contextual")
    
    return rules


def get_association_rules(
    frequent_itemsets: pd.DataFrame, 
    metric: str = "lift", 
    min_threshold: float = 0.1
) -> pd.DataFrame:
    """
    Generates association rules from frequent itemsets and sorts them
    by lift and confidence in descending order.

    Parameters
    ----------
    frequent_itemsets : pd.DataFrame
        DataFrame containing frequent itemsets and their support.
    metric : str, default="lift"
        Metric to evaluate the association rules (e.g., 'lift', 'confidence', 'support').
    min_threshold : float, default=0.1
        Minimum threshold for the chosen metric to filter rules.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the association rules sorted by lift and confidence.
    
    Example
    -------
    >>> frequent_itemsets = pd.DataFrame({
    ...     'support': [0.5, 0.5, 0.5],
    ...     'itemsets': [('A',), ('B',), ('C',)]
    ... })
    >>> get_association_rules(frequent_itemsets, metric="lift", min_threshold=0.5)
       antecedents consequents  ...  lift  leverage  conviction
    0        (A,)       (B,)  ...   ...      ...         ...
    """
    rules = association_rules(frequent_itemsets, metric=metric, min_threshold=min_threshold)
    rules = rules.sort_values(["lift", "confidence"], ascending=False).reset_index(drop=True)
    return rules



    """
    Categorizes association rules into strong, contextual, and incompatible
    based on lift and confidence thresholds.

    Parameters
    ----------
    rules : pd.DataFrame
        DataFrame containing association rules with 'lift' and 'confidence' columns.

    Returns
    -------
    dict
        Dictionary with keys:
        - 'strong_rules': rules with lift > 3 and confidence > 0.7
        - 'contextual_rules': rules with 1 < lift <= 3
        - 'incompatibles': rules with lift < 1
    
    Example
    -------
    >>> categorized = categorize_rules(rules_df)
    >>> categorized['strong_rules'].head()
    """
    strong_rules = rules[(rules['lift'] > 3) & (rules['confidence'] > 0.7)].copy()
    contextual_rules = rules[(rules['lift'] > 1) & (rules['lift'] <= 3)].copy()
    incompatibles = rules[rules['lift'] < 1].copy()
    
    return {
        "strong_rules": strong_rules,
        "contextual_rules": contextual_rules,
        "incompatibles": incompatibles
    }


def build_graph_and_detect_communities(strong_rules: pd.DataFrame) -> tuple:
    """
    Builds a graph from strong association rules and detects communities
    using the greedy modularity algorithm.

    Parameters
    ----------
    strong_rules : pd.DataFrame
        DataFrame containing strong association rules with 'antecedents',
        'consequents', and 'lift' columns.

    Returns
    -------
    tuple
        - G : networkx.Graph
            The graph where nodes are items and edges are weighted by lift.
        - communities : list of sets
            List of communities detected in the graph.
    
    Example
    -------
    >>> G, communities = build_graph_and_detect_communities(strong_rules_df)
    >>> len(communities)
    3
    """
    G = nx.Graph()
    
    for _, row in strong_rules.iterrows():
        antecedents = [str(a) for a in row['antecedents']]
        consequents = [str(c) for c in row['consequents']]
        for ant in antecedents:
            for cons in consequents:
                G.add_edge(ant, cons, weight=row['lift'])
    
    communities = list(greedy_modularity_communities(G))
    
    return G, communities


def create_item_group_dataframe(communities: List[Set[str]]) -> pd.DataFrame:
    """
    Creates a DataFrame mapping each item to its detected community/group.

    Parameters
    ----------
    communities : list of sets
        List of communities (sets of items) detected in a graph.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - 'item': item name
        - 'grupo': integer representing the community/group ID
    
    Example
    -------
    >>> communities = [{'A', 'B'}, {'C', 'D'}]
    >>> create_item_group_dataframe(communities)
      item  grupo
    0    A      0
    1    B      0
    2    C      1
    3    D      1
    """
    item_to_group = {}
    for i, comm in enumerate(communities):
        for item in comm:
            item_to_group[item] = i

    df_items_group = pd.DataFrame({
        'item': list(item_to_group.keys()),
        'grupo': list(item_to_group.values())
    })
    
    return df_items_group


def recomendar_itens_otimizado_grupo(carrinho, rules, df_itens_grupo, top_n=10) -> pd.DataFrame:
    """
    Generates optimized item recommendations for a shopping cart based on
    association rules and item communities/groups.

    Parameters
    ----------
    carrinho : list
        List of items currently in the shopping cart.
    rules : pd.DataFrame
        DataFrame containing association rules with columns 'antecedents', 
        'consequents', 'lift', and 'classe'.
    df_itens_grupo : pd.DataFrame
        DataFrame mapping each item to its community/group with columns 'item' and 'grupo'.
    top_n : int, default=10
        Number of top recommendations to return.

    Returns
    -------
    pd.DataFrame
        DataFrame with recommended items sorted by lift score, containing columns:
        - 'item': recommended item
        - 'lift': original lift of the rule
        - 'classe': classification of the rule ('Compatibilidade forte', 'Contextual', 'Incompatibilidade')

    Notes
    -----
    Items from the same community/group as items in the cart receive a boost in score 
    (1.5x) to prioritize related items.

    Example
    -------
    >>> carrinho = ['A', 'B']
    >>> recommended_df = recomendar_itens_otimizado_grupo(carrinho, rules_df, df_items_group, top_n=5)
    >>> recommended_df
       item  lift               classe
    0    C   1.8  Compatibilidade forte
    1    D   1.5             Contextual
    2    E   1.2             Contextual
    """
    recomendados = {}
    carrinho_set = set(carrinho)
    
    # pega grupos do carrinho
    grupos_carrinho = df_itens_grupo[df_itens_grupo['item'].isin(carrinho_set)]['grupo'].unique()
    
    for _, row in rules.iterrows():
        antecedents = set([str(a) for a in row['antecedents']])
        consequents = set([str(c) for c in row['consequents']])
        
        # checa se regra aplica
        if len(carrinho_set & antecedents) > 0:
            for item in consequents:
                item_str = str(item)

                fator_boost = 1.0
                grupo_item = df_itens_grupo.loc[df_itens_grupo['item'] == item_str, 'grupo']
                if len(grupo_item) > 0 and grupo_item.values[0] in grupos_carrinho:
                    fator_boost = 1.5  # boost if same community

                score = row['lift'] * fator_boost

                if item_str not in recomendados or score > recomendados[item_str]['score']:
                    recomendados[item_str] = {'score': score, 'lift': row['lift'], 'classe': row['classe']}
    
    # converte para DataFrame
    recomendados_df = pd.DataFrame([
        {'item': k, 'lift': v['lift'], 'classe': v['classe']} for k, v in recomendados.items()
    ])
    
    # ordena e pega top N
    recomendados_df = recomendados_df.sort_values('lift', ascending=False).head(top_n).reset_index(drop=True)
    
    return recomendados_df
