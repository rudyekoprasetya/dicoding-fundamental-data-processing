
def load_to_csv(df, path="products.csv"):
    try:
        df.to_csv(path, index=False)
    except Exception as e:
        print(f"An erro occurred an save to CSV : {e}")