from abc import ABC, abstractmethod
from datetime import datetime
import random
import json
import os

def inr(amount):
    amount = int(amount)
    s = str(abs(amount))
    if len(s) <= 3:
        result = s
    else:
        result = s[-3:]
        s = s[:-3]
        while len(s) > 2:
            result = s[-2:] + "," + result
            s = s[:-2]
        if s:
            result = s + "," + result
    sign = "-" if int(amount) < 0 else ""
    return f"Rs. {sign}{result}"

class Person(ABC):
    def __init__(self, person_id, name, email, contact_number, address):
        self._person_id = person_id
        self._name = name
        self._email = email
        self._contact_number = contact_number
        self._address = address

    @abstractmethod
    def display_details(self):
        pass

    def update_details(self, name=None, email=None, contact_number=None, address=None):
        if name:
            self._name = name
        if email:
            self._email = email
        if contact_number:
            self._contact_number = contact_number
        if address:
            self._address = address

    def __str__(self):
        return f"{self._name} (ID: {self._person_id})"

    def __repr__(self):
        return f"Person(id={self._person_id}, name={self._name})"


class Alumni(Person):
    def __init__(self, person_id, name, email, contact_number, address,
                 alumni_id, batch_year, degree, current_company="N/A", designation="N/A"):
        super().__init__(person_id, name, email, contact_number, address)
        self.alumni_id = alumni_id
        self.batch_year = batch_year
        self.degree = degree
        self.current_company = current_company
        self.designation = designation
        self.registered_events = []
        self.achievements = []

    def display_details(self):
        print(f"""
  ┌─────────────────────────────────────────┐
  │           ALUMNI PROFILE                │
  ├─────────────────────────────────────────┤
  │  ID         : {self.alumni_id:<26}│
  │  Name       : {self._name:<26}│
  │  Email      : {self._email:<26}│
  │  Contact    : {self._contact_number:<26}│
  │  Address    : {self._address:<26}│
  │  Batch Year : {str(self.batch_year):<26}│
  │  Degree     : {self.degree:<26}│
  │  Company    : {self.current_company:<26}│
  │  Designation: {self.designation:<26}│
  └─────────────────────────────────────────┘""")

    def update_employment(self, company, designation):
        self.current_company = company
        self.designation = designation

    def register_for_event(self, event_id):
        if event_id not in self.registered_events:
            self.registered_events.append(event_id)
            return True
        return False

    def view_profile(self):
        self.display_details()

    def to_dict(self):
        return {
            "person_id": self._person_id,
            "name": self._name,
            "email": self._email,
            "contact_number": self._contact_number,
            "address": self._address,
            "alumni_id": self.alumni_id,
            "batch_year": self.batch_year,
            "degree": self.degree,
            "current_company": self.current_company,
            "designation": self.designation,
            "registered_events": self.registered_events,
            "achievements": self.achievements,
        }

    @classmethod
    def from_dict(cls, d):
        obj = cls(
            d["person_id"], d["name"], d["email"],
            d["contact_number"], d["address"],
            d["alumni_id"], d["batch_year"], d["degree"],
            d.get("current_company", "N/A"), d.get("designation", "N/A")
        )
        obj.registered_events = d.get("registered_events", [])
        obj.achievements = d.get("achievements", [])
        return obj

    def __str__(self):
        return f"{self._name} | Batch: {self.batch_year} | {self.degree}"

    def __repr__(self):
        return f"Alumni(id={self.alumni_id}, name={self._name})"


class Coordinator(Person):
    def __init__(self, person_id, name, email, contact_number, address,
                 coordinator_id, department):
        super().__init__(person_id, name, email, contact_number, address)
        self.coordinator_id = coordinator_id
        self.department = department

    def display_details(self):
        print(f"""
  ┌─────────────────────────────────────────┐
  │         COORDINATOR PROFILE             │
  ├─────────────────────────────────────────┤
  │  ID         : {self.coordinator_id:<26}│
  │  Name       : {self._name:<26}│
  │  Department : {self.department:<26}│
  │  Email      : {self._email:<26}│
  │  Contact    : {self._contact_number:<26}│
  └─────────────────────────────────────────┘""")

    def organize_event(self):
        print(f"[{self._name}] organizing a new event...")

    def generate_reports(self):
        print(f"[{self._name}] generating reports...")

    def manage_alumni(self):
        print(f"[{self._name}] managing alumni records...")


