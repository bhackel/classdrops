import time, smtplib, re
import requests
from bs4 import BeautifulSoup as BS
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import win10toast
import dotenv
from dotenv import dotenv_values

toast = win10toast.ToastNotifier()
config = dotenv.dotenv_values('config.env')

courses = config['courses']
if len(courses) == 0:
    assert "courses in config.env is empty, add some course names."

term = config['term']
if len(term) == 0:
    assert "term in config.env is missing. Format is FA22, WI22, SP22, S122, S222"

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Origin': 'https://act.ucsd.edu',
    'Pragma': 'no-cache',
    'Referer': 'https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudentResult.htm',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

data = [
    ('selectedTerm', term),
    ('xsoc_term', ''),
    ('loggedIn', 'false'),
    ('tabNum', 'tabs-crs'),
    ('_selectedSubjects', '1'),
    ('schedOption1', 'true'),
    ('_schedOption1', 'on'),
    ('_schedOption11', 'on'),
    ('_schedOption12', 'on'),
    ('schedOption2', 'true'),
    ('_schedOption2', 'on'),
    ('_schedOption4', 'on'),
    ('_schedOption5', 'on'),
    ('_schedOption3', 'on'),
    ('_schedOption7', 'on'),
    ('_schedOption8', 'on'),
    ('_schedOption13', 'on'),
    ('_schedOption10', 'on'),
    ('_schedOption9', 'on'),
    ('schDay', 'M'),
    ('schDay', 'T'),
    ('schDay', 'W'),
    ('schDay', 'R'),
    ('schDay', 'F'),
    ('schDay', 'S'),
    ('_schDay', 'on'),
    ('_schDay', 'on'),
    ('_schDay', 'on'),
    ('_schDay', 'on'),
    ('_schDay', 'on'),
    ('_schDay', 'on'),
    ('schStartTime', '12:00'),
    ('schStartAmPm', '0'),
    ('schEndTime', '12:00'),
    ('schEndAmPm', '0'),
    ('_selectedDepartments', '1'),
    ('schedOption1Dept', 'true'),
    ('_schedOption1Dept', 'on'),
    ('_schedOption11Dept', 'on'),
    ('_schedOption12Dept', 'on'),
    ('schedOption2Dept', 'true'),
    ('_schedOption2Dept', 'on'),
    ('_schedOption4Dept', 'on'),
    ('_schedOption5Dept', 'on'),
    ('_schedOption3Dept', 'on'),
    ('_schedOption7Dept', 'on'),
    ('_schedOption8Dept', 'on'),
    ('_schedOption13Dept', 'on'),
    ('_schedOption10Dept', 'on'),
    ('_schedOption9Dept', 'on'),
    ('schDayDept', 'M'),
    ('schDayDept', 'T'),
    ('schDayDept', 'W'),
    ('schDayDept', 'R'),
    ('schDayDept', 'F'),
    ('schDayDept', 'S'),
    ('_schDayDept', 'on'),
    ('_schDayDept', 'on'),
    ('_schDayDept', 'on'),
    ('_schDayDept', 'on'),
    ('_schDayDept', 'on'),
    ('_schDayDept', 'on'),
    ('schStartTimeDept', '12:00'),
    ('schStartAmPmDept', '0'),
    ('schEndTimeDept', '12:00'),
    ('schEndAmPmDept', '0'),
    ('courses', courses),
    ('sections', ''),
    ('instructorType', 'begin'),
    ('instructor', ''),
    ('titleType', 'contain'),
    ('title', ''),
    ('_hideFullSec', 'on'),
    ('_showPopup', 'on'),
]

server = None

while True:
    timestamp = time.strftime('%a %H:%M:%S')
    print(timestamp)

    # Get HTML response from link with selected classes inputted
    url = 'https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudentResult.htm'
    response = requests.post(url, headers=headers, data=data, timeout=10)
    soup = BS(response.text, 'html.parser')

    # Find all sections for classes using specific class tag
    section_all = soup.find_all('tr', {'class': 'sectxt'})
    for section in section_all:
        col = section.find_all('td')
        try:
            resource_elem = col[10]
        except IndexError:
            # Skip if not found, such as when section is cancelled
            continue

        # Check if the class is not full
        resource_text = resource_elem.getText().strip()
        if "FULL" not in resource_text and len(resource_text) > 0:
            print("Open class found")
            print("Trying to send message")

            # First send windows notification
            toast.show_toast("ClassDrops Bot",f"Open class found: {courses}",duration=5)

            try:
                # Fetch details from config
                gmail_address = config['email']
                gmail_password = config['app_pass']
                att_number = config['phone']

                # Setup message contents
                section_id = col[2].getText().strip()
                day = col[5].getText().strip()
                time_ = col[6].getText().strip()
                building = col[7].getText().strip()
                prof = col[9].getText().strip()
                # Get 4 letter class ID using an excessively long regex
                class_id = re.search('subject=....', col[12].find('span')['onclick'])[0][-4:]

                message = f'Open class {class_id}, ID {section_id}, {day}, {time_} with {prof}'

                # Format everything using MIME
                msg = MIMEMultipart()
                msg['From'] = gmail_address
                msg['To'] = f'{att_number}@txt.att.net'
                msg['Subject'] = "ClassDrops Bot"
                body = message
                msg.attach(MIMEText(body, 'plain'))
                sms = msg.as_string()
                print(f"Message: {message}")

                # Setup Server
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(gmail_address, gmail_password)

                # Send text message through SMS gateway of destination number
                server.sendmail(gmail_address, f'{att_number}@txt.att.net', sms)
                server.quit()

                print("Successfully sent message")
            except KeyError:
                assert "Invalid credentials in config.env"
            finally:
                print("Waiting 600 seconds")
                time.sleep(600)

    print("Checking again in 180 seconds\n")
    time.sleep(240)
