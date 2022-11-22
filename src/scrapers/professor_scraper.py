import requests as req

class_numbers = []

def addClassNumber(obj):
    for a in obj["classes"]:
        clas = a["CLAS"]
        snum = clas["CLASSNBR"]
        class_numbers.append(snum)


semester = "Fall 2022"

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


# 1. GET CLASS NUMBERS
print ("Getting class numbers...")

while len(r.text) > 600:
    obj = r.json()
    addClassNumber(obj)

    url = "https://eadvs-cscc-catalog-api.apps.asu.edu:443/catalog-microservices/api/v1/search/classes"
    r = req.get(url, headers=headers, cookies=cookies, params=params)



# 2. GET PROFESSOR ID FROM CLASS NUMBER
print ("Getting professor IDs...")

professors = []
# Professor is a tuple: (name, type, class_number)

for class_number in class_numbers:
    url = f"https://api.myasuplat-dpl.asu.edu:443/api/class/2227/{class_number}?include=instructor"

    r = req.get(url, headers=headers, cookies=cookies)
    obj = r.json()
    
    if( obj["meetings"] and obj["meetings"][0]["instructors"] and obj["meetings"][0]["instructors"][0]["iSearchUrl"] != None):
        professors.append((obj["meetings"][0]["instructors"][0]["firstName"] + " " + obj["meetings"][0]["instructors"][0]["lastName"],
                           obj["meetings"][0]["instructors"][0]["iSearchUrl"].split("/")[-1], 
                           class_number))



# 3. GET PROFESSOR INFORMATION
print ("Getting professors information...")


with open("professor_statements.sql", "w") as f:
    for professor in professors:
        url = f"https://search.asu.edu:443/api/v1/webdir-profiles/faculty-staff?&sort-by=_score_desc&query={professor[0]}&page=1&size=6"
        r = req.get(url, headers=headers, cookies=cookies)
        obj = r.json()

        for prof in obj["results"]:
            if prof["eid"]["raw"] == professor[1]:

                #print ("prof", prof)
                if "email_address" in prof:
                    email = prof["email_address"]["raw"]
                else:
                    email = "None"

                if "phone" in prof:
                    phone = prof["phone"]["raw"]
                else:
                    phone = "None"

                if "bio" in prof:
                    bio = prof["bio"]["raw"]
                    if bio is not None:
                        bio = bio.replace("'","''")
                else:
                    bio = "None"

                if "website" in prof:
                    website = prof["website"]["raw"]
                else:
                    website = "None"

                prof_name = professor[0].replace("'", "''")

                statement_prof = f"INSERT INTO Professor (professor_id, name, email, phone_number, bio, website) VALUES ({professor[1]}, '{prof_name}', '{email}', '{phone}', '{bio}', '{website}');\n".replace("'None'", "NULL")

                statement_teaches = f"INSERT INTO Teaches (professor_id, section_number) VALUES ('{professor[1]}', {professor[2]});\n"

                f.write(statement_prof + statement_teaches)

                break
