from utils import scroll_down, split_text, get_language, askCHATGPT

from bs4 import BeautifulSoup
import pandas as pd
import math
import json
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from random import randint
import time

class vdab:

    def __init__(self, url, apikey, path = 'jobs'):
        '''
        Arguments:
        ----------
        url: string, link needs to point to the vdab vacatures website where the search term and location are already specified, example url "https://www.vdab.be/vindeenjob/vacatures?trefwoord=data%20analyst&locatie=3000%20Leuven&afstand=20&locatieCode=443&sort=standaard"
        '''
        self.url = url
        self.path = path
        self.apikey = apikey
        self.driver = self.signin_driver(self.url)

    def signin_driver(self, url):
        driver = webdriver.Chrome()

        # Go to LinkedIn's login page
        driver.get('https://www.vdab.be/')
        time.sleep(randint(5,15))
        return driver

    def get_contents_drive(self, link, scrollDown = False, implicit_wait = 10):
        self.driver.get(link)
        time.sleep(implicit_wait)

        if scrollDown:
            print('scrolling')
            scroll_down(self.driver)

        page = self.driver.page_source
        return BeautifulSoup(page, 'html.parser')

    def get_total_job_number(self, url):
        
        jobs_found = None
        implicit_wait = 5

        # if page does not fully load repeat until there are jobs found
        while jobs_found is None: # https://stackoverflow.com/questions/4606919/in-python-try-until-no-error
            try:
                soup = self.get_contents_drive(url, implicit_wait=implicit_wait)

                jobs_found = int(soup.find('div', {'class':"c-results__jobs u-text-meta"}).get_text().split()[0])
                alljobs_on_this_page=soup.find_all("div", {"class":"c-vacature__content-container"})

                num_pages = math.ceil(jobs_found / len(alljobs_on_this_page)) # subtract the fist page which has already been added
            except (ValueError,AttributeError) as e:
                implicit_wait += 5
                pass

        return num_pages

    # Iterate through pages

    def get_jobs_vdab(self):
        
        alljobs = []
        num_pages = self.get_total_job_number(self.url)
        print('num pages',num_pages)

        for i in range(1,num_pages+1):
            print('page', i)
            link = self.url+"&p="+str(i)
            implicit_wait = 5
            alljobs_on_this_page = []
            while len(alljobs_on_this_page) == 0:
                try:
                    soup = self.get_contents_drive(link, implicit_wait=implicit_wait)
                    alljobs_on_this_page=soup.find_all("div", {"class":"c-vacature__content-container"})
                    alljobs_on_this_page[0] # print to see if it exists
                    alljobs.append(alljobs_on_this_page)
                except IndexError as e:
                    # print(e)
                    implicit_wait += 5
            
        return alljobs
    
    def get_job_description(self, alljobs):

        requirements = None
        job_list = []
        unable_to_load = []

        for link in alljobs:
            implicit_wait = 5
            tries = 0

            while (requirements is None) and (tries < 3):
                text = self.get_contents_drive(link, implicit_wait=implicit_wait)
                try:
                    requirements = text.find('div', {'class':"c-job-section -about-vacature"}).get_text()
                    job_list.append(self.get_job_info(text, link))
                    temp_save = pd.DataFrame(job_list, columns=['job', 'employer', 'language', 'city', 'region', 'country', 'date_posted', 'link', 'jobsite', 'Language requirements', 'Academic requirements', 'Technical requirements'])
                    path_to_save_jobs = os.path.join(self.path, 'jobs_vdab.xlsx')
                    temp_save.to_excel(path_to_save_jobs)
                
                except AttributeError as e:
                    implicit_wait += 5
                    tries += 1
                    print(e, implicit_wait)
            if tries == 3:
                unable_to_load.append(link)

            requirements = None
        cnl = pd.DataFrame(unable_to_load)
        cnl.to_csv(os.path.join(self.path, 'jobs_could_not_load.csv'))
        self.driver.quit()

        return pd.DataFrame(job_list, columns=['job', 'employer', 'language', 'city', 'region', 'country', 'date_posted', 'link', 'jobsite', 'Language requirements', 'Academic requirements', 'Technical requirements'])
    
    def get_job_info(self, job, link):

        job_title = job.find("h1", {"class":"vej__detail-vacature-title c-h1"}).contents[-1].strip("\n      ")
        employer = job.find("div", {"class":"c-job-info-main__location"}).contents[1].string
        city = job.find("div", {"class":"c-job-info-main__location"}).contents[7].string
        date_posted = job.find("p", {"data-qa-id":"referentie-eerste-publicatie-datum"}).contents[1].string

        language, laguage_requirements, academic_requirements, technical_requirements = askCHATGPT(job.find('div', {'class':"c-job-section -about-vacature"}), self.apikey)

        return [job_title, employer, language, city, 'NA', 'Belgium', date_posted, link, 'VDAB', laguage_requirements, academic_requirements, technical_requirements]
    

    def unlist_get_href(self, alljobs):
        '''
        Attributes:
        ----------
        
        alljobs : output of get_jobs_vdab function
        '''
        job_list = []
        for i in range(0,len(alljobs)):
            for job in alljobs[i]:
                job_list.append("https://www.vdab.be" + job.a['href'])

        isExist = os.path.exists(self.path)
        if not isExist:

            # Create a new directory to save temporary files
            os.makedirs(self.path)

        path_to_save_jobs = os.path.join(self.path, 'jobs_vdab.json')
        with open(path_to_save_jobs, 'w') as f:
            json.dump(job_list, f)

        return job_list





