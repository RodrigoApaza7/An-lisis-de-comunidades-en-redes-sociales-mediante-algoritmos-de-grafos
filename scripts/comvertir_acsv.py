import pandas as pd

df = pd.read_csv(
    "data/facebook_combined.txt",
    sep=" ",
    header=None,
    names=["source", "target"]
)

df["weight"] = 1

df.to_csv("data/edges.csv", index=False)


print(df.head())
print("completado")