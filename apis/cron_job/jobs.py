import requests
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from apis.database import get_data_scheduler, remove_data_scheduler, add_data_scheduler, get_all_user
# from apis.main import internal_extract_certificates
def run_task():
    print("Starting cron job...", flush=True)
    url = "http://172.28.96.1:8000/internal_extract_certificates"
    users_data = get_all_user()
    print("The users data is ", users_data)
    users = users_data.get("data", [])
    print("here is the users", users)
    for record in users:
        email = record.get("username")
        role = record.get("role")
        try:
            print("lets call the api")
            resp = requests.post(f"{url}?email={email}&role={role}")
            # resp = requests.post(url, json=data, timeout=10)
            print(">>> Cron job started <<<", flush=True)

            print("Response:", resp.json())
            # internal_extract_certificates(email, role)
            scheduled_data = get_data_scheduler(email, role).get("data")
            if scheduled_data:
                status = remove_data_scheduler(email, role)
                print("Removed scheduled data:", status)
            add_data_scheduler(email, role, resp.json())
        except Exception as e:
            print("Error calling API:", e)

if __name__ == "__main__":
    run_task()
