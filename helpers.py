import functools
import json
import csv
import os
from datetime import datetime
from models import Alumni, Event, Employment, Achievement, Donation, Feedback

DATA_DIR        = "data"
ALUMNI_FILE     = os.path.join(DATA_DIR, "alumni.json")
EVENTS_FILE     = os.path.join(DATA_DIR, "events.json")
EMPLOYMENT_FILE = os.path.join(DATA_DIR, "employment.json")
ACHIEVEMENT_FILE= os.path.join(DATA_DIR, "achievements.json")
DONATION_FILE   = os.path.join(DATA_DIR, "donations.json")
FEEDBACK_FILE   = os.path.join(DATA_DIR, "feedbacks.json")
COUNTERS_FILE = os.path.join(DATA_DIR, "counters.json")



def log_action(action_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n  [LOG {timestamp}] {action_name} initiated.")
            result = func(*args, **kwargs)
            print(f"  [LOG {timestamp}] {action_name} completed.")
            return result
        return wrapper
    return decorator


def alumni_report_generator(alumni_list):
    for alumni in alumni_list:
        yield (alumni.alumni_id, alumni._name, alumni.batch_year,
               alumni.degree, alumni.current_company, alumni.designation, alumni._email)


def donation_report_generator(donations):
    for d in donations:
        yield (d.donation_id, d.donor_name, d.amount, d.donation_date)


sort_by_batch   = lambda lst: sorted(lst, key=lambda a: a.batch_year)
sort_by_company = lambda lst: sorted(lst, key=lambda a: a.current_company.lower())
sort_donations  = lambda lst: sorted(lst, key=lambda d: d.amount, reverse=True)


def recursive_search(alumni_list, query, index=0):
    if index >= len(alumni_list):
        return []
    a = alumni_list[index]
    match = query.lower() in a._name.lower() or query.lower() == a.alumni_id.lower()
    rest = recursive_search(alumni_list, query, index + 1)
    return [a] + rest if match else rest


def get_input(prompt, allow_empty=False):
    while True:
        try:
            val = input(f"  {prompt}: ").strip()
        except EOFError:
            return ""
        if val or allow_empty:
            return val
        print("  Input cannot be empty.")


def get_int(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = int(input(f"  {prompt}: ").strip())
            if min_val is not None and val < min_val:
                print(f"  Value must be at least {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"  Value must be at most {max_val}.")
                continue
            return val
        except ValueError:
            print("  Please enter a valid integer.")


def get_float(prompt, min_val=0):
    while True:
        try:
            val = float(input(f"  {prompt}: ").strip())
            if val < min_val:
                print(f"  Value must be at least {min_val}.")
                continue
            return val
        except ValueError:
            print("  Please enter a valid number.")


def print_header(title):
    print("\n" + "═" * 45)
    print(f"  {title.upper()}")
    print("═" * 45)


def print_separator():
    print("  " + "─" * 43)


def pause():
    try:
        input("\n  Press Enter to continue...")
    except EOFError:
        pass


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def save_all(system):
    ensure_data_dir()
    try:
        with open(ALUMNI_FILE, "w") as f:
            json.dump([a.to_dict() for a in system.alumni_list], f, indent=2)
        with open(EVENTS_FILE, "w") as f:
            json.dump([e.to_dict() for e in system.events], f, indent=2)
        with open(EMPLOYMENT_FILE, "w") as f:
            json.dump([e.to_dict() for e in system.employments], f, indent=2)
        with open(ACHIEVEMENT_FILE, "w") as f:
            json.dump([a.to_dict() for a in system.achievements], f, indent=2)
        with open(DONATION_FILE, "w") as f:
            json.dump([d.to_dict() for d in system.donations], f, indent=2)
        with open(FEEDBACK_FILE, "w") as f:
            json.dump([fb.to_dict() for fb in system.feedbacks], f, indent=2)
    except Exception as e:
        print(f"  Auto-save error: {e}")


def load_all(system):
    ensure_data_dir()
    try:
        if os.path.exists(ALUMNI_FILE):
            with open(ALUMNI_FILE) as f:
                system.alumni_list = [Alumni.from_dict(d) for d in json.load(f)]
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE) as f:
                system.events = [Event.from_dict(d) for d in json.load(f)]
        if os.path.exists(EMPLOYMENT_FILE):
            with open(EMPLOYMENT_FILE) as f:
                system.employments = [Employment.from_dict(d) for d in json.load(f)]
        if os.path.exists(ACHIEVEMENT_FILE):
            with open(ACHIEVEMENT_FILE) as f:
                system.achievements = [Achievement.from_dict(d) for d in json.load(f)]
        if os.path.exists(DONATION_FILE):
            with open(DONATION_FILE) as f:
                system.donations = [Donation.from_dict(d) for d in json.load(f)]
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE) as f:
                system.feedbacks = [Feedback.from_dict(d) for d in json.load(f)]
        system._batch_years = {a.batch_year for a in system.alumni_list}
    except Exception:
        pass


def export_alumni_csv(alumni_list):
    ensure_data_dir()
    path = os.path.join(DATA_DIR, "alumni_directory.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Alumni ID","Name","Batch Year","Degree","Company","Designation","Email"])
        for a in alumni_list:
            writer.writerow([a.alumni_id, a._name, a.batch_year, a.degree,
                             a.current_company, a.designation, a._email])
    print(f"  Alumni directory exported to {path}")


def export_donations_csv(donations):
    ensure_data_dir()
    path = os.path.join(DATA_DIR, "donations_report.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Donation ID","Donor","Alumni ID","Amount","Date"])
        for d in donations:
            writer.writerow([d.donation_id, d.donor_name, d.alumni_id, d.amount, d.donation_date])
    print(f"  Donations report exported to {path}")


def export_events_csv(events):
    ensure_data_dir()
    path = os.path.join(DATA_DIR, "events_report.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Event ID","Name","Date","Venue","Participants"])
        for e in events:
            writer.writerow([e.event_id, e.event_name, e.event_date, e.venue, len(e.participants)])
    print(f"  Events report exported to {path}")


def load_counters():
    default_counters = {"ALM": 0, "PER": 0, "EMP": 0, "EVT": 0, "ACH": 0, "DON": 0, "FBK": 0}
    if os.path.exists(COUNTERS_FILE):
        try:
            with open(COUNTERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return default_counters
    return default_counters

def save_counters(counters):
    ensure_data_dir()
    try:
        with open(COUNTERS_FILE, "w") as f:
            json.dump(counters, f, indent=2)
    except Exception as e:
        print(f"  Error saving counters: {e}")