import polars as pl
from sample_ext_lib import hello, hello_from_bin

# データフレームの作成
df = pl.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["New York", "Los Angeles", "Chicago"]
})
print(df)

print(hello())
print(hello_from_bin())
