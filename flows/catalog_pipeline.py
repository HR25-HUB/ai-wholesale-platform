
from prefect import flow

@flow
def catalog_pipeline():
    print("Catalog normalization pipeline")
