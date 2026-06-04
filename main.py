from fastapi import FastAPI
from pydantic import BaseModel
import requests
from datetime import datetime, timedelta

app = FastAPI()

CAL_API_KEY = "cal_live_46446a7bf96c703ddcabfad086c5cd91"
USERNAME = "saibhavya-yangoti-s9xhms"
EVENT_SLUG = "30min"

class BookingRequest(BaseModel):
    name: str
    email: str
    start: str  # ISO format: 2026-06-10T10:00:00Z

@app.get("/check-availability")
def check_availability(date: str):  # date: YYYY-MM-DD
    start = f"{date}T00:00:00+05:30"
    end = f"{date}T23:59:59+05:30"
    url = f"https://api.cal.com/v2/slots/available?eventTypeSlug={EVENT_SLUG}&username={USERNAME}&start={start}&end={end}"
    headers = {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "cal-api-version": "2024-09-04"
    }
    res = requests.get(url, headers=headers)
    data = res.json()
    slots = data.get("data", {}).get("slots", {})
    all_slots = []
    for day_slots in slots.values():
        for s in day_slots:
            all_slots.append(s["time"])
    return {"available_slots": all_slots[:5]}  # return top 5 slots

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
