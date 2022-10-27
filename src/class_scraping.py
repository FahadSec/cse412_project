import requests as req
import json

def addStatements(obj, f):
    for a in obj["hits"]["hits"]:
        clas = a['_source']
        snum = clas['CLASSNBR']
        sub = clas['SUBJECT']
        cnum = clas['CATALOGNBR']
        loctn = json.loads(clas['LOCATIONBUILDING'])
        loc = loctn[0]['NAME']
        ses = clas['SESSIONCODE']
        seats = int(clas['ENRLCAP']) - int(clas['ENRLTOT'])
        statement_section = f"INSERT INTO Section (section_number, location, semester, session, open_seats) VALUES ({snum}. '{loc}', '{semester}', '{ses}', {seats});\n"
        statement_scheduled = f"INSERT INTO Scheduled (subject, course_number, section_number) VALUES ( '{sub}', {cnum}, {snum});\n"
        f.write(statement_section + statement_scheduled)


semester = 'Fall 2022'
semc = '2227'

scrollId=""
url = f"https://eadvs-cscc-catalog-api.apps.asu.edu:443/catalog-microservices/api/v1/search/classes?&refine=N&campusOrOnlineSelection=A&honors=F&promod=F&searchType=all&term={semc}&scrollId={scrollId}"

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

r = req.get(url, headers=headers, cookies=cookies)
obj = r.json()
scrollId = obj["_scroll_id"]

with open("class_statements.db", "w") as f:
    while len(r.text) > 0:

        addStatements(obj, f)

        url = f"https://eadvs-cscc-catalog-api.apps.asu.edu:443/catalog-microservices/api/v1/search/classes?&refine=N&campusOrOnlineSelection=A&honors=F&promod=F&searchType=all&term={semc}&scrollId={scrollId}"
        r = req.get(url, headers=headers, cookies=cookies)
        obj = r.json()
