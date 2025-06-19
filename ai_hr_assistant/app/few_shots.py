few_shots = [
    {
        'Question': "How many male employees do we have?",
        'SQLQuery': "SELECT COUNT(*) FROM employee WHERE gender = 'Male';",
        'SQLResult': "2",
        'Answer': "There are 2 male employees."
    },
    {
        'Question': "Which employee has an annual leave request starting soon?",
        'SQLQuery': (
            "SELECT employee.first_name, employee.last_name, leave_requests.start_date "
            "FROM leave_requests "
            "JOIN employee ON leave_requests.employee_id = employee.id "
            "WHERE leave_requests.leave_type = 'Annual' "
            "AND leave_requests.status = 'Pending' "
            "ORDER BY leave_requests.start_date ASC "
            "LIMIT 1;"
        ),
        'SQLResult': "('Cristiano', 'Ronaldo', '2025-07-01')",
        'Answer': "Cristiano Ronaldo has an annual leave request starting on 2025-07-01."
    },
    {
        'Question': "If Cristiano goes on leave, how many people will be left in his department and what are their positions?",
        'SQLQuery': (
            "SELECT emp_position, COUNT(*) AS number_of_employees "
            "FROM employee e "
            "WHERE e.emp_department = (SELECT emp_department FROM employee WHERE first_name = 'Cristiano' LIMIT 1) "
            "AND e.first_name <> 'Cristiano' "
            "GROUP BY emp_position;"
        ),
        'SQLResult': "[('Senior Software Engineer', 1)]",
        'Answer': "There will be 1 person left in Cristiano's department, and their position is Senior Software Engineer."
    },
    {
        'Question': "If everyone in Cristiano department goes on leave for a week, how many days of leave will they have left?",
        'SQLQuery': (
            "SELECT first_name, last_name, "
            "CASE WHEN emp_leave_balance - 7 < 0 THEN 0 ELSE emp_leave_balance - 7 END AS leave_balance_after_week "
            "FROM employee "
            "WHERE emp_department = (SELECT emp_department FROM employee WHERE first_name = 'Cristiano' LIMIT 1);"
        ),
        'SQLResult': "[('John', 'Doe', 3), ('Jane', 'Smith', 5)]",
        'Answer': "The remaining leave balance for employees in Cristiano's department after taking a week of leave is 3 and 5 days."
    },
    {
        'Question': (
            "Show the most recent employee who requested leave with pending or approved status, "
            "are they currently active, when do they plan to return from leave, how long are they staying, and their positions."
        ),
        'SQLQuery': (
            "SELECT e.first_name, e.last_name, e.emp_status, l.end_date, l.days_requested, e.emp_position "
            "FROM employee e "
            "JOIN leave_requests l ON e.id = l.employee_id "
            "WHERE l.status IN ('Pending', 'Approved') "
            "ORDER BY l.start_date DESC "
            "LIMIT 1;"
        ),
        'SQLResult': "('Cristiano', 'Ronaldo', 'Active', '2025-07-05', 5, 'Software Engineer')",
        'Answer': (
            "The most recent employee who requested leave with pending or approved status is currently active, "
            "their leave ends on 2025-07-05, they are staying for 5 days, and their position is Software Engineer."
        )
    }
]
