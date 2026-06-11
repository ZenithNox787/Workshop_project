import os
import sys
import random
from datetime import datetime

from models import Alumni, Employment, Event, Achievement, Donation, Feedback, Report, inr
from helpers import (
    log_action, alumni_report_generator, donation_report_generator,
    sort_by_batch, sort_by_company, sort_donations, recursive_search,
    get_input, get_int, get_float, print_header, print_separator, pause,
    save_all, load_all, export_alumni_csv, export_donations_csv, export_events_csv,load_counters,save_counters
)



def _gen_id(entity_type):
    counters = load_counters()
    
    counters[entity_type] += 1
    year = datetime.now().year
    seq = f"{counters[entity_type]:03d}"
    salt = random.randint(10, 99)
    
    save_counters(counters)
    
    return f"{entity_type}{year}{seq}{salt}"

class AlumniManagementSystem:
    def __init__(self):
        self.alumni_list  = []
        self.events       = []
        self.employments  = []
        self.achievements = []
        self.donations    = []
        self.feedbacks    = []
        self.reports      = []
        self._batch_years = set()
        

    @staticmethod
    def total_donation_amount(donations):
        return sum(d.amount for d in donations)

    @staticmethod
    def event_statistics(events):
        return len(events), sum(len(e.participants) for e in events)

    @classmethod
    def institution_stats(cls, system):
        return {
            "total_alumni":    len(system.alumni_list),
            "total_events":    len(system.events),
            "total_donations": AlumniManagementSystem.total_donation_amount(system.donations),
            "unique_batches":  len(system._batch_years),
        }

    def _autosave(self):
        save_all(self)
        print("  Data saved automatically.")

    def _find_alumni(self, alumni_id):
        for a in self.alumni_list:
            if a.alumni_id.lower() == alumni_id.lower():
                return a
        return None

    def _find_event(self, event_id):
        for e in self.events:
            if e.event_id.lower() == event_id.lower():
                return e
        return None

    def _list_events(self):
        print_separator()
        for e in self.events:
            print(f"  {e.event_id} | {e.event_name} | {e.event_date} | {e.venue}")
        print_separator()

    @log_action("Alumni Registration")
    def register_alumni(self):
        print_header("Register New Alumni")
        alumni_id = _gen_id("ALM")
        name    = get_input("Full Name")
        email   = get_input("Email")
        contact = input("Contact Number").strip()
        while len(contact) !=10 :
            print("Wrong number!,Please enter again")
            contact = input("Contact Number")

        address = get_input("Address")
        batch   = get_int("Batch Year", 1980, datetime.now().year)
        degree  = get_input("Degree (e.g. B.Tech, MBA)")
        company = get_input("Current Company (press Enter to skip)", allow_empty=True) or "N/A"
        desig   = get_input("Designation (press Enter to skip)", allow_empty=True) or "N/A"
        alumni  = Alumni(_gen_id("PER"), name, email, contact, address,
                         alumni_id, batch, degree, company, desig)
        self.alumni_list.append(alumni)
        self._batch_years.add(batch)
        print(f"\n  Alumni registered successfully! ID: {alumni_id}")
        self._autosave()

    def update_alumni_profile(self):
        print_header("Update Alumni Profile")
        aid = get_input("Enter Alumni ID to update")
        alumni = self._find_alumni(aid)
        if not alumni:
            print("  Alumni not found.")
            return
        alumni.display_details()
        print("\n  Leave blank to keep existing value.")
        name    = get_input("New Name", allow_empty=True)
        email   = get_input("New Email", allow_empty=True)
        contact = get_input("New Contact", allow_empty=True)
        address = get_input("New Address", allow_empty=True)
        alumni.update_details(name=name or None, email=email or None,
                              contact_number=contact or None, address=address or None)
        print("  Profile updated.")
        self._autosave()

    def search_alumni(self):
        print_header("Search Alumni")
        print("  1. By Name    2. By Alumni ID    3. By Batch Year")
        choice = get_int("Choice", 1, 3)
        if choice == 1:
            results = recursive_search(self.alumni_list, get_input("Enter name or partial name"))
        elif choice == 2:
            results = recursive_search(self.alumni_list, get_input("Enter Alumni ID"))
        else:
            year = get_int("Enter Batch Year", 1980, datetime.now().year)
            results = [a for a in self.alumni_list if a.batch_year == year]
        if results:
            print(f"\n  Found {len(results)} result(s):")
            print_separator()
            for a in results:
                print(f"  {a.alumni_id} | {a._name} | Batch: {a.batch_year} | {a.degree}")
        else:
            print("  No alumni found matching your search.")

    def view_all_alumni(self):
        print_header("All Alumni Records")
        if not self.alumni_list:
            print("  No alumni registered yet.")
            return
        print("\n  Sort by:  1. Batch Year   2. Company Name   3. Default")
        ch = get_int("Choice", 1, 3)
        lst = sort_by_batch(self.alumni_list) if ch == 1 else \
              sort_by_company(self.alumni_list) if ch == 2 else self.alumni_list
        print_separator()
        print(f"  {'ID':<10} {'Name':<22} {'Batch':<6} {'Degree':<15} {'Company'}")
        print_separator()
        for a in lst:
            print(f"  {a.alumni_id:<10} {a._name:<22} {a.batch_year:<6} {a.degree:<15} {a.current_company}")

    def view_alumni_details(self):
        print_header("View Alumni Details")
        aid = get_input("Enter Alumni ID")
        alumni = self._find_alumni(aid)
        if not alumni:
            print("  Alumni not found.")
            return
        alumni.view_profile()
        emp_records = [e for e in self.employments if e.alumni_id == alumni.alumni_id]
        if emp_records:
            print("\n  Employment History:")
            print_separator()
            for e in emp_records:
                e.display_employment()
        ach_records = [a for a in self.achievements if a.alumni_id == alumni.alumni_id]
        if ach_records:
            print("\n  Achievements:")
            print_separator()
            for a in ach_records:
                a.display_achievement()
        don_records = [d for d in self.donations if d.alumni_id == alumni.alumni_id]
        if don_records:
            total = sum(d.amount for d in don_records)
            print(f"\n  Donations: {len(don_records)} contribution(s), Total: Rs.{float(total):,.2f}")
        events_attended = [e for e in self.events if alumni.alumni_id in e.participants]
        if events_attended:
            print(f"\n  Events Attended: {len(events_attended)}")
            for e in events_attended:
                print(f"    {e.event_id} | {e.event_name} | {e.event_date}")

    @log_action("Employment Update")
    def add_employment(self):
        print_header("Add Employment Record")
        aid = get_input("Alumni ID")
        alumni = self._find_alumni(aid)
        if not alumni:
            print("  Alumni not found.")
            return
        company = get_input("Company Name")
        desig   = get_input("Designation")
        salary  = get_float("Annual Salary", 0)
        j_date  = get_input("Joining Date (YYYY-MM-DD)")
        emp = Employment(_gen_id("EMP"), aid, company, desig, salary, j_date)
        self.employments.append(emp)
        alumni.update_employment(company, desig)
        print(f"  Employment record added. ID: {emp.employment_id}")
        self._autosave()

    def view_employment(self):
        print_header("Employment Records")
        aid = get_input("Enter Alumni ID")
        records = [e for e in self.employments if e.alumni_id == aid]
        if records:
            for r in records:
                r.display_employment()
                print_separator()
        else:
            print("  No employment records for this alumni.")

    @log_action("Event Creation")
    def create_event(self):
        print_header("Create New Event")
        event_name = get_input("Event Name")
        event_date = get_input("Event Date (YYYY-MM-DD)")
        venue      = get_input("Venue")
        event = Event(_gen_id("EVT"), event_name, event_date, venue)
        self.events.append(event)
        print(f"  Event created. ID: {event.event_id}")
        self._autosave()

    @log_action("Event Registration")
    def register_for_event(self):
        print_header("Register Alumni for Event")
        if not self.events:
            print("  No events available.")
            return
        self._list_events()
        event = self._find_event(get_input("Event ID"))
        if not event:
            print("  Event not found.")
            return
        alumni = self._find_alumni(get_input("Alumni ID"))
        if not alumni:
            print("  Alumni not found.")
            return
        if event.register_participant(alumni.alumni_id):
            alumni.register_for_event(event.event_id)
            print(f"  {alumni._name} registered for '{event.event_name}'.")
            self._autosave()
        else:
            print("  Alumni already registered for this event.")

    def view_events(self):
        print_header("All Events")
        if not self.events:
            print("  No events found.")
            return
        for e in self.events:
            e.display_event_details()

    def view_event_participants(self):
        print_header("Event Participants")
        self._list_events()
        event = self._find_event(get_input("Event ID"))
        if not event:
            print("  Event not found.")
            return
        print(f"\n  Event: {event.event_name} | Total: {len(event.participants)}")
        print_separator()
        for pid in event.participants:
            a = self._find_alumni(pid)
            print(f"  {pid} | {a._name if a else 'Unknown'}")

    def add_achievement(self):
        print_header("Add Achievement")
        alumni = self._find_alumni(get_input("Alumni ID"))
        if not alumni:
            print("  Alumni not found.")
            return
        title = get_input("Achievement Title")
        desc  = get_input("Description")
        date  = get_input("Achievement Date (YYYY-MM-DD)")
        ach   = Achievement(_gen_id("ACH"), alumni.alumni_id, title, desc, date)
        self.achievements.append(ach)
        alumni.achievements.append(ach.achievement_id)
        print(f"  Achievement recorded. ID: {ach.achievement_id}")
        self._autosave()

    def view_achievements(self):
        print_header("Alumni Achievements")
        aid = get_input("Enter Alumni ID (or press Enter to view all)", allow_empty=True)
        records = [a for a in self.achievements if not aid or a.alumni_id == aid]
        if records:
            for r in records:
                r.display_achievement()
                print_separator()
        else:
            print("  No achievements found.")

    @log_action("Donation Processing")
    def record_donation(self):
        print_header("Record Donation")
        alumni = self._find_alumni(get_input("Alumni ID"))
        if not alumni:
            print("  Alumni not found.")
            return
        amount = get_float("Donation Amount", min_val=1)
        don = Donation(_gen_id("DON"), alumni._name, alumni.alumni_id,
                       amount, datetime.now().strftime("%Y-%m-%d"))
        self.donations.append(don)
        don.generate_receipt()
        self._autosave()

    def view_donations(self):
        print_header("All Donations")
        if not self.donations:
            print("  No donations recorded yet.")
            return
        sorted_d = sort_donations(self.donations)
        print_separator()
        print(f"  {'ID':<10} {'Donor':<22} {'Amount (Rs.)':>16}  {'Date'}")
        print_separator()
        for d in sorted_d:
            print(f"  {d.donation_id:<10} {d.donor_name:<22} {inr(d.amount):>16}  {d.donation_date}")
        print_separator()
        print(f"  Total Collected: {inr(self.total_donation_amount(self.donations))}")

    def alumni_directory(self):
        print_header("Alumni Networking Directory")
        if not self.alumni_list:
            print("  No alumni registered.")
            return
        print(f"\n  {'Name':<22} {'Batch':<7} {'Company':<25} {'Email'}")
        print_separator()
        for a in sort_by_batch(self.alumni_list):
            print(f"  {a._name:<22} {a.batch_year:<7} {a.current_company:<25} {a._email}")

    def batch_wise_directory(self):
        print_header("Batch-wise Alumni Directory")
        if not self._batch_years:
            print("  No alumni data.")
            return
        for year in sorted(self._batch_years):
            batch_alumni = [a for a in self.alumni_list if a.batch_year == year]
            print(f"\n  Batch {year}  ({len(batch_alumni)} alumni)")
            print_separator()
            for a in batch_alumni:
                print(f"    {a.alumni_id} | {a._name} | {a.current_company}")

    def submit_feedback(self):
        print_header("Submit Feedback")
        alumni = self._find_alumni(get_input("Alumni ID"))
        if not alumni:
            print("  Alumni not found.")
            return
        text   = get_input("Your Feedback")
        rating = get_int("Rating (1-5)", 1, 5)
        fb = Feedback(_gen_id("FBK"), alumni.alumni_id, text, rating)
        self.feedbacks.append(fb)
        print("  Feedback submitted. Thank you!")
        self._autosave()

    def view_feedback(self):
        print_header("Alumni Feedback")
        if not self.feedbacks:
            print("  No feedback received yet.")
            return
        for fb in self.feedbacks:
            fb.display_feedback()
            print_separator()

    @log_action("Report Generation")
    def generate_reports(self):
        print_header("Report Generation")
        print("""
  1. Alumni Statistics Report
  2. Employment Report
  3. Donation Report
  4. Event Participation Report
  5. Batch-wise Alumni Report
  6. Export Alumni Directory (CSV)
  7. Export Donations Report (CSV)
  8. Export Events Report (CSV)""")
        ch = get_int("Choice", 1, 8)
        if ch == 1:
            stats = self.institution_stats(self)
            print(f"""
  ┌─────────────────────────────────────────┐
  │        ALUMNI STATISTICS REPORT         │
  ├─────────────────────────────────────────┤
  │  Total Alumni    : {str(stats['total_alumni']):<22}│
  │  Total Events    : {str(stats['total_events']):<22}│
  │  Total Donations : {inr(stats['total_donations']):<22}│
  │  Unique Batches  : {str(stats['unique_batches']):<22}│
  │  Total Feedbacks : {str(len(self.feedbacks)):<22}│
  └─────────────────────────────────────────┘""")
            self.reports.append(Report("Alumni Statistics", stats))
        elif ch == 2:
            print_header("Employment Report")
            if not self.employments:
                print("  No employment records.")
                return
            print(f"  {'ID':<10} {'Alumni ID':<10} {'Company':<22} {'Designation':<18} {'Salary':>16}")
            print_separator()
            for e in self.employments:
                print(f"  {e.employment_id:<10} {e.alumni_id:<10} {e.company_name:<22} {e.designation:<18} {inr(e.salary):>16}")
        elif ch == 3:
            print_header("Donation Report")
            print(f"  {'ID':<10} {'Donor':<22} {'Amount (Rs.)':>16}  {'Date'}")
            print_separator()
            for rec in donation_report_generator(sort_donations(self.donations)):
                print(f"  {rec[0]:<10} {rec[1]:<22} {inr(rec[2]):>16}  {rec[3]}")
            print_separator()
            print(f"  Total Collected: {inr(self.total_donation_amount(self.donations))}")
        elif ch == 4:
            print_header("Event Participation Report")
            total_ev, total_p = self.event_statistics(self.events)
            print(f"\n  Total Events: {total_ev}  |  Total Participations: {total_p}\n")
            print(f"  {'Event ID':<10} {'Name':<25} {'Date':<12} {'Participants':>12}")
            print_separator()
            for e in self.events:
                print(f"  {e.event_id:<10} {e.event_name:<25} {e.event_date:<12} {len(e.participants):>12}")
        elif ch == 5:
            self.batch_wise_directory()
        elif ch == 6:
            export_alumni_csv(self.alumni_list)
        elif ch == 7:
            export_donations_csv(self.donations)
        elif ch == 8:
            export_events_csv(self.events)

    def load_data(self):
        load_all(self)


