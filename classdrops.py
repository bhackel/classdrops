import time, smtplib, re
import requests
from bs4 import BeautifulSoup as BS
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

courses = input("Type the courses here, then push enter:    ")

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    'sec-ch-ua-mobile': '?0',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'https://act.ucsd.edu',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudent.htm',
    'Accept-Language': 'en-US,en;q=0.9',
}

data = [
    ('selectedTerm', 'FA21'),
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
    # Get HTML response from link with selected classes inputted
    url = 'https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudentResult.htm'
    response = requests.post(url, headers=headers, data=data, timeout=10)
    soup = BS(response.text, 'html.parser')

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
            try:
                # Fetch details from file
                with open('nudes.txt', 'r') as f:
                    contents = f.readlines()
                    gmail_address = contents[0]
                    gmail_password = contents[1]
                    att_number = contents[2]

                # Setup Server
                if server is None:
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(gmail_address, gmail_password)

                # Setup message contents
                section_id = col[2].getText().strip()
                day = col[5].getText().strip()
                time_ = col[6].getText().strip()
                building = col[7].getText().strip()
                prof = col[9].getText().strip()
                # Get 4 letter class ID using an excessively long regex
                class_id = re.search('subject=....', col[12].find('span')['onclick'])[0][-4:]

                message = f'Open class {class_id} of ID {section_id} on {day} at {time_} in {building} with {prof}'

                # Format everything using MIME
                msg = MIMEMultipart()
                msg['From'] = gmail_address
                msg['To'] = f'{att_number}@txt.att.net'
                msg['Subject'] = "Free Diamonds"
                body = message
                msg.attach(MIMEText(body, 'plain'))

                sms = msg.as_string()

                # Send text message through SMS gateway of destination number
                print(message)
                server.sendmail(gmail_address, f'{att_number}@txt.att.net', sms)
                print("Successfully sent message")
            except Exception as e:
                print("Something failed when sending a message:", e)

    print("Checking again in 90 seconds\n")
    time.sleep(90)
