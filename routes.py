import json
import sqlite3
from functools import wraps

from flask import request, jsonify, render_template, redirect, url_for, flash, session
from secrets import randbelow
from passlib.hash import sha256_crypt

#from pip._vendor.urllib3.packages.rfc3986 import validators
from wtforms import Form, StringField, TextAreaField, PasswordField, DateField, BooleanField, SelectField, validators

from api import app, db
from models import *


def generate_id():
    return str(randbelow(1000000)) + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

@app.route("/")
def index():
    return render_template("index.html")


# Register Form Class
class RegisterForm(Form):
    first_name = StringField('First name', [validators.Length(min=1, max=50)])
    last_name = StringField('Last name', [validators.Length(min=1, max=50)])
    birth_date = DateField('Birth date', format='%Y-%m-%d')
    sex = StringField('Sex', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    phone_number = StringField('Phone number', [validators.Length(min=1, max=50)])
    chronic_diseases = BooleanField("Chronic diseases")
    blood_type = SelectField("Blood type", choices=[("1", "I"), ("2", "II"), ("3", "III"), ("4", "IV")])
    rhesus_factor = SelectField("Rhesus factor", choices=[("+", "+"), ("-", "-")])
    drug_allergy = BooleanField("Drug allergy")


# User Register
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            id=generate_id(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            birth_date=form.birth_date.data,
            sex=form.sex.data,
            email=form.email.data,
            password=form.password.data,
            phone_number=form.phone_number.data,
            chronic_diseases=form.chronic_diseases.data,
            blood_type=form.blood_type.data,
            rhesus_factor=form.rhesus_factor.data,
            drug_allergy=form.drug_allergy.data)
        if User.query.filter_by(email=user.email).first() is None:
            try:
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('sign_in'))
            except Exception as err:
                db.session.rollback()
                result = {"ErrorMessage": "{}".format(err)}
                return jsonify(result), 403
        else:
            result = {"ErrorMessage": "email already in db"}
            return jsonify(result), 403
    else:
        return render_template('sign_up.html', form=form)


@app.route("/sign-in", methods=['POST', 'GET'])
def sign_in():
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']

        # Create cursor
        con = sqlite3.connect('clinic.db')
        cur = con.cursor()

        # Get user by username
        user = cur.execute("SELECT * FROM user WHERE email = ?", [email]).fetchone()

        if user is None:
            doctor = cur.execute("SELECT * FROM doctor WHERE email = ?", [email]).fetchone()
            # Close connection
            cur.close()
            if doctor is not None:
                if doctor[6] == password_candidate:
                    session['logged_in'] = True
                    session['id'] = doctor[0]
                    session['status'] = "doctor"
                    flash('You are now logged in', 'success')
                    return redirect(url_for('dashboard', status=session['status'], user_id=session['id']))
                else:
                    error = 'Invalid password'
                    return render_template('sign_in.html', error=error)
            else:
                error = 'Account is not found'
                return render_template('sign_in.html', error=error)       
        elif user[6] == password_candidate:
            session['logged_in'] = True
            session['id'] = user[0]
            session['status'] = "user"
            flash('You are now logged in', 'success')
            return redirect(url_for('dashboard', status=session['status'], user_id=session['id']))
        elif password_candidate != user[6]:
            error = 'Invalid password'
            return render_template('sign_in.html', error=error)




    else:
        return render_template("sign_in.html")


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('sign_in'))
    return wrap


# Dashboard
@app.route('/dashboard/<string:status>/<string:user_id>')
@is_logged_in
def dashboard(status, user_id):
    if status == "user":
        user = User.query.get(user_id)
        return render_template('dashboard.html', user=user)


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))


