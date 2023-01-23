from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import uuid


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and current Patient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    """
    TODO: Part 1
    """
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the Patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username) 


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False



def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    # check 1: if someone's already logged-in
    global current_patient
    global current_caregiver

    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return

    # check 2: the length for tokens need to be exactly 1 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    date_tokens = date.split("-")

    
    search_cg_query = "SELECT DISTINCT Username FROM Availabilities WHERE Time = %s ORDER BY Username"
    search_vc_query = "SELECT * FROM Vaccines ORDER BY name"

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    
    try:
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])
        d = datetime.datetime(year, month, day)
        
        print("...................................")
        print("For", date, "These are the Available Caregivers")
        
        cursor.execute(search_cg_query, d)
        for row in cursor:
            print(row[0])
        
        print("...................................")
        print("And These are the Available Vaccines")
        print("Vaccine |  Dose")
        
        cursor.execute(search_vc_query)
        for row in cursor:
            print(row[0], row[1], 'Doses')
        
        print("...................................")
    except pymssql.Error:
        print("Error occured Please try again!")
    except ValueError:
        print("Please enter a valid date! DATE should be in MM-DD-YYYY Format")
    except Exception as e:
        print("Error occured Please try again!")       
    finally:
        print("Thanks")
        cm.close_connection()
        return
    

