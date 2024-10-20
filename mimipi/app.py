import random

from typing import Annotated

from faker import Faker
from fastapi import FastAPI, Header, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .product import Product


app = FastAPI()


def stream_csv(products):
    yield "upc,name,details,weight,barcode\n"
    for product in products:
        yield f"{product.upc if product.upc else ''},{product.name},{product.details},{product.weight},{product.barcode}\n"


@app.get("/product")
def get_product(
    response: Response,
    accept: Annotated[str|None, Header()] = None,
    x_seed: Annotated[int|None, Header()] = None,
    quantity: int = 1
):
    seed = x_seed or random.randint(0, 100000)
    rng = random.Random(seed)
    fake = Faker()
    fake.seed_instance(seed)

    products = [Product(
        upc=fake.ean8(),
        name=fake.word(),
        details=fake.sentence(),
        weight=fake.random_int(1, 100),
        barcode=fake.ean13(),
    ) for _ in range(quantity)]

    match accept:
        case "text/csv":
            return StreamingResponse(content=stream_csv(products), media_type="text/csv", headers={"X-Seed": str(seed)})
        case _:
            response.headers["X-Seed"] = str(seed)
            return products
