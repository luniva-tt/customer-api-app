from sqlalchemy.orm import Session
from app import models, schemas
from app.logger import logger


def get_customers(db: Session, skip: int = 0, limit: int = 10):
    logger.info("Fetching customers")

    return (
        db.query(models.Customer)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_customer_by_id(db: Session, customer_id: int):
    logger.info(f"Fetching customer {customer_id}")

    return (
        db.query(models.Customer)
        .filter(
            models.Customer.customerNumber == customer_id
        )
        .first()
    )


def create_customer(
    db: Session,
    customer: schemas.CustomerCreate
):
    logger.info("Creating customer")

    db_customer = models.Customer(**customer.model_dump())

    db.add(db_customer)

    db.commit()

    db.refresh(db_customer)

    return db_customer


def update_customer(
    db: Session,
    customer_id: int,
    customer_update: schemas.CustomerUpdate
):
    customer = get_customer_by_id(db, customer_id)

    if not customer:
        return None

    update_data = customer_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(customer, key, value)

    db.commit()

    db.refresh(customer)

    return customer


def delete_customer(db: Session, customer_id: int):
    customer = get_customer_by_id(db, customer_id)

    if not customer:
        return None

    db.delete(customer)

    db.commit()

    return customer

    def get_customers_count(db: Session):
        logger.info("Counting customers")

    return db.query(models.Customer).count()


def get_orders_count(db: Session):
    logger.info("Counting orders")

    return db.query(models.Order).count()


def get_products_count(db: Session):
    logger.info("Counting products")

    return db.query(models.Product).count()


def get_employees_count(db: Session):
    logger.info("Counting employees")

    return db.query(models.Employee).count()


def get_offices_count(db: Session):
    logger.info("Counting offices")

    return db.query(models.Office).count()


def get_payments_count(db: Session):
    logger.info("Counting payments")

    return db.query(models.Payment).count()


def get_orderdetails_count(db: Session):
    logger.info("Counting orderdetails")

    return db.query(models.OrderDetail).count()


def get_productlines_count(db: Session):
    logger.info("Counting productlines")

    return db.query(models.ProductLine).count()