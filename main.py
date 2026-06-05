from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional
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
    date: Optional[str] = None

@app.post("/check-availability")
def check_availability(req: AvailabilityRequest, date: str = Query(None)):
    actual_date = req.date if req.date else date
    if not actual_date:
        return {"error": "date is required"}
    print(f"Checking availability for: {actual_date}")
    start = f"{actual_date}T03:30:00Z"
    end = f"{actual_date}T11:30:00Z"
    url = f"https://api.cal.com/v2/slots?eventTypeSlug={EVENT_SLUG}&username={USERNAME}&start={start}&end={end}"
    headers = {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "cal-api-version": "2024-09-04"
    }
    res = requests.get(url, headers=headers)
    data = res.json()
    print(f"Cal.com response: {data}")
    all_slots = []
    for day_slots in data.get("data", {}).values():
        for s in day_slots:
            all_slots.append(s["start"])
    return {"available_slots": all_slots[:5]}

@app.post("/book-meeting")
def book_meeting(req: BookingRequest):
    print(f"Booking for {req.name} ({req.email}) at {req.start}")
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
    print(f"Booking response: {data}")
    return {"status": "booked", "booking": data}

@app.get("/check-availability")
def check_availability_get(date: str = Query(None)):
    if not date:
        return {"error": "date is required"}
    print(f"GET - Checking availability for: {date}")
    start = f"{date}T03:30:00Z"
    end = f"{date}T11:30:00Z"
    url = f"https://api.cal.com/v2/slots?eventTypeSlug={EVENT_SLUG}&username={USERNAME}&start={start}&end={end}"
    headers = {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "cal-api-version": "2024-09-04"
    }
    res = requests.get(url, headers=headers)
    data = res.json()
    all_slots = []
    for day_slots in data.get("data", {}).values():
        for s in day_slots:
            all_slots.append(s["start"])
    return {"available_slots": all_slots[:5]}

@app.get("/ping")
def ping():
    return {"status": "alive"}

@app.get("/test-cal")
def test_cal(date: str = Query("2026-06-10")):
    start = f"{date}T03:30:00Z"
    end = f"{date}T11:30:00Z"
    url = f"https://api.cal.com/v2/slots?eventTypeSlug={EVENT_SLUG}&username={USERNAME}&start={start}&end={end}"
    headers = {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "cal-api-version": "2024-09-04"
    }
    res = requests.get(url, headers=headers)
    return res.json()
