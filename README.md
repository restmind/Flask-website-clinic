# /sign-up, methods - POST 
 Приймає first_name - str,
         last_name - str,
         birth_date - date,
         sex - str,
         email - email,
         password - str,
         phone_number - str,
         chronic_diseases - bool,
         blood_type - str,
         rhesus_factor - str,
         drug_allergy - bool 
 в json форматі.
 Повертає user_id та user_status = user в json форматі.


# /sign-in, methods - POST
 Приймає email - email,
        password - str,
 в json форматі
 Повертає user_id та user_status в json форматі.


# /add-doctor, methods - POST
 Приймає first_name - str,
         last_name - str,
         birth_date - date,
         sex - str,
         email - email,
         password - str,
         phone_number - str,
         department_name - str 
 в json форматі
 Повертає user_id та user_status = doctor в json форматі.


# /get-user/<string:user_id>, methods - GET
 Поле <string:user_id> приймає id користувача
 Повертає first_name - str,
          last_name - str,
          birth_date - date,
          sex - str,
          email - email,
          password - str,
          phone_number - str,
          chronic_diseases - bool,
          blood_type - str,
          rhesus_factor - str,
          drug_allergy - bool
 в json форматі.


# /get-doctor/<string:doctor_id>, methods - GET
 Поле <string:doctor_id> приймає id лікаря
 Повертає first_name - str,
          last_name - str,
          birth_date - date,
          sex - str,
          email - email,
          password - str,
          phone_number - str,
          department_name - str 
 в json форматі.


# /get-doctor-by-department/<string:name>, methods - GET
 Поле <string:name> приймає назву відділу
 Повертає список усіх лікарів в json форматі.
 В кожного лікаря є поля:
 		first_name - str,
        last_name - str,
        birth_date - date,
        sex - str,
        email - email,
        password - str,
        phone_number - str,
        department_name - str


# /timeslot-creations/<string:doc_id>, methods - POST
 Поле <string:doc_id> приймає id лікаря
 Приймає date - data,
         time - time,
         is_open - bool 
 в json форматі.
 Повертає timeslot_id


# /get-open-timeslots/<string:doc_id>/<string:date>, methods - GET
 Поле <string:doc_id> приймає id лікаря, в поле <string:date> приймає дату
 Повертає всі вільні години в день date (поле time - тип str) в json форматі.


# /make-an-appointment/<string:user_id>, methods - POST
 Поле <string:user_id> приймає id користувача
 Приймає department_name - str,
         doctor_id - str,
         date_of_appointment - date,
         time_of_appointment - time,
         format - str,
 в json форматі. 
 Повертає appointment_id


# /get-appointment/<string:patient_id>, methods - GET
 Поле <string:user_id> приймає id пацієнта(користувача)
 Повертає всі записи на прийом користувача у вигляді списку в json форматі.
 В кожного запису є поля:
 		appointment_id - str,
        date_of_appointment - date,
        time_of_appointment - str,
        doctor_id - str
        format - str

# /delete-appointment/<string:appointment_id>, methods - POST
 Поле <string:appointment_id> приймає id запису.
 Якщо запис більше ніж за 2 дні, видаляє запис.
 При успішному виконанні повертає "Result": "successful" в json форматі.


# /add-department, methods - POST
 Приймає name - str в json форматі.
 Повертає department_id


# /get-departments, methods - GET
 Повертає імена та id всіх відділів: department_id - str, name - str
 в json форматі.


# /delete-department/<string:name>, methods - POST
 Поле <string:name> приймає назву відділу.
 Видаляє відділ.
 При успішному виконанні повертає "Result": "successful" в json форматі.


# /doctors-appointments/<string:doctor_id>, methods - GET
 Поле <string:doctor_id> приймає id лікаря.
 Повертає посортований список усіх прийомів лікаря в json форматі.
 В кожного запису є поля:
 		id - str,
        date_of_appointment - date,
        time_of_appointment - str,
        doctor_id - str
        format - str
        patient_id - str


# /get-free-days/<string:doctor_id>, methods - GET
 Поле <string:doctor_id> приймає id лікаря.
 Повертає всі вільні дні лікаря.


# /delete-time-slots, methods - POST
 Видаляє всі недійсні слоти

# /add-to-archive/<string:appointment_id>, methods - POST
 Поле <string:appointment_id> приймає id запису.
 Повертає archive_id