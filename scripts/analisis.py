import os
import json
import csv
import networkx as nx
from networkx.algorithms.community import louvain_communities

def calcular_comunidades_louvain(G):
    """
    Aplica el algoritmo de Louvain sobre un grafo no dirigido.
    Devuelve un diccionario plano {nodo: id_comunidad}.
    """
    if G.is_directed():
        G_undirected = G.to_undirected()
    else:
        G_undirected = G

    comunidades_lista = louvain_communities(G_undirected, seed=42)
    
    comunidades_dict = {}
    for id_comunidad, comunidad in enumerate(comunidades_lista):
        for nodo in comunidad:
            # Aseguramos que la llave sea un string para consistencia en JSON
            comunidades_dict[str(nodo)] = id_comunidad
            
    return comunidades_dict


def calcular_pagerank_normalizado(G):
    """
    Calcula el PageRank manteniendo la dirección si es un dígrafo.
    Devuelve un diccionario plano {nodo: pagerank_normalizado} con valores entre 0 y 1.
    """
    pr = nx.pagerank(G)
    
    if not pr:
        return {}
        
    min_val = min(pr.values())
    max_val = max(pr.values())
    
    if max_val == min_val:
        return {str(nodo): 1.0 for nodo in pr}
        
    pr_normalizado = {str(nodo): (val - min_val) / (max_val - min_val) for nodo, val in pr.items()}
    return pr_normalizado


def generar_reporte_y_archivos(G, comunidades_dict, pagerank_dict, folder_output="data"):
    """
    Procesa las comunidades y el PageRank para generar los tres archivos requeridos:
    1. comunidades.json
    2. pagerank.json
    3. resumen_comunidades.csv
    """
    # Asegurar que la carpeta 'data' exista
    os.makedirs(folder_output, exist_ok=True)
    
    # Definición de rutas exactas
    path_comunidades_json = os.path.join(folder_output, "comunidades.json")
    path_pagerank_json = os.path.join(folder_output, "pagerank.json")
    path_resumen_csv = os.path.join(folder_output, "resumen_comunidades.csv")

    # 1. Exportar comunidades.json (Diccionario: nodo -> número de comunidad)
    with open(path_comunidades_json, 'w', encoding='utf-8') as f:
        json.dump(comunidades_dict, f, indent=4, ensure_ascii=False)
    print(f"[OK] Archivo '{path_comunidades_json}' generado.")

    # 2. Exportar pagerank.json (Diccionario: nodo -> puntaje normalizado)
    with open(path_pagerank_json, 'w', encoding='utf-8') as f:
        json.dump(pagerank_dict, f, indent=4, ensure_ascii=False)
    print(f"[OK] Archivo '{path_pagerank_json}' generado.")

    # 3. Procesar datos para resumen_comunidades.csv
    num_comunidades = max(comunidades_dict.values()) + 1
    
    # Agrupar los nodos que pertenecen a cada comunidad
    comunidades_agrupadas = {i: [] for i in range(num_comunidades)}
    for nodo, id_com in comunidades_dict.items():
        comunidades_agrupadas[id_com].append(nodo)

    # Abrir el archivo CSV para escribir la tabla resumen
    with open(path_resumen_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Encabezados de la tabla
        writer.writerow(['comunidad', 'tamaño', 'promedio_pagerank', 'top_5_influyentes'])
        
        for id_com in range(num_comunidades):
            nodos_comunidad = comunidades_agrupadas[id_com]
            tamano = len(nodos_comunidad)
            
            if tamano == 0:
                continue
            
            # Calcular el promedio de PageRank de la comunidad
            suma_pr = sum(pagerank_dict[nodo] for nodo in nodos_comunidad)
            promedio_pr = float(suma_pr / tamano)
            
            # Obtener el Top 5 de usuarios influyentes (ordenados por su PageRank de mayor a menor)
            top_nodos = sorted(nodos_comunidad, key=lambda n: pagerank_dict[n], reverse=True)[:5]
            # Convertimos la lista de los top 5 a un formato string legible para una celda CSV (ej: "User1, User2, User3")
            top_nodos_str = ", ".join(top_nodos)
            
            # Escribir la fila correspondiente a esta comunidad
            writer.writerow([id_com, tamano, f"{promedio_pr:.6f}", top_nodos_str])
            
    print(f"[OK] Archivo '{path_resumen_csv}' generado exitosamente.")


def main():
    graphml_path = "data\grafo.graphml" 
    
    print(f"Cargando el grafo desde {graphml_path}...")
    try:
        G = nx.read_graphml(graphml_path)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{graphml_path}'.")
        return

    print(f"Grafo cargado correctamente. Nodos: {G.number_of_nodes()} | Aristas: {G.number_of_edges()}")
    
    print("Calculando comunidades con Louvain...")
    comunidades = calcular_comunidades_louvain(G)
    
    print("Calculando PageRank normalizado...")
    pagerank = calcular_pagerank_normalizado(G)
    
    print("Generando entregables finales...")
    generar_reporte_y_archivos(G, comunidades, pagerank, folder_output="data")

if __name__ == "__main__":
    main()