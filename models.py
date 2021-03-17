import datetime

from marshmallow import Schema, fields, validates, ValidationError

from api import db


class User(db.Model):
    __tablename__ = "User"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.String(45), primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    sex = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(45), nullable=False)
    password = db.Column(db.String(45), nullable=False)
    phone_number = db.Column(db.String(45), nullable=False)
    chronic_diseases = db.Column(db.Boolean, nullable=False)
    blood_type = db.Column(db.String(45), nullable=False)
    rhesus_factor = db.Column(db.String(45), nullable=False)
    drug_allergy = db.Column(db.Boolean, nullable=False)


class UserSchema(Schema):
    id = fields.String(required=False)
    first_name = fields.String(required=False)
    last_name = fields.String(required=False)
    birth_date = fields.Date(required=False)
    sex = fields.String(required=False)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    phone_number = fields.String(required=False)
    chronic_diseases = fields.Boolean(required=False)
    blood_type = fields.String(required=False)
    rhesus_factor = fields.String(required=False)
    drug_allergy = fields.Boolean(required=False)


class Doctor(db.Model):
    __tablename__ = "Doctor"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.String(45), primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    sex = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(45), nullable=False)
    password = db.Column(db.String(45), nullable=False)
    phone_number = db.Column(db.String(45), nullable=False)
    department_name = db.Column(db.String(45), nullable=False)


class DoctorSchema(Schema):
    id = fields.String(required=False)
    first_name = fields.String(required=False)
    last_name = fields.String(required=False)
    birth_date = fields.Date(required=False)
    sex = fields.String(required=False)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    phone_number = fields.String(required=False)
    department_name = fields.String(required=False)


class Appointment(db.Model):
    __tablename__ = "Appointment"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.String(45), primary_key=True)
    department_name = db.Column(db.String(45), nullable=False)
    doctor_id = db.Column(db.String(45), nullable=False)
    patient_id = db.Column(db.String(45), nullable=False)
    date_of_appointment = db.Column(db.Date, nullable=False)
    time_of_appointment = db.Column(db.Time, nullable=False)
    format = db.Column(db.String(45), nullable=False)


class AppointmentSchema(Schema):
    id = fields.String(required=False)
    department_name = fields.String(required=False)
    doctor_id = fields.String(required=False)
    patient_id = fields.String(required=False)
    date_of_appointment = fields.Date(required=False)
    time_of_appointment = fields.Time(required=False)
    format = fields.String(required=False)


class TimeSlots(db.Model):
    __tablename__ = "TimeSlots"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.String(45), primary_key=True)
    doctor_id = db.Column(db.String(45), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    is_open = db.Column(db.Boolean, nullable=False)


class TimeSlotsSchema(Schema):
    id = fields.String(required=False)
    doctor_id = fields.String(required=False)
    date = fields.Date(required=False)
    time = fields.Time(required=False)
    is_open = fields.Boolean(required=False)

    @validates("date")
    def validate_date(self, value):

        if value < datetime.date.today():
            raise ValidationError("invalid date")


class Departments(db.Model):
    __tablename__ = "Departments"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.String(45), primary_key=True)
    name = db.Column(db.String(45), nullable=False)


class DepartmentsSchema(Schema):
    id = fields.String(required=False)
    name = fields.String(required=False)


class Archive(db.Model):
    __tablename__ = "Archive"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.String(45), primary_key=True)
    department_name = db.Column(db.String(45), nullable=False)
    doctor_id = db.Column(db.String(45), nullable=False)
    patient_id = db.Column(db.String(45), nullable=False)
    date_of_appointment = db.Column(db.Date, nullable=False)
    time_of_appointment = db.Column(db.Time, nullable=False)
    format = db.Column(db.String(45), nullable=False)


class ArchiveSchema(Schema):
    id = fields.String(required=False)
    department_name = fields.String(required=False)
    doctor_id = fields.String(required=False)
    patient_id = fields.String(required=False)
    date_of_appointment = fields.Date(required=False)
    time_of_appointment = fields.Time(required=False)
    format = fields.String(required=False)