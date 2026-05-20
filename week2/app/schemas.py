from pydantic import BaseModel
from typing import Optional


class CustomerBase(BaseModel):
    customerName: str
    contactLastName: str
    contactFirstName: str
    phone: str

    addressLine1: str
    addressLine2: Optional[str] = None

    city: str
    state: Optional[str] = None

    postalCode: Optional[str] = None
    country: str

    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[int] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    customerName: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class CustomerOut(CustomerBase):
    customerNumber: int

    class Config:
        from_attributes = True