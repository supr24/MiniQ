// ============================================
// 20 EXAMPLE PROGRAMS - MiniQ SQL QUERIES
// ============================================

// Object with all examples
// Key = value from dropdown option
// Value = { name, code }

const examples = {
    
    filter: {
        name: "1. Filter Students",
        code: `load students
filter age > 18
select name, age, marks`
    },
    
    simple_sort: {
        name: "2. Sort by Marks",
        code: `load students
select name, marks
sort by marks desc`
    },
    
    limit_results: {
        name: "3. Top 5 Students",
        code: `load students
select name, marks
sort by marks desc
limit 5`
    },
    
    aggregate_sum: {
        name: "4. Total Revenue",
        code: `load sales
aggregate sum(revenue) as total_revenue`
    },
    
    aggregate_count: {
        name: "5. Count Products",
        code: `load products
aggregate count(*) as total_products`
    },
    
    aggregate_avg: {
        name: "6. Average Salary",
        code: `load employees
aggregate avg(salary) as average_salary`
    },
    
    group_by_simple: {
        name: "7. Group by Department",
        code: `load employees
group by department
aggregate count(*) as employee_count`
    },
    
    group_by_revenue: {
        name: "8. Revenue by Category",
        code: `load sales
group by category
aggregate sum(revenue) as total_revenue`
    },
    
    filter_and_select: {
        name: "9. IT Department Salary",
        code: `load employees
filter department = IT
select name, salary, email`
    },
    
    filter_and_sort: {
        name: "10. Senior Employees",
        code: `load employees
filter salary > 50000
select name, salary, department
sort by salary desc`
    },
    
    high_performers: {
        name: "11. High Performers",
        code: `load students
filter marks > 80
select name, marks, gpa
sort by gpa desc
limit 10`
    },
    
    affordable_products: {
        name: "12. Affordable Products",
        code: `load products
filter price < 1000
select name, price, quantity
sort by price asc`
    },
    
    sales_filtering: {
        name: "13. Recent Orders",
        code: `load orders
filter status = completed
select customer, amount
sort by date desc`
    },
    
    customer_locations: {
        name: "14. Customers by City",
        code: `load customers
group by city
aggregate count(*) as city_count`
    },
    
    product_inventory: {
        name: "15. Low Stock Alert",
        code: `load products
filter quantity < 100
select name, quantity, price
sort by quantity asc`
    },
    
    sales_summary: {
        name: "16. Sales Performance",
        code: `load sales
group by product
aggregate sum(revenue) as total_sales, count(*) as total_transactions`
    },
    
    employee_filter: {
        name: "17. Engineering Team",
        code: `load employees
filter department = Engineering
select name, salary, joining_date
sort by salary desc`
    },
    
    email_contacts: {
        name: "18. Student Contacts",
        code: `load students
filter department = CSE
select name, email, phone`
    },
    
    premium_customers: {
        name: "19. VIP Customers",
        code: `load customers
filter country = USA
select name, email, city
sort by name asc
limit 20`
    },
    
    complex_analysis: {
        name: "20. Top Performers Analysis",
        code: `load sales
filter revenue > 10000
group by category
aggregate sum(revenue) as total_revenue, count(*) as transaction_count
sort by total_revenue desc
limit 5`
    }
};

console.log('✓ Examples loaded:', Object.keys(examples).length, 'examples');
