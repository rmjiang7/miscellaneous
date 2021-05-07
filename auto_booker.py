import requests
from bs4 import BeautifulSoup
import datetime
import logging
logging.basicConfig(filename='logs/auto_booker.log', 
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level = logging.INFO)

header = {
    "Host" : "register.recreation.ucsb.edu",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Length": "236",
    "Origin": "https://register.recreation.ucsb.edu",
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": "https://register.recreation.ucsb.edu/Account/Login?ReturnUrl=%2Fbooking%2F7e2a6844-584b-4d94-90c6-6f4abf0c5f1a"
}

header_booking = {
    "Host" : "register.recreation.ucsb.edu",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Length": "236",
    "Origin": "https://register.recreation.ucsb.edu",
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": "https://register.recreation.ucsb.edu/booking/7e2a6844-584b-4d94-90c6-6f4abf0c5f1a"
}

def login_and_book(username, password, date, slot_str):
    session = requests.Session()
    
        # Establish session
    login_info_url = "https://register.recreation.ucsb.edu/Account/GetLoginOptions?returnURL=%2F&isAdmin=false"
    res = session.get(login_info_url)
    soup = BeautifulSoup(res.text, features = "html.parser")
    request_token = soup.find("form", id = "frmExternalLogin").find("input").get("value")

    
    # Login
    login_url = "https://register.recreation.ucsb.edu//Account/Login?ReturnUrl=%2Fbooking%2F7e2a6844-584b-4d94-90c6-6f4abf0c5f1a%2Fslots%2Fc6f5c7d4-aa2c-4ca3-bcda-1f1922b15cb6%2F2021%2F4%2F16"
    request_payload = {
        'UserName' : username, 
        'Password' : password,
        '__RequestVerificationToken' : request_token
    }
    res = session.post(login_url, data = request_payload, headers = header)
    if res.json()['IsSucess'] == False:
        return -1

    logging.info("Logged in using credentials")

    # Get booking information
    booking_info_url = "https://register.recreation.ucsb.edu/booking/7e2a6844-584b-4d94-90c6-6f4abf0c5f1a/slots/c6f5c7d4-aa2c-4ca3-bcda-1f1922b15cb6/2021/{}/{}".format(date.month, date.day)
    res = session.get(booking_info_url)
    soup = BeautifulSoup(res.text, features = "html.parser")
    slots = soup.findAll("div", {"class" : "booking-slot-item"})
    print(slots)

    # Register for the specific slot
    for slot in slots:
        time = slot.find("p").find("strong").getText()
        available = slot.find("span").getText()
        if time == slot_str and available != "No spots available":
            booking_codes = slot.find("button").get("onclick").replace("Reserve","").strip("'()").split(",")
            appointmentid = booking_codes[0].replace("'","").replace(" ","")
            timeSlotId = booking_codes[1].replace("'","").replace(" ","")
            timeSlotInstanceId = booking_codes[2].replace("'","").replace(" ","")

            booking_url = "https://register.recreation.ucsb.edu/booking/reserve"
            booking_request_payload = {
                'bookingId' : "7e2a6844-584b-4d94-90c6-6f4abf0c5f1a",
                'facilityId' : "c6f5c7d4-aa2c-4ca3-bcda-1f1922b15cb6",
                'appointmentId' : appointmentid,
                'timeSlotId' : timeSlotId,
                'timeSlotInstanceId' : timeSlotInstanceId,
                'year' : '2021',
                'month' : str(date.month),
                'day' : str(date.day),
            }
            res = session.post(booking_url, data = booking_request_payload, headers = header_booking)
            if res.json()['Success']:
                return 1 
            else:
                logging.info("Could not book slot")
                return -1
    logging.info("Slot {} not listed or unavailable".format(slot_str))
    return -2

if __name__ == "__main__":
    import sys
    import time

    username = sys.argv[1]
    password = sys.argv[2]
    
    date = datetime.datetime.today() + datetime.timedelta(days=2)
    
    if date.weekday() == 5 or date.weekday() == 6:
        slot_str = "12 - 1:30 PM"
    else:
        slot_str = "7 - 8:30 AM"

    ret_code = -2
    run_count = 0
    while ret_code == -2 and run_count < 10:
        time.sleep(60)
        try:
            ret_code = login_and_book(username, password, date, slot_str)
        except KeyboardInterrupt:
            raise
        run_count += 1
    if run_count < 10 and ret_code == 1:
        logging.info("Successfully booked a spot for {} at {}!".format(date, slot_str))
    else:
        logging.info("Failed to book a spot for {} at {}".format(date, slot_str))