class Employment:
    def __init__(self, employment_id, alumni_id, company_name, designation, salary, joining_date):
        self.employment_id = employment_id
        self.alumni_id = alumni_id
        self.company_name = company_name
        self.designation = designation
        self.salary = salary
        self.joining_date = joining_date

    def display_employment(self):
        print(f"""
  Employment ID : {self.employment_id}
  Alumni ID     : {self.alumni_id}
  Company       : {self.company_name}
  Designation   : {self.designation}
  Salary        : {inr(self.salary)}
  Joining Date  : {self.joining_date}""")

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, d):
        return cls(d["employment_id"], d["alumni_id"], d["company_name"],
                   d["designation"], d["salary"], d["joining_date"])

    def __str__(self):
        return f"{self.company_name} | {self.designation}"


class Event:
    def __init__(self, event_id, event_name, event_date, venue):
        self.event_id = event_id
        self.event_name = event_name
        self.event_date = event_date
        self.venue = venue
        self.participants = []

    def register_participant(self, alumni_id):
        if alumni_id not in self.participants:
            self.participants.append(alumni_id)
            return True
        return False

    def display_event_details(self):
        print(f"""
  ┌─────────────────────────────────────────┐
  │              EVENT DETAILS              │
  ├─────────────────────────────────────────┤
  │  ID          : {self.event_id:<25}│
  │  Name        : {self.event_name:<25}│
  │  Date        : {self.event_date:<25}│
  │  Venue       : {self.venue:<25}│
  │  Participants: {str(len(self.participants)):<25}│
  └─────────────────────────────────────────┘""")

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, d):
        obj = cls(d["event_id"], d["event_name"], d["event_date"], d["venue"])
        obj.participants = d.get("participants", [])
        return obj

    def __str__(self):
        return f"{self.event_name} on {self.event_date} @ {self.venue}"


class Achievement:
    def __init__(self, achievement_id, alumni_id, title, description, achievement_date):
        self.achievement_id = achievement_id
        self.alumni_id = alumni_id
        self.title = title
        self.description = description
        self.achievement_date = achievement_date

    def display_achievement(self):
        print(f"""
  Achievement ID : {self.achievement_id}
  Alumni ID      : {self.alumni_id}
  Title          : {self.title}
  Description    : {self.description}
  Date           : {self.achievement_date}""")

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, d):
        return cls(d["achievement_id"], d["alumni_id"], d["title"],
                   d["description"], d["achievement_date"])

    def __str__(self):
        return f"{self.title} ({self.achievement_date})"


class Donation:
    def __init__(self, donation_id, donor_name, alumni_id, amount, donation_date):
        self.donation_id = donation_id
        self.donor_name = donor_name
        self.alumni_id = alumni_id
        self.amount = amount
        self.donation_date = donation_date

    def generate_receipt(self):
        print(f"""
  ╔═══════════════════════════════════════╗
  ║         DONATION RECEIPT              ║
  ╠═══════════════════════════════════════╣
  ║  Receipt No  : {self.donation_id:<22}║
  ║  Donor       : {self.donor_name:<22}║
  ║  Amount      : {inr(self.amount):<22}║
  ║  Date        : {self.donation_date:<22}║
  ║  Thank you for your contribution!     ║
  ╚═══════════════════════════════════════╝""")

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, d):
        return cls(d["donation_id"], d["donor_name"], d["alumni_id"],
                   d["amount"], d["donation_date"])

    def __str__(self):
        return f"{self.donor_name} | {inr(self.amount)} | {self.donation_date}"


class Feedback:
    def __init__(self, feedback_id, alumni_id, feedback_text, rating):
        self.feedback_id = feedback_id
        self.alumni_id = alumni_id
        self.feedback_text = feedback_text
        self.rating = rating

    def display_feedback(self):
        stars = "★" * self.rating + "☆" * (5 - self.rating)
        print(f"""
  Feedback ID : {self.feedback_id}
  Alumni ID   : {self.alumni_id}
  Rating      : {stars} ({self.rating}/5)
  Feedback    : {self.feedback_text}""")

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, d):
        return cls(d["feedback_id"], d["alumni_id"], d["feedback_text"], d["rating"])


class Report:
    _report_counter = 0

    def __init__(self, report_type, content):
        Report._report_counter += 1
        self.report_id = f"RPT{Report._report_counter:03d}"
        self.report_type = report_type
        self.generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.content = content

    @classmethod
    def get_total_reports(cls):
        return cls._report_counter

    def __str__(self):
        return f"[{self.report_id}] {self.report_type} - {self.generated_date}"
