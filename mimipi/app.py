import random

from typing import Annotated, Literal

from faker import Faker
from fastapi import FastAPI, Header, Response, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from scalar_fastapi import get_scalar_api_reference

from .product import Product


app = FastAPI(
    title="Product API",
    docs_url=None,
    redoc_url=None,
)


def stream_csv(products):
    yield "upc,name,details,weight\n"
    for product in products:
        yield f"{product.upc},{product.name},{product.details},{product.weight}".replace("\n", "\\n") + "\n"


@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        hide_download_button=True,
        hide_models=False,
    )

@app.get("/product")
def get_product(
    response: Response,
    accept: Annotated[str, Header()] = "text/csv",
    x_seed: Annotated[int|None, Header(description="The seed used to generate the product list. When no X-Seed header has been provided, a random seed will be generated.")] = None,
    quantity: int = Query(1, ge=1, description="Number of products to generate."),
    entropy: float = Query(0.0, ge=0.0, le=1.0, description="The percent chance of switching formatting of each row before generating each row.")
) -> Response:
    """Get a list of products."""
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
        case "application/json":
            return products
        case _:
            return StreamingResponse(content=stream_csv(products), media_type="text/csv", headers=response.headers)
