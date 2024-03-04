from requests import Session, utils
from requests_pkcs12 import Pkcs12Adapter
import re
import sqlite3
import smtplib, ssl
from email.message import EmailMessage
from datetime import datetime

smpt_port=465
smpt_server="smtp.gmail.com"        #Address of smtp server
email_sender="Sender@mail.com"      #Address that sends the mail
email_password="ChangeMe"           #Password for that mail
email_receiver="Receiver@mail.com"  #Mail that gets the Notification     
cer_filename='/EduCert.p12'         #FileName of Certificate
cer_password='ChangeMe'             #Password of Certificate
username="abc-def"                  #username for the website
password="password123"              #password for the website


Noten = []
Titel = []
with Session() as s:
    #print("Versuche einzuloggen...")
    s.mount('https://secure.th-owl.de', Pkcs12Adapter(pkcs12_filename=cer_filename, pkcs12_password=cer_password))
    response = s.post('https://secure.th-owl.de/studi/rds?state=user&type=1&category=auth.login&startpage=portal.vm&breadCrumbSource=portal', data={'asdf': username,'fdsa': password,'submit': 'login'})
    if(response.status_code==200):
        #print("eingloggt!")
        response = s.get("https://secure.th-owl.de/studi/rds?state=change&type=1&moduleParameter=studyPOSMenu&nextdir=change&next=menu.vm&subdir=applications&xml=menu&purge=y&navigationPosition=functions%2CstudyPOSMenu&breadcrumb=studyPOSMenu&topitem=functions&subitem=studyPOSMenu")
        if(response.status_code==200):
            #print("Seite: Prüfungsverwaltung...")
            #Link finden
            start = response.text.index("Leistungs&uuml;bersicht")
            temp = response.text[int(start): int(start)+400]
            start = temp.index('href="')
            end = temp.index('"  title=""')
            temp = temp[int(start)+6: int(end)]
            temp = temp.replace("amp;", "")
            response =s.get(temp)
            if(response.status_code==200):
                #print("Seite: Leistungsübersicht...")
                start = response.text.index("Abschluss 84 Bachelor</a>")
                temp = response.text[int(start): int(start)+500]
                start = temp.index('href="')
                end = temp.index('" title="Leistungen für Abschluss')
                temp = temp[int(start)+6: int(end)]
                temp = temp.replace("amp;", "")
                response =s.get(temp)
                if(response.status_code==200):
                    #print("Erfolgreich Noten gelesen!")
                    temp = response.text
                    start = temp.index('Bemerkungen')
                    #temp = response.text[int(start): int(start)+400]
                    stringset = temp.split("<tr>")
                    beinoten = False
                    NotenListe = []
                    for string in stringset:
                        if "PNr." in string:
                            continue
                        if beinoten:
                            NotenListe.append(string)
                        if "Darstellung von Credits/Noten in den Konten" in string:
                            beinoten = True
                    
                    

                    start = NotenListe[0].index('width="25%"')
                    for string in NotenListe:
                        #temp = ' '.join(NotenListe.split())
                        temp = string
                        temp= temp.replace("\n", "")
                        temp= temp.replace("\t", "")
                        temp = re.sub("[\(\<].*?[\)\>]", "", temp)
                        temp = temp.replace("  ", "")
                        #print(temp)
                        templist = temp.split(" ")

                        #print(templist)
                        #print(templist[4])
                        Nummer = False
                        Note = False
                        TitelString = ""
                        for a in templist:
                            if a.startswith("1,") or a.startswith("2,") or a.startswith("3,") or a.startswith("4,") or a.startswith("5,"):
                                Note = True
                                Nummer = False
                                Noten.append(a)
                                Titel.append(TitelString)
                                TitelString = ""

                            if(Nummer):
                                TitelString = TitelString + " " + a
                            if (a.isdigit()):
                                b = int(a)
                                if(b>=1000 and b<99999):
                                    Nummer=True
                                    Note = False


Leistung = {}
for i in range(0, len(Noten)):
    Leistung.update({Titel[i]:Noten[i]})

neueNote = False
neueNoteName = ""
neueNoteValue = 0
#in DB schreiben                                                            
conn = sqlite3.connect("/database.db")
cur = conn.cursor()
data = conn.execute("SELECT Name,Note FROM Noten;")
for Note in Leistung:
    found = False
    data = conn.execute("SELECT Name,Note FROM Noten;")
    for row in data:
        #print(Note + " | "+ row[0])
        if(row[0] == Note):
            found = True
    if(not found):
        conn.execute("INSERT INTO Noten (Name, Note) VALUES('"+ Note +"', '"+ Leistung[Note] +"');")
        neueNote = True
        neueNoteName = Note
        neueNoteValue = Leistung[Note]
        conn.commit()

now = datetime.now()
print("Grades scraped around::", now)
#neueNote=True


if(neueNote):
    subject= "new grade!"
    body="new grade: "+ neueNoteName + " : " + str(neueNoteValue)
    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smpt_server, smpt_port, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
        print("mail was send!")



if(False):
    print("---------------------------")
    for a in Leistung:
        print(a +" : "+ Leistung[a])
    print("---------------------------")