def alumni_menu(ams):
    while True:
        print_header("Alumni Management")
        print("""
  1. Register New Alumni
  2. Update Alumni Profile
  3. Search Alumni
  4. View All Alumni
  5. View Alumni Details
  0. Back""")
        ch = get_int("Choice", 0, 5)
        try:
            if ch == 1:
                ams.register_alumni()
            elif ch == 2:
                ams.update_alumni_profile()
            elif ch == 3:
                ams.search_alumni()
            elif ch == 4:
                ams.view_all_alumni()
            elif ch == 5:
                ams.view_alumni_details()
            elif ch == 0:
                break
        except Exception as e:
            print(f"  Error: {e}")
        if ch != 0:
            pause()


def employment_menu(ams):
    while True:
        print_header("Employment Management")
        print("""
  1. Add Employment Record
  2. View Employment Records
  0. Back""")
        ch = get_int("Choice", 0, 2)
        try:
            if ch == 1:
                ams.add_employment()
            elif ch == 2:
                ams.view_employment()
            elif ch == 0:
                break
        except Exception as e:
            print(f"  Error: {e}")
        if ch != 0:
            pause()


def event_menu(ams):
    while True:
        print_header("Event Management")
        print("""
  1. Create New Event
  2. Register Alumni for Event
  3. View All Events
  4. View Event Participants
  0. Back""")
        ch = get_int("Choice", 0, 4)
        try:
            if ch == 1:
                ams.create_event()
            elif ch == 2:
                ams.register_for_event()
            elif ch == 3:
                ams.view_events()
            elif ch == 4:
                ams.view_event_participants()
            elif ch == 0:
                break
        except Exception as e:
            print(f"  Error: {e}")
        if ch != 0:
            pause()