@app.route("/add-doctor", methods=['POST'])
def add_doctor():
    if request.method == 'POST':
        req_data = request.data
        try:
            data1 = json.loads(req_data.decode('utf-8'))  # Тут перетворення з b{} в {}
            data = DoctorSchema().load(data1)  # тут валідація
        except ValidationError as err:
            return jsonify({"ErrorMessage": "{0}".format(err.messages)})
        if Departments.query.filter_by(name=data['department_name']).first is not None:
            doctor = Doctor(
                id=generate_id(),
                first_name=data['first_name'],
                last_name=data['last_name'],
                birth_date=data['birth_date'],
                sex=data['sex'],
                email=data['email'],
                password=data['password'],
                phone_number=data['phone_number'],
                department_name=data['department_name'])
        else:
            return jsonify({"ErrorMessage": "invalid department_name"})
        if Doctor.query.filter_by(email=doctor.email).first() is None:
            try:
                db.session.add(doctor)
                db.session.commit()
                return jsonify({"user_id": doctor.id,
                               "user_status": "doctor"})
            except Exception as err:
                db.session.rollback()
                result = {"ErrorMessage": "{}".format(err)}
                return jsonify(result), 403
        else:
            result = {"ErrorMessage": "email already in db"}
            return jsonify(result), 403


@app.route("/get-user/<string:user_id>", methods=['GET'])
def get_user_by_id(user_id):
    if request.method == 'GET':
        user = User.query.get(user_id)
        if user is None:
            result = {"ErrorMessage": "Invalid id"}
            return jsonify(result), 400
        else:
            result = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "birth_date": user.birth_date,
                "sex": user.sex,
                "email": user.email,
                "password": user.password,
                "phone_number": user.phone_number,
                "chronic_diseases": user.chronic_diseases,
                "blood_type": user.blood_type,
                "rhesus_factor": user.rhesus_factor,
                "drug_allergy": user.drug_allergy
                }
            return jsonify(result)


@app.route("/get-doctor/<string:doctor_id>", methods=['GET'])
def get_doctor_by_id(doctor_id):
    if request.method == 'GET':
        doctor = Doctor.query.get(doctor_id)
        if doctor is None:
            result = {"ErrorMessage": "Invalid id"}
            return jsonify(result), 400
        else:
            result = {
                "first_name": doctor.first_name,
                "last_name": doctor.last_name,
                "birth_date": doctor.birth_date,
                "sex": doctor.sex,
                "email": doctor.email,
                "password": doctor.password,
                "phone_number": doctor.phone_number,
                "department_name": doctor.department_name
                }
            return jsonify(result)


@app.route("/get-doctor-by-department/<string:name>", methods=['GET'])
def get_doctor_by_department(name):
    if request.method == 'GET':
        doctor = Doctor.query.filter_by(department_name=name.title()).all()
        if doctor is None:
            result = {"ErrorMessage": "Invalid name"}
            return jsonify(result), 400
        else:
            doctors = []
            for doc in doctor:
                doctors.append({"id": doc.id,
                                "first_name": doc.first_name,
                                "last_name": doc.last_name,
                                "birth_date": doc.birth_date,
                                "sex": doc.sex,
                                "email": doc.email,
                                "password": doc.password,
                                "phone_number": doc.phone_number,
                                "department_name": doc.department_name
                                })
            return jsonify(doctors)


@app.route("/timeslot-creations/<string:doc_id>", methods=['POST'])
def timeslot_creations(doc_id):
    if Doctor.query.get(doc_id) is not None:
        if request.method == "POST":
            req_data = request.data
            try:
                data1 = json.loads(req_data.decode('utf-8'))  # Тут перетворення з b{} в {}
                data = TimeSlotsSchema().load(data1)  # тут валідація
            except ValidationError as err:
                return jsonify({"ErrorMessage": "{0}".format(err.messages)})
            timeslot = TimeSlots(
                id=generate_id(),
                doctor_id=doc_id,
                date=data['date'],
                time=data['time'],
                is_open=data['is_open']
            )
            if TimeSlots.query.filter_by(date=timeslot.date, time=timeslot.time).first() is None:
                try:
                    db.session.add(timeslot)
                    db.session.commit()
                    return jsonify({"timeslot_id": timeslot.id})
                except Exception as err:
                    db.session.rollback()
                    result = {"ErrorMessage": "{}".format(err)}
                    return jsonify(result), 403
            else:
                result = {"ErrorMessage": "Timeslot already in db"}
                return jsonify(result), 403
    else:
        result = {"ErrorMessage": "Invalid doctorId"}
        return jsonify(result), 400


