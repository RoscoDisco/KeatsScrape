'''
Author: Ross Henry
Date:4/2/2018
'''

import requests
import argparse
from bs4 import BeautifulSoup as BS
import os
import re

def login(creditations,session):
    url='https://keats.kcl.ac.uk/login/index.php'
    r = session.post(url, data=creditations)
    try:
        if r.headers['Access-Control-Allow-Origin'] == 'https://login-keats.kcl.ac.uk':
            print('Login Successful')
            return r
    except:
        print('Username or password is incorrect. Check and retry')

def main():
    # Parser for arguments
    pr = argparse.ArgumentParser()
    pr.add_argument("-pw", "--password", help="Password for Kings")
    pr.add_argument("-un", "--username", help="Username for Kings")
    pr.add_argument("-wd", "--workingDirectory", default=os.getcwd())


    args = pr.parse_args()
    password = args.password
    username = args.username
    cwd = args.workingDirectory
    creditations = {'username': username, 'password': password}

    # Set up session
    with requests.Session() as session:
        htmlData = login(creditations, session)
        dashboardData = BS(htmlData.text, 'html.parser')
        courses = dashboardData.find_all("h2", class_= 'title')
        # Print courses with index
        for i in range(0,len(courses)-1):
            print('%d: %s'%(i, courses[i].a.get('title')))

        course = int(input('Index of course\n>>>'))
        print('%s Selected' %courses[course].a.get('title'))
        courseURL = courses[course].a.get('href')
        courseData = session.get(courseURL)
        courseHTML = BS(courseData.text, 'html.parser')
        sections =courseHTML.find_all("li", class_= 'section')
        for section in sections:
            # Skip over 'Not available'
            try:
                if section.find('h3').get_text() == 'Not available':
                    continue
            except:
                pass
            #Folder created
            pathway = cwd + '/' + section.get('aria-label')
            if not os.path.exists(pathway):
                os.makedirs(pathway)
                print('Folder Created: ' + section.get('aria-label'))
            else:
                print('Folder exists')

            files = section.find_all("li", class_='activity')
            for filex in files:
                try:
                    fileName = filex.find('span').get_text()
                except AttributeError:
                    fileID = filex.find('a')
                # Folder
                if filex.find('img', src='https://keats.kcl.ac.uk/theme/image.php/keats/folder/1516692714/icon'):
                    fileType = 'folder - This is still to be supported'
                    print(fileType)
                # PDF file
                elif (filex.find('img', src=re.compile('pdf'))):
                    fileType = 'pdf'
                    filePathway = pathway+'/'+fileName +'.'+fileType
                    fileURL = filex.find('a').get('href') + '&redirect=1'
                    if not os.path.exists(pathway+'/'+fileName +'.'+fileType):
                        fileData = session.get(fileURL)
                        with open(filePathway, 'wb') as f:
                            f.write(fileData.content)
                        print('File created: %s' % fileName)
                    else:
                        print('File exists')

                else:
                    fileType = 'File to be supported'
                    print(fileType)




if __name__ == '__main__':
    main()
