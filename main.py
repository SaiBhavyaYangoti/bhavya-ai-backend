from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

CAL_API_KEY = "cal_live_46446a7bf96c703ddcabfad086c5cd91"
USERNAME = "saibhavya-yangoti-s9xhms"
EVENT_SLUG = "30min"

class BookingRequest(BaseModel):
    name: str
    email: str
    start: str

class AvailabilityRequest(BaseModel):
    date: str

@app.post("/check-availability")
def check_availability(req: AvailabilityRequest):
    print(f"Received date: {req.date}")  # add this
    start = f"{req.date}T03:30:00Z"
    end = f"{req.date}T11:30:00Z"
    url = f"https://api.cal.com/v2/slots?eventTypeSlug={EVENT_SLUG}&username={USERNAME}&start={start}&end={end}"
    headers = {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "cal-api-version": "2024-09-04"
    }
    res = requests.get(url, headers=headers)
    data = res.json()
    print(f"Cal.com response: {data}")  # add this
    all_slots = []
    day_data = data.get("data", {})
    for day_slots in day_data.values():
        for s in day_slots:
            all_slots.append(s["start"])
    return {"available_slots": all_slots[:5]}

@app.post("/book-meeting")
def book_meeting(req: BookingRequest):
    url = "https://api.cal.com/v2/bookings"
    headers = {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "cal-api-version": "2024-08-13",
        "Content-Type": "application/json"
    }
    payload = {
        "eventTypeSlug": EVENT_SLUG,
        "username": USERNAME,
        "start": req.start,
        "attendee": {
            "name": req.name,
            "email": req.email,
            "timeZone": "Asia/Kolkata"
        }
    }
    res = requests.post(url, json=payload, headers=headers)
    data = res.json()
    return {"status": "booked", "booking": data}

@app.get("/debug-cal")
def debug_cal(date: str):
    start = f"{date}T03:30:00Z"
    end = f"{date}T11:30:00Z"
    url = f"https://api.cal.com/v2/slots?eventTypeSlug={EVENT_SLUG}&username={USERNAME}&start={start}&end={end}"
    headers = {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "cal-api-version": "2024-09-04"
    }
    res = requests.get(url, headers=headers)
    return res.json()

@app.get("/ping")
def ping():
    return {"status": "alive"}

@app.get("/test-cal")
def test_cal():
    import requests
    start = "2026-06-10T03:30:00Z"
    end = "2026-06-10T11:30:00Z"
    url = f"https://api.cal.com/v2/slots?eventTypeSlug={EVENT_SLUG}&username={USERNAME}&start={start}&end={end}"
    headers = {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "cal-api-version": "2024-09-04"
    }
    res = requests.get(url, headers=headers)
    return res.json()
