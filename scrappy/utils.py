import pandas as pd
import langid
import time
from random import randint
from openai import OpenAI

def scroll_down(driver):
    """A method for scrolling the page. 
    Source: https://stackoverflow.com/questions/48850974/selenium-scroll-to-end-of-page-in-dynamically-loading-webpage 
    
    Arguments:
    ---------
    driver: selenium webdirver object
    time_sleep: delay time to load html code
    
    """

    # Get scroll height.
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:

        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        time.sleep(randint(5,20))
        # driver.implicitly_wait(randint(10,20))

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:

            break

        last_height = new_height

def split_text(text):
    '''
    -- replaced by chatgpt
    source: https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
    follows a get_text() function
    returns a list of sentences
    '''
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return ('\n'.join(chunk for chunk in chunks if chunk)).split('\n')

def get_language(text):
    '''
    -- replaced by chatgpt
    Input: list of text chunks
    Returns: average language over all chunks, and sentences related to languages
    '''
    languages = []
    lang_requirements = []
    for sentence in text:

        l = langid.classify(sentence)
        languages.append(l)
        if ('Engels' in sentence) or ('Nederlands' in sentence) or ('English' in sentence) or ('German' in sentence):
            lang_requirements.append(sentence)

    return pd.DataFrame(languages).groupby(0).sum().sort_values([1]).index[0], lang_requirements

def askCHATGPT(job_description, apikey):
    '''
    job_description should be of type 'bs4.element.Tag' to extract the text
    '''
    apikey = apikey.strip(' ')
    client = OpenAI(api_key=apikey)

    response = client.responses.create(
        model= "gpt-4.1",
        input= "In what language is this job decription written? Please answer with a single word that is the identified language. "+job_description.get_text()
    )

    language = response.output_text

    response = client.responses.create(
        model= "gpt-4.1",
        input= "Please extract the sentence that specifies the language requirements of the following job description. Please only include the extracted sentence in your answer. "+job_description.get_text()
    )

    laguage_requirements = response.output_text

    response = client.responses.create(
        model= "gpt-4.1",
        input= "What academic degrees do I need to have for the following job? Return only a list with the degree names without making a sentence. "+job_description.get_text()
    )

    academic_requirements = response.output_text

    response = client.responses.create(
        model= "gpt-4.1",
        input= "What are the technical skills for the following job? Return only a list of skills without making a sentence. "+job_description.get_text()
    )

    technical_requirements = response.output_text

    return language, laguage_requirements, academic_requirements, technical_requirements