@app.route("/get-open-timeslots/<string:doc_id>/<string:date>", methods=['GET'])
def get_open_timeslots(doc_id, date):
    if request.method == "GET":
        timeslots = TimeSlots.query.filter_by(date=datetime.datetime.strptime(date, '%Y-%m-%d').date(),
                                              doctor_id=doc_id, is_open=True).group_by(TimeSlots.time).all()
        result = []
        for timeslot in timeslots:
            result.append(str(timeslot.time))
        return jsonify(result)


@app.route("/make-an-appointment/<string:user_id>", methods=['POST'])
def make_an_appointment(user_id):
    if User.query.get(user_id) is not None:
        if request.method == 'POST':
            req_data = request.data
            try:
                data1 = json.loads(req_data.decode('utf-8'))  # Тут перетворення з b{} в {}
                data = AppointmentSchema().load(data1)  # тут валідація
            except ValidationError as err:
                return jsonify({"ErrorMessage": "{0}".format(err.messages)})
            if Departments.query.filter_by(name=data['department_name']).first is not None:
                appointment = Appointment(id=generate_id(),
                                          department_name=data['department_name'],
                                          doctor_id=data['doctor_id'],
                                          patient_id=user_id,
                                          date_of_appointment=data['date_of_appointment'],
                                          time_of_appointment=data['time_of_appointment'],
                                          format=data['format'])
            else:
                return jsonify({"ErrorMessage": "invalid department_name"})
            timeslot = TimeSlots.query.filter_by(date=appointment.date_of_appointment, doctor_id=appointment.doctor_id,
                                                 time=appointment.time_of_appointment).first()
            if timeslot.is_open == 1:
                try:
                    db.session.add(appointment)
                    db.session.query(TimeSlots).filter_by(id=timeslot.id).update({"is_open": False})
                    db.session.commit()
                    return jsonify({"appointment_id": appointment.id})
                except Exception as err:
                    db.session.rollback()
                    result = {"ErrorMessage": "{}".format(err)}
                    return jsonify(result), 403
            else:
                result = {"ErrorMessage": "Timeslot is not open"}
                return jsonify(result), 400
    else:
        result = {"ErrorMessage": "Invalid userId"}
        return jsonify(result), 400


@app.route("/get-appointment/<string:patient_id>", methods=["GET"])
def get_appointment(patient_id):
    if request.method == 'GET':
        appointments = Appointment.query.filter_by(patient_id=patient_id).all()
        if appointments:
            result = []
            for appointment in appointments:
                result.append({"appointment_id": appointment.id,
                               "date_of_appointment": appointment.date_of_appointment,
                               "time_of_appointment": str(appointment.time_of_appointment),
                               "doctor_id": appointment.doctor_id,
                               "format": appointment.format})
            return jsonify(result)
        else:
            result = {"ErrorMessage": "invalid patient id"}
            return jsonify(result), 400


@app.route("/delete-appointment/<string:appointment_id>", methods=['POST'])
def delete_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if appointment is not None:
        timeslot = TimeSlots.query.filter_by(date=appointment.date_of_appointment, doctor_id=appointment.doctor_id,
                                             time=appointment.time_of_appointment).first()
        if datetime.date.today() + datetime.timedelta(2) < timeslot.date:
            try:
                db.session.delete(appointment)
                db.session.query(TimeSlots).filter_by(id=timeslot.id).update({"is_open": True})
                db.session.commit()
                return jsonify({"Result": "successful"})
            except Exception as err:
                db.session.rollback()
                result = {"ErrorMessage": "{}".format(err)}
                return jsonify(result), 403
        else:
            result = {"ErrorMessage": "invalid date now"}
            return jsonify(result), 400
    else:
        result = {"ErrorMessage": "invalid appointment id"}
        return jsonify(result), 400


