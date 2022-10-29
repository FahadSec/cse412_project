import requests as req
import json

def addStatements(obj, f):
    for a in obj["classes"]:
        clas = a['CLAS']
        snum = clas['CLASSNBR']
        sub = clas['SUBJECT']

        cnum = clas['CATALOGNBR']
        number_ext = ""
        if len(cnum) > 3:
            temp = cnum
            cnum = temp[:3]
            number_ext = temp[3:]

        loctn = json.loads(clas['LOCATIONBUILDING'])
        loc = loctn[0]['NAME']
        ses = clas['SESSIONCODE']
        seats = int(clas['ENRLCAP']) - int(clas['ENRLTOT'])
        statement_section = f"INSERT INTO Section (section_number, location, semester, session, open_seats) VALUES ({snum}, '{loc}', '{semester}', '{ses}', {seats});\n"
        statement_scheduled = f"INSERT INTO Scheduled (subject, course_number, number_ext, section_number) VALUES ('{sub}', {cnum}, '{number_ext}', {snum});\n"
        f.write(statement_section + statement_scheduled)


semester = 'Fall 2022'

url = "https://eadvs-cscc-catalog-api.apps.asu.edu:443/catalog-microservices/api/v1/search/classes"

params={
        "refine":"Y",
        "term":"2227",
        "scrollId":""
}

cookies = {"asuCookieConsent": "true"}
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://catalog.apps.asu.edu/",
    "Authorization": "Bearer null",
    "Origin": "https://catalog.apps.asu.edu",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Te": "trailers",
}

r = req.get(url, headers=headers, cookies=cookies, params=params)
obj = r.json()
params["scrollId"] = obj["scrollId"]

with open("class_statements.sql", "w") as f:
    while len(r.text) > 600:
        obj = r.json()
        addStatements(obj, f)
        r = req.get(url, headers=headers, cookies=cookies, params=params)
