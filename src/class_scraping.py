import requests as req
import json


semester = 'Fall 2022'
semc = '2227'

url = f"https://eadvs-cscc-catalog-api.apps.asu.edu:443/catalog-microservices/api/v1/search/classes?&refine=N&campusOrOnlineSelection=A&honors=F&promod=F&searchType=all&term={semc}"
cookies = {"asuCookieConsent": "true"}
headers  = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0", "Accept": "*/*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "https://catalog.apps.asu.edu/", "Authorization": "Bearer null", "Origin": "https://catalog.apps.asu.edu", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-site", "Te": "trailers"}
r = req.get(url, headers=headers, cookies=cookies)

print(r.content[:100])

# print(r)
# print(r.content)

obj = r.json()

print(json.dumps(obj['classes'][0], indent=2)[:800])
# print(json.dumps(obj[0], indent=2))

f = open("class_statements.db", "w")


for a in obj['classes']:
    clas = a['CLAS']
    snum = clas['CLASSNBR']
    sub = clas['SUBJECT']
    cnum = clas['CATALOGNBR']
    locar = json.loads(clas['LOCATIONBUILDING'])
    loc = locar[0]['NAME']
    ses = clas['SESSIONCODE']
    # seatob = json.loads(clas['seatInfo'])
    seats = a['seatInfo']['ENRL_CAP'] - a['seatInfo']['ENRL_TOT']

    statement_section = f"INSERT INTO Section (section_number, location, semester, session, open_seats) VALUES ({snum}. '{loc}', '{semester}', '{ses}', {seats});\n"
    statement_scheduled = f"INSERT INTO Scheduled (subject, course_number, section_number) VALUES ( '{sub}', {cnum}, {snum});\n"

    f.write(statement_section + statement_scheduled)

f.close()













