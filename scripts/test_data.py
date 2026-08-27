import duckdb

df = duckdb.sql("""
    SELECT *
    FROM read_csv_auto('data/raw/patients.csv')
    LIMIT 10
""").df()

print(df)