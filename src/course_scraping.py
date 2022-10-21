import requests as req
import json

url = "https://eadvs-cscc-catalog-api.apps.asu.edu:443/catalog-microservices/api/v1/search/courses?&refine=Y&campusOrOnlineSelection=A&honors=F&promod=F&searchType=all&term=2227"#&subject=CSE&term=2227""
cookies = {"asuCookieConsent": "true"}
headers  = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0", "Accept": "*/*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "https://catalog.apps.asu.edu/", "Authorization": "Bearer null", "Origin": "https://catalog.apps.asu.edu", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-site", "Te": "trailers"}
r = req.get(url, headers=headers, cookies=cookies)

print(r.content[:100])

# print(r)
# print(r.content)

obj = r.json()

# print(json.dumps(obj['classes'][0], indent=2))
# print(json.dumps(obj[0], indent=2))

f = open("statements.db", "w")


for a in obj:

    sub = a['SUBJECT']
    cnum = a['CATALOGNBR']
    title = a['COURSETITLELONG']
    credits = 0
    if 'UNITSMAXIMUM' in a.keys():
        credits = a['UNITSMAXIMUM']
    gen_str = a['DESCR4']
    desc = a['DESCRLONG']  

    gen_arr = []
    gen_str = gen_str.replace(" or ", " & ")
    splt = gen_str.split(' & ')
    for str in splt:
        if len(str) > 0:
            gen_arr.append("'"+str+"'")
    
    gen_studies = "'{" + ','.join(gen_arr) + "}'"

    statement = f"INSERT INTO Course (subject, course_number, title, credits, General_Studies, description) VALUES ('{sub}', {cnum}, '{title}', {credits}, {gen_studies}, '{desc}');\n"
    f.write(statement)

f.close()













