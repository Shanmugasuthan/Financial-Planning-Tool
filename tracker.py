import PySimpleGUI as sg
import mysql.connector as msc
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import PyPDF2
import fitz


# Function to insert user data into the database
def insert_into_database(name,username, age, ph_no, salary, debt, liabilities, choice, connection):
    try:
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # SQL query to insert user data into the "budget_py" table
        insert_query = "INSERT INTO budget_py (name,username, age, ph_no, salary, debt, liabilities, choice) " \
                       "VALUES (%s,%s, %s, %s, %s, %s, %s, %s)"
        data = (name,username, age, ph_no, salary, debt, liabilities, choice)

        # Execute the SQL query
        cursor.execute(insert_query, data)

        # Commit the changes to the database
        connection.commit()
        print("Data inserted successfully!")

        # Close the cursor (connection will be closed externally)
        cursor.close()

    except mysql.connector.Error as err:
        sg.popup_error(f"Error: {err}")

def get_user_input():

    layout = [
        [sg.Text("Enter your name:"), sg.InputText(key="name")],
        [sg.Text("Enter your username:"), sg.InputText(key="username")],
        [sg.Text("Enter your age:"), sg.InputText(key="age")],
        [sg.Text("Enter your phone number:"), sg.InputText(key="ph_no")],
        [sg.Text("Enter your salary:"), sg.InputText(key="salary")],
        [sg.Text("Enter your debt:"), sg.InputText(key="debt")],
        [sg.Text("Enter your liabilities worth:"), sg.InputText(key="liabilities")],
        [sg.Button("Submit")]
    ]

    window = sg.Window("BUDGET PLAN CALCULATOR", layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        if event == "Submit":
            # Check if any input field is empty
            if any(values[key] == "" for key in ["name","username", "age", "ph_no", "salary", "debt", "liabilities"]):
                sg.popup_error("Please enter all required details")
                continue
            values["username"]=values["username"].lower()    

            ph_no = values["ph_no"]
            while len(ph_no) != 10:
                sg.popup_error("Please enter a valid phone number (10 digits)")
                event, values = window.read()
                ph_no = values["ph_no"]

            try:
                
                salary = float(values["salary"])
                if salary < 0:
                    sg.popup_error("Salary cannot be lesser than zero")
                    continue  # Restart the loop to allow the user to enter a valid salary

                age = int(values["age"])
                if age <= 0:
                    sg.popup_error("Please enter a valid age")
                    continue  # Restart the loop to allow the user to enter a valid salary


                debt = float(values["debt"])
                if debt < 0:
                     sg.popup_error("debt cannot be lesser than zero")
                     continue  # Restart the loop to allow the user to enter a valid salary
                
            
                liabilities = float(values["liabilities"])
                if liabilities < 0:
                     sg.popup_error("liabilities cannot be lesser than zero")
                     continue  # Restart the loop to allow the user to enter a valid salary
                

                window.close()
                return values["name"],values["username"], age, ph_no, salary, debt, liabilities
            except ValueError:
                sg.popup_error("Invalid input. Please enter valid numeric values.")

    window.close()

def display_plans():

    sg.popup("\nPlease choose a Financial Plan from below:",
             "1. Aggressive Investment Plan",
             "2. Balanced Investment Plan",
             "3. Conservative Investment Plan",
             "4. Debt Repayment Plan",
             "5. Emergency Fund Plan")

def choose_plan():

    layout = [
        [sg.Text("Enter your choice (1-5):"), sg.InputText(key="choice")],
        [sg.Button("Submit")]
    ]

    window = sg.Window("Choose Plan", layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        if event == "Submit":
            try:
                choice = int(values["choice"])
                if 1 <= choice <= 5:
                    window.close()
                    return choice
                else:
                    sg.popup_error("Invalid choice. Please enter a number between 1 and 5.")
            except ValueError:
                sg.popup_error("Invalid input. Please enter a valid numeric value.")

    window.close()

def calculate_plans(salary, debt, liabilities, choice):

    plans = {
        1: {"Investment": 0.4 * salary, "Household Expenses": 0.5 * salary, "Entertainment": 0.05 * salary,
            "Savings": 0.05 * salary},

        2: {"Investment": 0.3 * salary, "Household Expenses": 0.5 * salary, "Entertainment": 0.05 * salary,
            "Savings": 0.15 * salary},

        3: {"Investment": 0.18 * salary, "Household Expenses": 0.5 * salary, "Entertainment": 0.15 * salary,
            "Savings": 0.17 * salary},

        4: {"Debt Repayment": debt, "Household Expenses": 0.5 * salary, "Entertainment": 0.01 * salary,
            "Repay debt": 0.2 * salary},

        5: {"Available emergency Fund of minimum ": (0.5 * liabilities + 0.5 * salary),
            " to maximum of ": (liabilities  + 0.5 * salary), "Household Expenses": 0.35 * salary,
            "Entertainment": 0.05 * salary, "Savings": 0.3 * salary}
    }

    return plans.get(choice, "Invalid choice. Please choose between 1-5.")



def retrieve_data_by_username(username, connection):
    try:
        cursor = connection.cursor()
        select_query = "SELECT * FROM budget_py WHERE username = %s"
        cursor.execute(select_query, (username,))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data:
            return user_data
        else:
            sg.popup_error("No data found for the entered username.")
            return None
    except msc.Error as err:
        sg.popup_error(f"Error: {err}")
        return None



def display_data(user_data):
    # Display the retrieved data or handle it as per your requirements
    print(user_data)
    
    
def save_data_to_pdf(user_data):
    pdf_filename = "user_data.pdf"

    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.drawString(100, 750, "Retrieved User Data:")

    y_position = 730
    for key, value in enumerate(user_data):
        c.drawString(100, y_position - (key * 20), f"{key}: {value}")

    c.save()
    sg.popup(f"PDF file '{pdf_filename}' generated successfully.")

    return pdf_filename

def display_pdf(pdf_filename):
    pdf_images = pdf_to_images(pdf_filename)

    layout = [
        [sg.Image(data=image_data, size=(300, 300))] for image_data in pdf_images
    ]
    window = sg.Window("PDF Viewer", layout, finalize=True)

    while True:
        event, _ = window.read()

        if event == sg.WINDOW_CLOSED:
            break
def pdf_to_images(pdf_filename):
    images = []
    pdf_document = fitz.open(pdf_filename)
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(alpha=False)
        img_data = pix.tobytes()
        images.append(img_data)
    pdf_document.close()
    return images

def display_pdf(pdf_filename):
    pdf_images = pdf_to_images(pdf_filename)

    layout = [
        [sg.Image(data=image_data)] for image_data in pdf_images
    ]
    window = sg.Window("PDF Viewer", layout, finalize=True)

    while True:
        event, _ = window.read()

        if event == sg.WINDOW_CLOSED:
            break

    window.close()

def main():
    sg.theme("lightblue3")
    sg.popup("Welcome to the BUDGET PLAN CALCULATOR ")

    cnx = msc.connect(user='root', password='Yourpassword',
                          host='###.0.0.#',
                          database='bud_sql',
                          use_pure=False)
    cursor = cnx.cursor()

    #Ask the user whether to enter data or retrieve data
    choice = sg.popup_get_text("Choose an option '1-> Enter Data', '2-> Retrieve Data'", (1, 2))

    if choice == "1":
        # Get user input
        name, username, age, ph_no, salary, debt, liabilities = get_user_input()

        # Display available plans
        display_plans()

        # Choose a plan
        choice = choose_plan()

        # Insert data into the database
        insert_into_database(name, username, age, ph_no, salary, debt, liabilities, choice, cnx)

        # Calculate and display the chosen plan
        plan_details = calculate_plans(salary, debt, liabilities, choice)

        sg.popup(f"\nDear {name}, aged {age}, based on your choice {choice}, here is your financial plan:",
                 "\n".join([f"{category}: Rs.{amount:,.2f}" for category, amount in plan_details.items()]))
        
    if choice == "2":
        # Ask the user for the username
        username = sg.popup_get_text("Enter Username")

        # Retrieve data by username
        user_data = retrieve_data_by_username(username, cnx)

        if user_data:
            # Display the retrieved data
            display_data(user_data)

            # Save the retrieved data to a PDF file
            pdf_filename = save_data_to_pdf(user_data)

            # Display the PDF content within the application
            display_pdf(pdf_filename)

    # Close the database connection
    cursor.close()

main()
