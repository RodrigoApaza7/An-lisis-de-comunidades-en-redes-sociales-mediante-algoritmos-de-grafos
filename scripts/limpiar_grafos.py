import pandas as pd
import networkx as nx

# =========================================
# 1. CARGAR CSV
# =========================================

df = pd.read_csv("data/edges.csv")

print("Primeras filas:")
print(df.head())

# =========================================
# 2. LIMPIEZA BÁSICA
# =========================================

# eliminar filas vacías
df = df.dropna()

# eliminar auto-conexiones
df = df[df["source"] != df["target"]]

# eliminar pesos bajos
UMBRAL_PESO = 1

df = df[df["weight"] >= UMBRAL_PESO]

print("\nDatos después de limpieza:")
print(df.head())

# =========================================
# 3. CREAR GRAFO
# =========================================

G = nx.from_pandas_edgelist(
    df,
    source="source",
    target="target",
    edge_attr="weight",
    create_using=nx.Graph()
)

print("Nodos:", G.number_of_nodes())
print("Aristas:", G.number_of_edges())

# Si quieres dirigido:
# create_using=nx.DiGraph()

# =========================================
# 4. ELIMINAR NODOS AISLADOS
# =========================================

isolated = list(nx.isolates(G))

print(f"\nNodos aislados encontrados: {len(isolated)}")

G.remove_nodes_from(isolated)

# =========================================
# 5. INFORMACIÓN DEL GRAFO
# =========================================

print("\nInformación del grafo:")
print(f"Número de nodos: {G.number_of_nodes()}")
print(f"Número de aristas: {G.number_of_edges()}")

print(
    f"Número de componentes conectados: "
    f"{nx.number_connected_components(G)}"
)

print(
    f"Densidad: "
    f"{nx.density(G):.6f}"
)

# =========================================
# 6. COMPONENTE GIGANTE
# =========================================

largest_cc = max(nx.connected_components(G), key=len)

G = G.subgraph(largest_cc).copy()

print("\nComponente gigante:")
print(f"Nodos: {G.number_of_nodes()}")
print(f"Aristas: {G.number_of_edges()}")

# =========================================
# 7. GUARDAR
# =========================================

nx.write_graphml(G, "data/grafo.graphml")
nx.write_gml(G, "data/grafo.gml")

print("\nArchivos exportados correctamente.")