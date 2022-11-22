import requests as req

url = "https://eadvs-cscc-catalog-api.apps.asu.edu:443/catalog-microservices/api/v1/search/courses"

params={
        "refine":"Y",
        "term":"2227",
        "level":""
}

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
    "Te": "trailers"
}

params["level"] = "undergrad"
undergrad_req = req.get(url, headers=headers, cookies=cookies, params=params)

params["level"] = "grad"
grad_req = req.get(url, headers=headers, cookies=cookies, params=params)

obj = undergrad_req.json()
grad_obj = grad_req.json()

obj.extend(grad_obj) # combine both undergrad and grad objects

with open("course_statements.sql", "w") as f:
    for a in obj:
        sub = a["SUBJECT"]
        cnum = a["CATALOGNBR"]
        number_ext = ""
        if len(cnum) > 3:
            temp = cnum
            cnum = temp[:3]
            number_ext = temp[3:]

        title = a["COURSETITLELONG"].replace("'","''")
        credit = 0
        if "UNITSMAXIMUM" in a.keys():
            credit = a["UNITSMAXIMUM"]
        gen_studies = a["DESCR4"]
        desc = a["DESCRLONG"].replace("'","''")

        statement = f"INSERT INTO Course (subject, course_number, number_ext, title, credits, General_Studies, description) VALUES ('{sub}', {cnum}, '{number_ext}', '{title}', {credit}, '{gen_studies}', '{desc}');\n"
        f.write(statement)