def achievement_menu(ams):
    while True:
        print_header("Achievement Management")
        print("""
  1. Add Achievement
  2. View Achievements
  0. Back""")
        ch = get_int("Choice", 0, 2)
        try:
            if ch == 1:
                ams.add_achievement()
            elif ch == 2:
                ams.view_achievements()
            elif ch == 0:
                break
        except Exception as e:
            print(f"  Error: {e}")
        if ch != 0:
            pause()


def donation_menu(ams):
    while True:
        print_header("Donation Management")
        print("""
  1. Record Donation
  2. View All Donations
  0. Back""")
        ch = get_int("Choice", 0, 2)
        try:
            if ch == 1:
                ams.record_donation()
            elif ch == 2:
                ams.view_donations()
            elif ch == 0:
                break
        except Exception as e:
            print(f"  Error: {e}")
        if ch != 0:
            pause()


def networking_menu(ams):
    while True:
        print_header("Networking Directory")
        print("""
  1. Full Alumni Directory
  2. Batch-wise Directory
  0. Back""")
        ch = get_int("Choice", 0, 2)
        try:
            if ch == 1:
                ams.alumni_directory()
            elif ch == 2:
                ams.batch_wise_directory()
            elif ch == 0:
                break
        except Exception as e:
            print(f"  Error: {e}")
        if ch != 0:
            pause()