@app.route("/add-department", methods=['POST'])
def add_department():
    if request.method == 'POST':
        req_data = request.data
        try:
            data1 = json.loads(req_data.decode('utf-8'))
            data = DepartmentsSchema().load(data1)
        except ValidationError as err:
            return jsonify({"ErrorMessage": "{0}".format(err.messages)})
        department = Departments(id=generate_id(), name=data['name'].title())
        if Departments.query.filter_by(name=department.name).first() is None:
            try:
                db.session.add(department)
                db.session.commit()
                return jsonify({"department_id": department.id})
            except Exception as err:
                db.session.rollback()
                result = {"ErrorMessage": "{}".format(err)}
                return jsonify(result), 403
        else:
            result = {"ErrorMessage": "Department already in db"}
            return jsonify(result), 403


@app.route("/get-departments", methods=['GET'])
def get_departments():
    if request.method == 'GET':
        departments = Departments.query.all()
        results = []
        for department in departments:
            results.append({"department_id": department.id,
                            "name": department.name})
        return jsonify(results)


@app.route("/delete-department/<string:name>", methods=['POST'])
def delete_department(name):
    if request.method == 'POST':
        department = Departments.query.filter_by(name=name).first()
        if department is not None:
            try:
                db.session.delete(department)
                db.session.commit()
                return jsonify({"Result": "successful"})
            except Exception as err:
                db.session.rollback()
                result = {"ErrorMessage": "{}".format(err)}
                return jsonify(result), 403
        else:
            result = {"ErrorMessage": "invalid name"}
            return jsonify(result), 400


@app.route("/doctors-appointments/<string:doctor_id>", methods=['GET'])
def doctors_appointments(doctor_id):
    if request.method == "GET":
        appointments = db.session.query(Appointment).filter_by(doctor_id=doctor_id).\
            group_by(Appointment.date_of_appointment).group_by(Appointment.time_of_appointment).all()
        if appointments:
            result = []
            for appointment in appointments:
                result.append({"time_of_appointment": str(appointment.time_of_appointment),
                               "date_of_appointment": appointment.date_of_appointment,
                               "patient_id": appointment.patient_id,
                               "id": appointment.id,
                               "format": appointment.format,
                               "department_name": appointment.department_name})
            return jsonify(result)
        else:
            result = {"ErrorMessage": "invalid id"}
            return jsonify(result), 400


@app.route("/get-free-days/<string:doctor_id>", methods=["GET"])
def get_free_days(doctor_id):
    if request.method == "GET":
        days = TimeSlots.query.filter_by(doctor_id=doctor_id).group_by(TimeSlots.date).all()
        if days:
            result = set()
            for day in days:
                if day.is_open:
                    result.add(day.date)
            return jsonify(sorted(list(result)))
        else:
            return jsonify([]), 200


@app.route("/delete-time-slots", methods=['POST'])
def delete_time_slots():
    if request.method == "POST":
        slots = TimeSlots.query.all()
        result = []
        for slot in slots:
            if slot.date < datetime.date.today():
                result.append(slot)
            if slot.date == datetime.date.today() and str(slot.time) < datetime.datetime.now().strftime("%H:%M"):
                result.append(slot)
        for i in result:
            try:
                db.session.delete(i)
            except Exception as err:
                db.session.rollback()
                result = {"ErrorMessage": "{}".format(err)}
                return jsonify(result), 403
        try:
            db.session.commit()
            return jsonify({"Result": "successful"})
        except Exception as err:
            db.session.rollback()
            result = {"ErrorMessage": "{}".format(err)}
            return jsonify(result), 403


@app.route("/add-to-archive/<string:appointment_id>", methods=['POST'])
def add_to_archive(appointment_id):
    if request.method == "POST":
        appointment = Appointment.query.get(appointment_id)
        if appointment is not None:
            archive = Archive(id=generate_id(),
                              department_name=appointment.department_name,
                              doctor_id=appointment.doctor_id,
                              patient_id=appointment.patient_id,
                              date_of_appointment=appointment.date_of_appointment,
                              time_of_appointment=appointment.time_of_appointment,
                              format=appointment.format)
            try:
                db.session.add(archive)
                db.session.delete(appointment)
                db.session.commit()
                return jsonify({"archive_id": archive.id})
            except Exception as err:
                db.session.rollback()
                result = {"ErrorMessage": "{}".format(err)}
                return jsonify(result), 403
        else:
            result = {"ErrorMessage": "invalid appointment id"}
            return jsonify(result), 403