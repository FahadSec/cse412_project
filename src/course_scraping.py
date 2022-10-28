import requests as req
import json

undergrad_url = "https://eadvs-cscc-catalog-api.apps.asu.edu:443/catalog-microservices/api/v1/search/courses?refine=Y&campusOrOnlineSelection=A&searchType=all&term=2227&level=undergrad"
grad_url = "https://eadvs-cscc-catalog-api.apps.asu.edu:443/catalog-microservices/api/v1/search/courses?refine=Y&campusOrOnlineSelection=A&searchType=all&term=2227&level=grad"


cookies = {"asuCookieConsent": "true"}
headers  = {
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


undergrad_req = req.get(undergrad_url, headers=headers, cookies=cookies)
grad_req = req.get(grad_url, headers=headers, cookies=cookies)

obj = undergrad_req.json()
grad_obj = grad_req.json()

obj.extend(grad_obj) # combine both undergrad and grad objects


with open("statements.db", "w") as f:
    for a in obj:
        sub = a['SUBJECT']
        cnum = a['CATALOGNBR']
        title = a['COURSETITLELONG']
        credit = 0
        if 'UNITSMAXIMUM' in a.keys():
            credit = a['UNITSMAXIMUM']
        gen_str = a['DESCR4']
        desc = a['DESCRLONG'].replace("'","''")

        gen_arr = []
        gen_str = gen_str.replace(" or ", " & ")
        splt = gen_str.split(' & ')
        for str in splt:
            if len(str) > 0:
                gen_arr.append("'"+str+"'")

        gen_studies = "'{" + ','.join(gen_arr) + "}'"

        statement = f"INSERT INTO Course (subject, course_number, title, credits, General_Studies, description) VALUES ('{sub}', {cnum}, '{title}', {credit}, {gen_studies}, '{desc}');\n"
    f.write(statement)