def feedback_menu(ams):
    while True:
        print_header("Feedback Management")
        print("""
  1. Submit Feedback
  2. View All Feedback
  0. Back""")
        ch = get_int("Choice", 0, 2)
        try:
            if ch == 1:
                ams.submit_feedback()
            elif ch == 2:
                ams.view_feedback()
            elif ch == 0:
                break
        except Exception as e:
            print(f"  Error: {e}")
        if ch != 0:
            pause()


def main():
    os.system("clear" if os.name == "posix" else "cls")
    print("""
  ╔═══════════════════════════════════════════╗
  ║    Welcome to Alumni Management System    ║
  ╚═══════════════════════════════════════════╝""")

    ams = AlumniManagementSystem()
    ams.load_data()

    while True:
        print("""
  ╔═══════════════════════════════════════════╗
  ║      ALUMNI MANAGEMENT SYSTEM             ║
  ╠═══════════════════════════════════════════╣
  ║   1.  Alumni Management                   ║
  ║   2.  Employment Management               ║
  ║   3.  Event Management                    ║
  ║   4.  Achievement Management              ║
  ║   5.  Donation Management                 ║
  ║   6.  Networking Directory                ║
  ║   7.  Feedback Management                 ║
  ║   8.  Report Generation                   ║
  ║   0.  Exit                                ║
  ╚═══════════════════════════════════════════╝""")
        try:
            choice = get_int("Enter your choice", 0, 8)
            if choice == 1:
                alumni_menu(ams)
            elif choice == 2:
                employment_menu(ams)
            elif choice == 3:
                event_menu(ams)
            elif choice == 4:
                achievement_menu(ams)
            elif choice == 5:
                donation_menu(ams)
            elif choice == 6:
                networking_menu(ams)
            elif choice == 7:
                feedback_menu(ams)
            elif choice == 8:
                ams.generate_reports()
                pause()
            elif choice == 0:
                save_all(ams)
                print("""
  ╔═══════════════════════════════════════════╗
  ║   Thank you for using Alumni Mgmt System  ║
  ║                  Goodbye!                 ║
  ╚═══════════════════════════════════════════╝
""")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\n\n  Saving data before exit...")
            save_all(ams)
            sys.exit(0)
        except Exception as e:
            print(f"\n  Unexpected error: {e}")
            pause()


if __name__ == "__main__":
    main()
