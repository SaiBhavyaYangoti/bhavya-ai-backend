from fastapi import FastAPI, Request, Query
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

@app.post("/check-availability")
async def check_availability(request: Request, date: str = Query(None)):
    try:
        body = await request.json()
        print(f"Raw body: {body}")
        actual_date = date
        if "date" in body:
            actual_date = body["date"]
        elif "message" in body:
            args = body["message"]["toolCallList"][0]["function"]["arguments"]
            actual_date = args.get("date")
    except Exception as e:
        print(f"Parse error: {e}")
        actual_date = date

    if not actual_date:
        return {"available_slots": [], "error": "date is required"}

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
async def book_meeting(request: Request):
    try:
        body = await request.json()
        print(f"Raw booking body: {body}")
        name = body.get("name")
        email = body.get("email")
        start = body.get("start")
        if "message" in body:
            args = body["message"]["toolCallList"][0]["function"]["arguments"]
            name = args.get("name")
            email = args.get("email")
            start = args.get("start")
    except Exception as e:
        print(f"Parse error: {e}")
        return {"status": "error", "message": str(e)}

    print(f"Booking for {name} ({email}) at {start}")
    url = "https://api.cal.com/v2/bookings"
    headers = {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "cal-api-version": "2024-08-13",
        "Content-Type": "application/json"
    }
    payload = {
        "eventTypeSlug": EVENT_SLUG,
        "username": USERNAME,
        "start": start,
        "attendee": {
            "name": name,
            "email": email,
            "timeZone": "Asia/Kolkata"
        }
    }
    res = requests.post(url, json=payload, headers=headers)
    data = res.json()
    print(f"Booking response: {data}")
    return {"status": "booked", "booking": data}

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
