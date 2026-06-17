import email
import imaplib
import os
from typing import Any

from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote

import scraper
import ai_scorer as scorer
import report_generator as reporter

tempList: list[Any] = []

def main():
    data = getEmailsFromIMAP()
    output = parseEmailsList(data)
    print(f"Output: {len(output)}")
    flatOutput = flattenTheList(output)
    print(f"flatOutput: {len(flatOutput)}")
    outputWithJDs = fetchAllJDs(flatOutput)
    outputWithScores = fetchMatchScores(outputWithJDs)
    reporter.generateAndSaveReport(outputWithScores)
    markEmailsAsRead(outputWithScores)
    # myprint(outputWithScores)


def myprint(output):
        for o in output:
            print(f"\nMeta:{o['meta']}"
                  f"\nSTR: {o['str']}"
                  f"\nHREF: {o['href']}"
                  f"\nJD Length: {len(o['jd'])}"
                  f"\nMatchScore:{o['oScore']}"
                  f"\nMatches Well: {o['matches_well']}"
                  f"\nMissing: {o['missing']}"
                  f"\nMailID: {o['mail_id']}"
                  , "-x-"*20)
        print("--" * 100)

def markEmailsAsRead(data: list):
    mailIds = set()
    metas = set()
    i = 0
    imap = imapConn()
    imap.select('inbox')
    for o in data:
        mailIds.add(o['mail_id'])
        metas.add(o['meta'])
    for mail_id in mailIds:  # set() deduplicates
        imap.uid('store',mail_id, '+FLAGS', '\\Seen')
        i = i + 1
    imap.close()
    imap.logout()
    print("--" * 100)
    print(f"Marked {i} emails as read.\n\n", "\n".join(metas))
    print("--" * 100)

def fetchMatchScores(output) -> list[dict]:
    returnList = []
    llmFailed = []
    resumeContent = scorer.getFileContent('RESUME.md')
    print("--" * 100)
    print("Matching Scores: ", end='')
    for o in output:
        matchResult = scorer.setMyPrompt(o['jd'], resumeContent)
        matchResult = scorer.getLLMMatchResults(matchResult)
        matchResult = scorer.sanitiseLLMResult(matchResult)
        if matchResult is not None:
            o.update({
                'oScore': matchResult['scores']['overall']
                , 'matches_well': "\n".join(matchResult['what_matches_well'])
                , 'missing': "\n".join(matchResult['what_is_missing'])
            })
            returnList.append(o)
            print("|", end='')
        else:
            llmFailed.append(o['href'])

    if len(llmFailed) > 0:
        print("--" * 100)
        print("\nLLM Failed for the following links:")
        print("\n".join(llmFailed))

    print("\n", "--" * 100)
    return returnList



def flattenTheList(output):
    returnList = []
    for item in output:
        for o in item['links']:
            if len(o['href'])>30:
                returnList.append({'meta': item['meta'], 'str': o['str'], 'href': o['href'], 'mail_id': item['mail_id']})
    return  returnList


def fetchAllJDs(output):
    returnValue = []
    notReturned = []
    print("Scraping JDs: ", end='')
    for o in output:
        print(".", end="")
        jd = scraper.getIIMJobsJD(o['href'])
        o.update({'jd': jd})
        if jd not in ['APPLIED', 'ERROR_TIMEOUT', 'NO_LINK', 'NOT_SCRAPABLE']:
            returnValue.append(o)
        else:
            notReturned.append(o)
    print("\n", "--" * 100, "\n\nNot Returned:")
    for x in notReturned:
        print(f"{x['href']}->{x['jd']}")
    print("--" * 100, "\n\n")
    return returnValue


def setEnvVariables():
    load_dotenv()
    emailId = os.getenv('YAHOO_EMAIL')
    password = os.getenv('YAHOO_APP_PASSWORD')
    return emailId, password

def imapConn():
    emailP, passwordP = setEnvVariables()
    imap = imaplib.IMAP4_SSL('imap.mail.yahoo.com', 993)
    if emailP is None or passwordP is None:
        print("Email or password not set in environment variables.")
        exit(1)
    imap.login(emailP, passwordP)
    return imap

def getEmailsFromIMAP() -> list[dict]:
    imapObj = imapConn()
    imapObj.select('inbox')
    status, messages = imapObj.uid('search',None,'UNSEEN', 'FROM info@iimjobs.com')
    messages = messages[0].split()
    mailList = []
    for mail in messages:
        metaContent = ''
        bodyContent = ''
        _, msg = imapObj.uid('fetch',mail, '(BODY.PEEK[])')
        for response in msg:
            if isinstance(response, tuple):
                msgDecoded = email.message_from_bytes(response[1])
                metaContent = (f"Date: {datetime.strptime(msgDecoded["date"].split(" (")[0], "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S")}, "
                               f"From: {msgDecoded["from"]}, "
                               f"Sub: {msgDecoded["subject"]}")
                if msgDecoded.is_multipart():
                    for part in msgDecoded.walk():
                        if part.get_content_type() == "text/html":
                            bodyContent = part.get_payload(decode=True).decode('utf-8')

        mailList.append({'meta': metaContent, 'body': bodyContent, 'mail_id': mail})
        # if len(mailList)>3:
        #     break
    imapObj.close()
    return mailList


def parseEmailsList(mailListDict):
    returnMailList = []
    for mail in mailListDict:
        metaContent = mail['meta']
        bodyContent = mail['body']
        fetchedLinks = fetchLinksListForThisEmail(bodyContent)
        # print("#" * 100)
        # print(bodyContent)
        # print("*" * 100)
        # print("<A>")
        # print(fetchedLinks)
        # print("|" * 100)
        fetchedLinks = filterLinks(fetchedLinks)
        returnMailList.append({'meta': metaContent, 'body': bodyContent, 'links': fetchedLinks, 'mail_id': mail['mail_id']})
    return returnMailList


def filterLinks(fetchedLinks) -> list:
    global tempList
    # tempList = []
    returnList = []
    for link in fetchedLinks:
        redirectLink = parse_qs(urlparse(link['href']).query).get("redirect", [None])[0]
        if redirectLink is not None and '/j/' in redirectLink:
            if redirectLink is not None:
                redirectLink = redirectLink[:redirectLink.find('?')]
            if redirectLink not in tempList:
                tempList.append(redirectLink)
                returnList.append({'href': redirectLink, 'str': link['str']})
        if link['href'] is not None and '%2Fj%2F' in link['href']:
            extractionStart = link['href'].find('/CL0/')
            extractedEnd = link['href'].find('/', extractionStart+5)
            extractedLink = unquote( link['href'][extractionStart+5:extractedEnd] )
            if extractedLink not in tempList:
                tempList.append(extractedLink)
                returnList.append({'href': extractedLink, 'str': link['str']})
    return returnList


def fetchLinksListForThisEmail(bodyContent):
    linksList = []
    bsObj = BeautifulSoup(bodyContent, 'html.parser')
    for eachAnchor in bsObj.find_all('a'):
        linksList.append({'str': eachAnchor.string, 'href': eachAnchor.get('href')})
    return linksList

if __name__ == "__main__":
    main()