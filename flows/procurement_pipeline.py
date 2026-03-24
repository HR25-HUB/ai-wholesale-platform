
from prefect import flow

@flow
def procurement_pipeline():
    print("Supplier discovery pipeline")
