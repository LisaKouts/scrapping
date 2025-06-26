from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
from random import randint
import numpy as np
import pandas as pd
import os
import json
from utils import askCHATGPT

class scrap:
    def __init__(self, url, li_username, li_password, apikey, path):
        self.url = url
        self.li_username, self.li_password = li_username, li_password
        self.driver = self.signin_linkedin()
        self.path = path
        self.apikey = apikey

    def signin_linkedin(self):
        driver = webdriver.Chrome()

        # Go to LinkedIn's login page
        driver.get("https://www.linkedin.com/login")

        # Find the username and password fields
        username = driver.find_element(By.NAME,"session_key")
        password = driver.find_element(By.NAME,"session_password")

        # Enter your credentials
        username.send_keys(self.li_username)
        password.send_keys(self.li_password)

        # Submit the login form
        password.send_keys(Keys.RETURN)
        time.sleep(30)

        return driver

    def get_soup(self, driver, url):
        driver.get(url)
        time.sleep(randint(5,15))

        page = driver.page_source
        return BeautifulSoup(page, 'html.parser')

    def find_all_jobs(self, soups):

        alljobs = []
        for s in soups:
            all_li = s.find_all('li')
            for li in all_li:
                try:
                    jobid = li['data-occludable-job-id']
                    alljobs.append('https://www.linkedin.com/jobs/view/'+jobid)
                except KeyError:
                    continue
        return alljobs
    
    def get_all_job_links(self):
        s = self.get_soup(self.driver, self.url)
        jobs_found = int(s.find('div', {'class':'jobs-search-results-list__subtitle'}).text.strip().split()[0])
        soups = []
        for i in np.arange(0,jobs_found,25): 
            link = self.url + "&start=" + str(i)
            soups.append(self.get_soup(self.driver, link))
        
        alljobs = self.find_all_jobs(soups)

        isExist = os.path.exists(self.path)
        if not isExist:

            # Create a new directory to save temporary files
            os.makedirs(self.path)

        path_to_save_jobs = os.path.join(self.path, 'jobs_linkedin.json')
        with open(path_to_save_jobs, 'w') as f:
            json.dump(alljobs, f)

        return alljobs
    
    def get_job_description(self, alljobs):

        job_list = []

        for j in alljobs:
            self.driver.get(j)
            time.sleep(randint(5,10))

            page = self.driver.page_source
            text = BeautifulSoup(page, 'html.parser')
            job_list.append(self.get_job_info(text, j))
            temp_save = pd.DataFrame(job_list, columns=['job', 'employer', 'language', 'Language requirements', 'location', 'ago', 'applicants', 'academic requirements', 'technical requirements', 'link', 'jobsite'])
            path_to_save_jobs = os.path.join(self.path, 'jobs_linkedin.xlsx')
            temp_save.to_excel(path_to_save_jobs)

        return pd.DataFrame(job_list, columns=['job', 'employer', 'language', 'Language requirements', 'location', 'ago', 'applicants', 'academic requirements', 'technical requirements', 'link', 'jobsite'])
    
    def get_job_info(self, text, job_url):

        try:
            description = text.find('p',{'dir':'ltr'})
            language, laguage_requirements, academic_requirements, technical_requirements = askCHATGPT(description, self.apikey)
            job_title = text.find('div',{'class':'job-details-jobs-unified-top-card__sticky-header-job-title'}).span.get_text().strip(' \n\n\n\n')
            info = text.find('div',{'class':'job-details-jobs-unified-top-card__primary-description-container'}).span.get_text().split('·')
            location, ago, applicants = info[0], info[1], info[2]
            employer = text.find("div",{"class":"job-details-jobs-unified-top-card__company-name"}).get_text().strip('\n')
            return [job_title, employer, language, laguage_requirements, location, ago, applicants, academic_requirements, technical_requirements, job_url, 'LinkedIn']
        except TypeError:
            print(text)


