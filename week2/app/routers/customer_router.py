from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from week2.app.database import get_db
from week2.app import schemas
from week2.app.logger import logger
from week2.app import crud

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.get(
    "/",
    response_model=List[schemas.CustomerOut]
)
def get_customers(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    logger.info("GET all customers request")

    return crud.get_customers(
        db,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{customer_id}",
    response_model=schemas.CustomerOut
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"GET customer {customer_id}")

    customer = crud.get_customer_by_id(
        db,
        customer_id
    )

    if not customer:
        logger.warning(
            f"Customer not found {customer_id}"
        )

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


@router.post(
    "/",
    response_model=schemas.CustomerOut
)
def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db)
):
    logger.info("POST create customer")

    return crud.create_customer(db, customer)


@router.put(
    "/{customer_id}",
    response_model=schemas.CustomerOut
)
def update_customer(
    customer_id: int,
    customer: schemas.CustomerUpdate,
    db: Session = Depends(get_db)
):
    updated_customer = crud.update_customer(
        db,
        customer_id,
        customer
    )

    if not updated_customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return updated_customer


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    deleted_customer = crud.delete_customer(
        db,
        customer_id
    )

    if not deleted_customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return {
        "message":
        f"Customer {customer_id} deleted"
    }