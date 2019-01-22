from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import datetime as dt
import json

username =''
email = ''

# Initiate headless driver for deployment
browser = Browser("chrome", executable_path="chromedriver", headless=True)

def load_browser(browser, url):
    browser.visit(url)

    return browser

def login():
    login_url = "https://wwwtestaccounts.careerbuilder.com/share/login.aspx?next=https%3a%2f%2fwwwtestaccounts.careerbuilder.com%2fshare%2foauth2%2fauth.aspx%3fclient_id%3dCd03edb6f%26elui%3d1%26redirect_uri%3dhttps%25253a%25252f%25252frecruitment-staging.ace.careerbuilder.com%25252fauthCallback%25253foriginalUrl%25253d%2525252Fuserinfo%26response_type%3dcode%26scope%3dopenid&elui=1&client_id=Cd03edb6f"
    
    data = ""

    try:
        load_browser(browser, login_url)
            
        browser.fill_form({"cbsys_login_email": "Personified.Tester3@careerbuilder.com", "cbsys_login_password": "c0lumbusrocks!"}, form_id=None, name=None)
        browser.find_by_id('btnsigninemp').click()
        browser.is_text_present("username", wait_time=0.5)
        
        username = get_data_as_json(browser)["userInfo"]["first_name"]
        email = get_data_as_json(browser)["userInfo"]["email"]

        data = "Email is {} and User is {}".format(username, email)

        print(data)

    except:
        print("error happened on login")

    return data

def get_data_as_json(browser):
    
    html = browser.html
    api_result = BeautifulSoup(html, "html.parser")

    try:
        json_string = api_result.select_one("body").text

    except AttributeError:
        return None

    return json.loads(json_string)

def actions_used_by_recruiter():
    array_dic = []
    ### Total Usage:
    api_urls = [
        'https://recruitment-staging.ace.careerbuilder.com/api/cba/roi/actions/20180225/20190124',
        'https://recruitment-staging.ace.careerbuilder.com/api/cba/roi/searches/20180225/20190124',
        'https://recruitment-staging.ace.careerbuilder.com/api/cba/roi/emails/20180224/20190123',  
        'https://recruitment-staging.ace.careerbuilder.com/api/cba/roi/intakes/20180224/20190123',
        'https://recruitment-staging.ace.careerbuilder.com/api/cba/roi/campaigns-sent/20180224/20190123',
    ]

    for api_url in api_urls:
        load_browser(browser, api_url)
        array_dic.append(get_data_as_json(browser))

    action_description = { "sd_searches": "Supply & Demand Searches", "intakes_started": "Intakes Started", "actions_taken": "Actions Taken", "campaigns_sent": "Campaigns Sent", "emails_sent": "Talent Network Emails Sent" }

    print(action_description)

    data = pd.DataFrame.from_dict(array_dic[0], orient='index')
    data = data.append(pd.DataFrame.from_dict(array_dic[1], orient='index'))
    data = data.append(pd.DataFrame.from_dict(array_dic[2], orient='index'))
    data = data.append(pd.DataFrame.from_dict(array_dic[3], orient='index'))
    data = data.append(pd.DataFrame.from_dict(array_dic[4], orient='index'))

    data = data.dropna()

    data = data.rename(columns={0:"values"})
    data["values"] = pd.to_numeric(data["values"])

    data.sort_values(by="values", ascending=False)

    response_ideas = [
        "Total usage since January 2018 is...",
    ]

    for index, row in data.reset_index().iterrows():
        response_ideas.append("{}: {:,}".format(action_description[row[0]], row[1]))
    
    print(response_ideas)

    return response_ideas

def most_viewed_resumes():

    ### Job Positions most viewed:
    api_url = 'https://recruitment-staging.ace.careerbuilder.com/api/cba/roi/resumes-stats/20180224/20190123'
    load_browser(browser, api_url)
    data = pd.DataFrame(get_data_as_json(browser))
    data["position"] = data["onet_name"].str.split(" - ", n = 1, expand = True)[0]
    data["city"] = data["onet_name"].str.split(" - ", n = 1, expand = True)[1]
    data = data.drop(columns=["onet_name"])

    position_1 = data.iloc[0]["position"]
    city_1 = data.iloc[0]["city"]
    viewed_1 = data.iloc[0]["resume_viewed"]
    inventory_1 = data.iloc[0]["resume_inventory"]

    position_2 = data.iloc[1]["position"]
    city_2 = data.iloc[1]["city"]
    viewed_2 = data.iloc[1]["resume_viewed"]
    inventory_2 = data.iloc[1]["resume_inventory"]

    position_3 = data.iloc[2]["position"]
    city_3 = data.iloc[2]["city"]
    viewed_3 = data.iloc[2]["resume_viewed"]
    inventory_3 = data.iloc[2]["resume_inventory"]

    response_ideas = [
        "Top 3 most viewed resumes are.",
        "{}, city: {}, with {} views, from an inventory of {:,}.".format(position_1, city_1, viewed_1, inventory_1),
        "{}, city: {}, with {} views, from {:,}.".format(position_2, city_2, viewed_2, inventory_2),
        "{}, city: {}, with {} views, from {:,}.".format(position_3, city_3, viewed_3, inventory_3)
    ]
    
    print(response_ideas)

    return response_ideas


def get_candidate_growth():
    
    ### Candidate Growth:
    api_url = 'https://recruitment-staging.ace.careerbuilder.com/api/cba/roi/candidates-count/20180101/20190123'
    load_browser(browser, api_url)
    data = pd.DataFrame(get_data_as_json(browser))
    data["mycand_member_growth"] = pd.to_numeric(data["mycand_member_growth"])
    data['yearmonth'] = pd.to_datetime(data['yearmonth'], format="%Y%m")
    data["month"] = data["yearmonth"].dt.month_name()
    data["year"] = data["yearmonth"].dt.year

    first_date = "{} {}".format(data.iloc[0]["month"], data.iloc[0]["year"])
    current_growth = data.iloc[-1]["mycand_member_growth"]
    data.sort_values(by="mycand_member_growth", ascending=False, inplace=True)
    total = np.sum(data["mycand_member_growth"])

    high_pitch = "{} {}".format(data.iloc[0]["month"], data.iloc[0]["year"])
    high_pitch_value = data.iloc[0]["mycand_member_growth"]
    high_pitch_value_mean = (high_pitch_value / total) * 100

    lower_pitch = "{} {}".format(data.iloc[-1]["month"], data.iloc[-1]["year"])

    response_ideas = [
        "Since {} the growth in candidates has been variable with".format(first_date), 
        "a high pitch in {} with {:.2f}% and the lowest in {}".format(high_pitch, high_pitch_value_mean, lower_pitch),
        "currently representing a candidate growth of {}".format(current_growth)
    ]
    
    return response_ideas
