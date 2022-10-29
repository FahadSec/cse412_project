import requests as req
import json

class_numbers = []

def addClassNumber(obj):
    for a in obj["hits"]["hits"]:
        clas = a['_source']
        snum = clas['CLASSNBR']
        class_numbers.append(snum)


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

# GET CLASS NUMBERS

print ("Getting class numbers...")

#for _ in range(1): ############### TODO RETURN BACK TO NORMAL
while len(r.text) > 600:
    #print(obj["hits"]["hits"][0]["_source"]["SUBJECT"])
    obj = r.json()
    addClassNumber(obj)

    url = f"https://eadvs-cscc-catalog-api.apps.asu.edu:443/catalog-microservices/api/v1/search/classes?&refine=N&campusOrOnlineSelection=A&honors=F&promod=F&searchType=all&term={semc}&scrollId={scrollId}"
    r = req.get(url, headers=headers, cookies=cookies)




# GET PROFESSOR ID FROM CLASS NUMBER
print ("Getting professor IDs...")

# professor: (name, type, class_number)
professors = []

for class_number in class_numbers:
    url = f"https://api.myasuplat-dpl.asu.edu:443/api/class/{semc}/{class_number}?include=instructor"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:106.0) Gecko/20100101 Firefox/106.0", "Accept": "*/*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "https://catalog.apps.asu.edu/", "Origin": "https://catalog.apps.asu.edu", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-site", "Te": "trailers"}

    r = req.get(url, headers=headers)
    obj = r.json()
    
    if( obj["meetings"] and obj["meetings"][0]["instructors"] and obj["meetings"][0]["instructors"][0]["iSearchUrl"] != None):
        professors.append((obj["meetings"][0]["instructors"][0]["firstName"] + " " + obj["meetings"][0]["instructors"][0]["lastName"],obj["meetings"][0]["instructors"][0]["iSearchUrl"].split("/")[-1], class_number))



# GET PROFESSOR INFORMATION
print ("Getting professors information...")

#professor = professors[0]

#print ("professor", professor)

cookies = {"asuCookieConsent": "true"}
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:106.0) Gecko/20100101 Firefox/106.0", "Accept": "application/json, text/plain, */*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "https://search.asu.edu/?search-tabs=web_dir_faculty_staff&q=miller", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Te": "trailers"}


with open("professor_statements.db", "w") as f:
    for professor in professors:
        url = f"https://search.asu.edu:443/api/v1/webdir-profiles/faculty-staff?&sort-by=_score_desc&query={professor[0]}&page=1&size=6"
        r = req.get(url, headers=headers, cookies=cookies)
        obj = r.json()

        for prof in obj["results"]:
            if prof["eid"]["raw"] == professor[1]:

                #print ("prof", prof)
                if "email" in prof:
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

                statement_prof = f"INSERT INTO Professor (professor_id, name, email, phone_number, bio, website) VALUES ({professor[1]}, '{professor[0]}', '{email}', '{phone}', '{bio}', '{website}');\n".replace("'None'", "NULL")

                statement_teaches = f"INSERT INTO Teaches (professor_id, section_number) VALUES ('{professor[1]}', {professor[2]});\n"

                f.write(statement_prof + statement_teaches)
                break