def reserve(tokens):
    """
    TODO: Part 2
    """
    global current_patient
    global current_caregiver

    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return    
    elif current_patient is None:
        print("Please login as a patient first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again! Querry Missing information")
        print("Please input both the date and vacccine")
        return

    # Initializes the Data    
    date = tokens[1]
    vaccine = tokens[2]
    date_tokens = date.split("-")

    # Checks if Data is Valid
    try:
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])
        d = datetime.datetime(year, month, day)
    except ValueError:
        print("Please enter a valid date! DATE should be in MM-DD-YYYY Format")
        return                                      
    except Exception as e:
        print("Error occured Please try again!")  
    
    # Establishes Connection with Server
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    
    # Checks to Make Sure Enouph Doses Available 
    search_vc_query = "SELECT * FROM Vaccines WHERE name = %s"
    try:
        vaccine_found = []
        cursor.execute(search_vc_query, vaccine)
        vaccine_found = cursor.fetchall()
        
        if vaccine_found:
            if int(vaccine_found[0][1]) == 0:
                print('Not enough available doses!')
                cm.close_connection()
                return
        else:
            print('Vaccine Not Found, Please Try Again')
            cm.close_connection()
            return
    except pymssql.Error:
        print("Error occured Please try again!")
        cm.close_connection()
        return
    except Exception as e:
        print("Error occured Please try again!")
        cm.close_connection()
        return      

    
    # Checks to Ensure CG Available 
    
    find_free_caregivers = """
        SELECT Time, Username as Caregiver
        FROM Availabilities 
        WHERE Time = %s
        EXCEPT 
        SELECT Time, Caregiver 
        FROM APPOINTMENT 
        WHERE Time = %s
        ORDER BY Caregiver;
    """ 
    drop_caregiver_avb = 'DELETE FROM Availabilities WHERE Username = %s AND Time = %s;'
    reduce_vaccine = 'UPDATE Vaccines SET Doses = Doses - 1 WHERE Name = %s;'
    add_reservation = 'Insert INTO APPOINTMENT VALUES (%d, %s, %s, %s, %s);'
    free_caregivers = []
    
    try:
        cursor.execute(find_free_caregivers, (d,d))
        free_caregivers = cursor.fetchall()
        
        if not free_caregivers:
            print('No Caregiver is available! Please Select Another Date')
            cm.close_connection()
            return

        # At the point we have verified that there are both Vaccines and Caregivers Available
        
        # Assign Caregiver
        caregiver_assigned = free_caregivers[0][1]
        # Generate unique ID
        new_apid = int(str(uuid.uuid4().int)[0:9])
        
        # Add appointment
        Patient_username = current_patient.get_username()
        cursor.execute(add_reservation, (new_apid, Patient_username, vaccine, d, caregiver_assigned))
        
        # remove caregiver from availability
        cursor.execute(drop_caregiver_avb, (caregiver_assigned,d))

        # reduce vaccine stock
        cursor.execute(reduce_vaccine, vaccine)
        
    except pymssql.Error:
        print("Error occured Please try again!")
    except Exception as e:
        print("Error occured Please try again!")
    else:
        try:
            conn.commit()
        except pymssql.Error:
            print("Error occured Saving Appointment Please try again!")
            cm.close_connection()
            return
        except Exception as e:
            print("Error occured Saving Appointment Please try again!")
            cm.close_connection()
            return

        print('Your Appointment Has Been Booked For The', date, '| You will be given the', vaccine, 'Vaccine' )
        print('...............................................................................................')
        print('Appointment ID:', new_apid, ',', 'Caregiver username:', caregiver_assigned)
        print('...............................................................................................')
    finally:
        cm.close_connection()
        print("Thanks")
        return


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    global current_patient
    global current_caregiver

    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    
    if len(tokens) != 2:
        print("Please try again!")
        return

    apid = tokens[1]
    retrive_appointment = 'SELECT APID, Vaccine, Time, Caregiver, Patient FROM APPOINTMENT WHERE APID = %d;'
    drop_app = 'DELETE FROM APPOINTMENT WHERE APID = %d;' 
    addback_avb = 'Insert INTO Availabilities VALUES(%s, %s);'
    update_vaccine = 'UPDATE Vaccines SET Doses = Doses + 1 WHERE Name = %s;'

    # Establishes Connection with Server
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    try:
        retrived_appointment = []
        cursor.execute(retrive_appointment, apid)
        retrived_appointment = cursor.fetchall()

        if not retrived_appointment:
            print('Appointment Not Found Please Check Appointment ID and Try Again')
            cm.close_connection()
            return      

        vaccine = retrived_appointment[0][1]
        date = retrived_appointment[0][2]
        cg_asigned = retrived_appointment[0][3]
        schd_patient = retrived_appointment[0][4]

        cursor.execute(drop_app, apid)
        cursor.execute(addback_avb, (date, cg_asigned))
        cursor.execute(update_vaccine, vaccine)
    except pymssql.Error:
        print("Error occured Please try again!")
    except Exception as e:
        print("Error occured Please try again!")
    else:
        try:
            conn.commit()
        except pymssql.Error:
            print("Error occured Saving Appointment Please try again!")
            cm.close_connection()
            return
        except Exception as e:
            print("Error occured Saving Appointment Please try again!")
            cm.close_connection()
            return
        
        print('The Following Appointment For', schd_patient, 'Has Been Cannceled')
        print('.................................................................')
        print(' Appointment ID | Vaccine name | Date | Caregiver | Patient name ')
        print('.................................................................')
        print(' ', apid, vaccine, date, cg_asigned, schd_patient )
        print('.................................................................')

    finally:
        cm.close_connection()
        print("Thanks")
        return      


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    global current_patient
    global current_caregiver

    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    elif current_caregiver is not None:
        
        current_user = current_caregiver.get_username()
        
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        try:
            search_vc_query = "SELECT APID, Vaccine, Time, Patient FROM APPOINTMENT WHERE Caregiver = %s ORDER BY APID"
            print("For", current_user, "These are your Appoitments")
            print('appointment ID | Vaccine name | Date | Patient name')
            print('...................................................')
            
            cursor.execute(search_vc_query, current_user)
            for row in cursor:
                print(row[0], row[1], row[2], row[3])            
            print('...................................................')

        except pymssql.Error:
            print("SQL Error occured Please try again!")
        except Exception as e:
            print("Error occured Please try again!")       
        finally:
            print("Thanks")
            cm.close_connection()
            return                                              
    elif current_patient is not None:
        
        current_user = current_patient.get_username()
        
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        try:
            search_vc_query = "SELECT APID, Vaccine, Time, Caregiver FROM APPOINTMENT WHERE Patient = %s ORDER BY APID"
            print("For", current_user, "These are your Appoitments")
            print('appointment ID | Vaccine name | Date | Caregiver name')
            print('.....................................................')
            cursor.execute(search_vc_query, current_user)
            for row in cursor:
                print(row[0], row[1], row[2], row[3])            
            print('.....................................................')

        except pymssql.Error:
            print("Error occured Please try again!")
        except Exception as e:
            print("Error occured Please try again!")       
        finally:
            print("Thanks")
            cm.close_connection()
            return                                             
    else:
        print("Error occured Please try again!")
        return


def logout(tokens):
    """
    TODO: Part 2
    """
    global current_patient
    global current_caregiver
    
    try:
        if current_patient is None and current_caregiver is None:
            print("Please login first")
            return
        current_patient = None
        current_caregiver = None
    except Exception as e:
        print('Error occured Please try again!')   
        return  

    if current_patient is None and current_caregiver is None:
        print("Successfully logged out!")
    else:
        print('Please try again!')
    return

def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == 'cancel':
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()