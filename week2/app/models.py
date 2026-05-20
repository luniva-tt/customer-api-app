from sqlalchemy import Column, Integer, String
from week2.app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customerNumber = Column(Integer, primary_key=True, index=True)
    customerName = Column(String(50), nullable=False)

    contactLastName = Column(String(50), nullable=False)
    contactFirstName = Column(String(50), nullable=False)

    phone = Column(String(50), nullable=False)

    addressLine1 = Column(String(50), nullable=False)
    addressLine2 = Column(String(50))

    city = Column(String(50), nullable=False)
    state = Column(String(50))

    postalCode = Column(String(15))
    country = Column(String(50), nullable=False)

    salesRepEmployeeNumber = Column(Integer)
    creditLimit = Column(Integer)

    class Order(Base):
        __tablename__ = "orders"


        orderNumber = Column(Integer, primary_key=True)


class Product(Base):
    __tablename__ = "products"

    productCode = Column(String, primary_key=True)


class Employee(Base):
    __tablename__ = "employees"

    employeeNumber = Column(Integer, primary_key=True)


class Office(Base):
    __tablename__ = "offices"

    officeCode = Column(String, primary_key=True)


class Payment(Base):
    __tablename__ = "payments"

    customerNumber = Column(Integer, primary_key=True)
    checkNumber = Column(String, primary_key=True)


class OrderDetail(Base):
    __tablename__ = "orderdetails"

    orderNumber = Column(Integer, primary_key=True)
    productCode = Column(String, primary_key=True)


class ProductLine(Base):
    __tablename__ = "productlines"

    productLine = Column(String, primary_key=True)