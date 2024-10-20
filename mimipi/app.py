import random

from typing import Annotated, Literal

from faker import Faker
from fastapi import FastAPI, Header, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .product import Product


app = FastAPI()


def stream_csv(products):
    yield "upc,name,details,weight\n"
    for product in products:
        yield f"{product.upc},{product.name},{product.details},{product.weight}".replace("\n", "\\n") + "\n"


@app.get("/product")
def get_product(
    response: Response,
    accept: Annotated[str|None, Header()] = None,
    x_seed: Annotated[int|None, Header()] = None,
    quantity: int = 1,
    entropy: float = 0,
):
    seed = x_seed or random.randint(0, 100000)
    response.headers["X-Seed"] = str(seed)

    rng = random.Random(seed)
    fake = Faker()
    fake.seed_instance(seed)

    upc_faker_list = [fake.ean8, fake.ean13]
    upc_faker = rng.choice(upc_faker_list)

    name_faker_list = [fake.word, fake.sentence, fake.text]
    name_faker = rng.choice(name_faker_list)

    details_faker_list = [fake.sentence, fake.text]
    details_faker = rng.choice(details_faker_list)

    weight_faker_list = [fake.random_int]
    weight_faker = rng.choice(weight_faker_list)


    products = []
    for _ in range(quantity):
        if rng.random() <= entropy:
            upc_faker = rng.choice(upc_faker_list)
            name_faker = rng.choice(name_faker_list)
            details_faker = rng.choice(details_faker_list)
            weight_faker = rng.choice(weight_faker_list)

        products.append(Product(
            upc=upc_faker(),
            name=name_faker(),
            details=details_faker(),
            weight=weight_faker(),
        ))

    # Shuffle to avoid bunching up simiarly generated products based on entropy
    rng.shuffle(products)

    match accept:
        case "text/csv":
            return StreamingResponse(content=stream_csv(products), media_type="text/csv", headers=response.headers)
        case _:
            return products
