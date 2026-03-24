
from prefect import flow

@flow
def rfq_pipeline():
    print("RFQ pipeline started")

if __name__ == "__main__":
    rfq_pipeline()
