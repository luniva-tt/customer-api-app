-- 1.Show all the customers whose creditLimit is greater than 20000

SELECT * 
FROM customers
WHERE creditLimit > 20000;


-- 2. Show the employees who report to VP Sales

SELECT e.*
FROM employees e
JOIN employees m ON e.reportsTo = m.employeeNumber
WHERE m.jobTitle = 'VP Sales';


-- 3. Find all the customers who have set their state while filling the forms and Lives in USA and credit limit is between 100000 and 200000.

SELECT *
FROM customers
WHERE state IS NOT NULL
  AND country = 'USA'
  AND creditLimit BETWEEN 100000 AND 200000;


-- 4. Find all the employees who report to Sales Managers of all types.

SELECT e.*
FROM employees e
JOIN employees m ON e.reportsTo = m.employeeNumber
WHERE m.jobTitle LIKE '%Sales Manager%';


-- 5. Find the average credit limit of customers of each country.

SELECT country, AVG(creditLimit) AS avg_credit_limit
FROM customers
GROUP BY country;


-- 6. Find the total no. of orders for each date and customer. Show only dates with total number of orders greater than 10 for date and customer.

SELECT orderDate, customerNumber, COUNT(*) AS total_orders
FROM orders
GROUP BY orderDate, customerNumber
HAVING COUNT(*) > 10;


-- 7. Find the name of the supervisor, job title of supervisor and total no. of supervisee using subquery. (With out using Join operation)

SELECT 
  CONCAT(firstName, ' ', lastName) AS supervisor_name,
  jobTitle,
  (SELECT COUNT(*) 
   FROM employees e2 
   WHERE e2.reportsTo = e1.employeeNumber) AS total_supervisees
FROM employees e1;


-- 8. Find the name of the supervisor, job title of supervisor and total no. of supervisee using subquery. (With using Join operation)

SELECT 
  CONCAT(m.firstName, ' ', m.lastName) AS supervisor_name,
  m.jobTitle,
  COUNT(e.employeeNumber) AS total_supervisees
FROM employees m
LEFT JOIN employees e ON e.reportsTo = m.employeeNumber
GROUP BY m.employeeNumber;


-- 9. Find all customers with a credit limit greater than average credit credit limit using WITH Clause.
WITH avg_credit AS (
  SELECT AVG(creditLimit) AS avg_val FROM customers
)
SELECT *
FROM customers, avg_credit
WHERE customers.creditLimit > avg_credit.avg_val;


-- 10. Find the rank of customer. [Customer with highest credit limit have 1 rank and Customer with lowest credit limit have highest rank]. Then, find the customer with the third highest credit limit.

WITH ranked_customers AS (
  SELECT customerName, creditLimit,
         RANK() OVER (ORDER BY creditLimit DESC) AS rnk
  FROM customers
)
SELECT *
FROM ranked_customers
WHERE rnk = 3;


-- 11. Generate a report that shows total no. of employees working in each office.

SELECT officeCode, COUNT(*) AS total_employees
FROM employees
GROUP BY officeCode;


-- 12. Generate a report that shows total no. of customers visited each office.

SELECT o.officeCode, COUNT(c.customerNumber) AS total_customers
FROM offices o
LEFT JOIN employees e ON o.officeCode = e.officeCode
LEFT JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
GROUP BY o.officeCode;


-- 13. Generate a report that shows total payment received by each office using payment tables and essential tables. The report should show the office name, state and country, along with total payments made.

SELECT o.officeCode, o.state, o.country,
       SUM(p.amount) AS total_payments
FROM offices o
JOIN employees e ON o.officeCode = e.officeCode
JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
JOIN payments p ON c.customerNumber = p.customerNumber
GROUP BY o.officeCode, o.state, o.country;


-- 14. Generate a report that shows total sales(in amount) by each office using order details table and other essential tables.

SELECT o.officeCode,
       SUM(od.quantityOrdered * od.priceEach) AS total_sales
FROM offices o
JOIN employees e ON o.officeCode = e.officeCode
JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
JOIN orders ord ON c.customerNumber = ord.customerNumber
JOIN orderdetails od ON ord.orderNumber = od.orderNumber
GROUP BY o.officeCode;


-- 15. Generate a report that shows total payment pending for each office.

SELECT o.officeCode,
       SUM(od.quantityOrdered * od.priceEach) - IFNULL(SUM(p.amount), 0) AS pending_amount
FROM offices o
JOIN employees e ON o.officeCode = e.officeCode
JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
JOIN orders ord ON c.customerNumber = ord.customerNumber
JOIN orderdetails od ON ord.orderNumber = od.orderNumber
LEFT JOIN payments p ON c.customerNumber = p.customerNumber
GROUP BY o.officeCode;


-- 16.Find the creditLimit of each person, proportion of creditLimit of each person in each country. [Proportion of person in USA = creditLimit of that person / sum(creditLimit of all person in USA] 

SELECT customerName, country, creditLimit,
       creditLimit / SUM(creditLimit) OVER (PARTITION BY country) AS proportion
FROM customers;


-- 17. Create a view showing the customer name, complete address, and their total number of orders.

CREATE VIEW customer_order_summary AS
SELECT c.customerName,
       CONCAT(c.addressLine1, ', ', c.city, ', ', c.country) AS address,
       COUNT(o.orderNumber) AS total_orders
FROM customers c
LEFT JOIN orders o ON c.customerNumber = o.customerNumber
GROUP BY c.customerNumber;

select *  from customers where customerNumber = 103;

-- 18. Update the country of a customer (use any one record).

UPDATE customers
SET country = 'Nepal'
WHERE customerNumber = 103;

select *  from customers where customerNumber = 103;

select * from payments WHERE amount < 20000;
SET SQL_SAFE_UPDATES = 0;
-- 19. Delete all payments below 20,000.

DELETE FROM payments
WHERE amount < 20000;
select * from payments WHERE amount < 20000;


-- 20.Add new payments manually for an existing customer.

INSERT INTO payments (customerNumber, checkNumber, paymentDate, amount)
VALUES (103, 'NEW12345', '2026-05-03', 25000);

select * from payments where checkNumber = 'New12345';
SET SQL_SAFE_UPDATES = 0;


Error Code: 1175. You are using safe update mode and you tried to update a table without a WHERE that uses a KEY column.  To disable safe mode, toggle the option in Preferences -> SQL Editor and reconnect.
