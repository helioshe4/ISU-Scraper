from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from Row import Row

s = Service("C:\Program Files (x86)\chromedriver.exe")
driver = webdriver.Chrome(service=s)
driver.get("https://shorttrack.sportresult.com/")
driver.minimize_window()

def get_sec(time_str):
    """Get seconds from time."""
    try:
        m, s, ms = time_str.split(':')
        return float(m) * 60 + float(s) + float(ms) * 0.001
    except:
        return ' '.join(time_str.split())

def get_season():
    years = input("Enter the season you would like to look at in the form Year1-Year2 (e.g. 2021-2022): ")
    x = driver.find_element(By.NAME, 'sea')
    drop = Select(x)
    try:
        drop.select_by_visible_text(f'{years} SEASON') # selects the season using dropdown button
        return years
    except NoSuchElementException:
        print("Please enter a valid season in the form previously shown.")
        main()

def get_competition_urls(loc_year_type_list):
    competition_url_list = []
    elems1 = driver.find_elements(By.PARTIAL_LINK_TEXT, 'ISU')
    elems2 = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Olympic')
    elems3 = driver.find_elements(By.PARTIAL_LINK_TEXT, 'World')
    elems4 = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Championships')
    elems5 = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Universiade')
    elems6 = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Invitational')
    elems7 = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Winterfest')
    elems = elems1 + elems2 + elems3 + elems4 + elems5 + elems6 + elems7
    elems = list(dict.fromkeys(elems))
    for element in elems:
        loc_year_type_list.append(element.text)  # adds the text of the link to the list that contains location, year, type
        competition_url_list.append(element.get_attribute("href")) # adds the url of the link to the comp url list
    return competition_url_list

# takes the url for a comp and returns a dictionary with all the race waves as the key, and the distance as the value
def men_get_races(comp_url, race_urls):
    driver.get(comp_url)
    home_button = driver.find_element(By.LINK_TEXT, 'HOME') # clicks the home button once it gets to the link, to access all the links
    home_button.click()

    elems = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Men') # selects all links with instances of Men
    elems_relay = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Relay') # selects all links with instances of Relay

    elems = set(elems) - set(elems_relay) # keeps elements with only Men and no Relay
    for element in elems:
        if '1500' in element.text:
            race_urls.update({element.get_attribute("href"): 1500})  # extracts url from each element
        elif '1000' in element.text:
            race_urls.update({element.get_attribute("href"): 1000})  # extracts url from each element
        else:
            race_urls.update({element.get_attribute("href"): 500})  # extracts url from each element

    return race_urls # dictionary

def women_get_races(comp_url, race_urls):
    driver.get(comp_url)
    home_button = driver.find_element(By.LINK_TEXT, 'HOME') # clicks the home button once it gets to the link, to access all the links
    home_button.click()

    elems = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Women') # selects all links with instances of Men
    elems_relay = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Relay') # selects all links with instances of Relay

    elems = set(elems) - set(elems_relay) # keeps elements with only Men and no Relay
    for element in elems:
        if '1500' in element.text:
            race_urls.update({element.get_attribute("href"): 1500})  # extracts url from each element
        elif '1000' in element.text:
            race_urls.update({element.get_attribute("href"): 1000})  # extracts url from each element
        else:
            race_urls.update({element.get_attribute("href"): 500})  # extracts url from each element

    #print(race_urls)
    return race_urls # dictionary

def scrape_round(round_url, race_dict, list_of_rows, loc_year_type):
    html_text = requests.get(round_url).text
    soup = BeautifulSoup(html_text, 'lxml')

    heat_num = 0
    distance = race_dict[round_url]
    round = ' '.join(soup.find('div', attrs={'class': 'tabbuttonsel'}).text.split()) + ' ' + str(heat_num)
    names = soup.find_all('td', attrs={'style': 'width:200px;'}) # finds all instances of skaters' names in HTML code
    placement = soup.find_all('td', attrs={'style': 'width:30px;'})
    placement = placement[0::2] # removes every second element which is the start position, so only the placement remains
    countries = soup.find_all('td', attrs={'style': 'width:80px;'}) # finds all instances of skaters' countries in HTML code
    times = soup.find_all('td', attrs={'style': 'width:40px;'}) # finds all instances of skaters' times in HTML code
    splits_urls = get_splits_urls(round_url)
    splits = []
    for url in splits_urls:
        splits = scrape_splits(url, splits)

    for i in range(len(names)): # adds the names into a list
        if ' '.join(placement[i].text.split()) == '1': # checks if its a new heat by checking if the next person won
            heat_num += 1
        if heat_num >= 10:
            round = round[:-2] + str(heat_num) # removes the last char off round and adds heat_num to it
        else:
            round = round[:-1] + str(heat_num)
        names[i] = ' '.join(names[i].text.split())
        countries[i] = ' '.join(countries[i].text.split())
        if distance == 1000 or distance == 1500:
            times[i] = get_sec(times[i].text.replace('.', ':').replace('WR', ''))
        else:
            times[i] = ' '.join(times[i].text.split())

        if len(splits) == 0:
            list_of_rows.append(Row(loc_year_type, distance, round, names[i], countries[i], times[i], []))
            Row(loc_year_type, distance, round, names[i], countries[i], times[i], []).my_print()
        else:
            j = 0
            while names[i] != splits[j][0]:
                j += 1
                if j >= len(splits):
                    list_of_rows.append(Row(loc_year_type, distance, round, names[i], countries[i], times[i], []))
                    Row(loc_year_type, distance, round, names[i], countries[i], times[i], []).my_print()
                    break
            if j < len(splits):
                list_of_rows.append(Row(loc_year_type, distance, round, names[i], countries[i], times[i], splits[j][1:]))
                Row(loc_year_type, distance, round, names[i], countries[i], times[i], splits[j][1:]).my_print()


def get_splits_urls(round_url):
    driver.get(round_url)
    splits_urls = []
    elems = driver.find_elements(By.LINK_TEXT, '[Splits]')  # clicks the home button once it gets to the link, to access all the links
    for element in elems:
        splits_urls.append(element.get_attribute("href"))

    return splits_urls

def scrape_splits(split_url, list_of_splits):
    html_text = requests.get(split_url).text
    soup = BeautifulSoup(html_text, 'lxml')

    table = soup.find('table', attrs={'cellspacing': '0', 'align': 'Center', 'border': '0',
                                      'style': 'border-collapse:collapse;'}) # gets the table with the splits
    tr = table.find_all('tr') # gets all the rows
    names = tr[0].find_all('th', attrs={'scope': 'col'})  # list of names in race
    names.pop(0)  # removes first element of list (which is some random blank value)
    row_length = len(names) # length of each row in table
    #tr.pop(0) # removes the row with skaters names

    list_of_race_splits = []
    for i in range(row_length): # creates a list within a list, one list of splits for each skater
        list_of_race_splits.append([names[i].text])
    tr.pop(0) # removes the row with skaters names

    for row in tr:
        split_times = row.find_all('td')
        split_times.pop(0) # since first is the lap number
        for i in range(row_length):
            s = split_times[i].text
            s = s[s.find("(") + 1:s.find(")")]
            if s == '':
                list_of_race_splits[i].append(0)
            elif ':' in s:
                list_of_race_splits[i].append(get_sec(s.replace('.', ':').replace('WR', ''))) # in the case one lap is more than a minute long
            else:
                try:
                    list_of_race_splits[i].append(float(s)) # returns numbers between the brackets
                except:
                    list_of_race_splits[i].append(0)


    list_of_splits = list_of_splits + list_of_race_splits
    return list_of_splits

def main():
    race_urls = {}
    loc_year_type_list = []
    list_of_rows = []
    splits_url = []
    get_season()
    comp_urls = get_competition_urls(loc_year_type_list)

    gender = input("Which gender would you like the results for? (Type 'Men' or 'Women') \n> ")

    if gender.lower() == 'men':
        for j in range(len(comp_urls)):
            race_dict = men_get_races(comp_urls[j], race_urls)
            listof_race_urls = list(race_dict.keys())

            for i in range(len(listof_race_urls)):
                scrape_round(listof_race_urls[i], race_dict, list_of_rows, loc_year_type_list[j])
            race_urls = {}

    elif gender.lower() == 'women':
        for j in range(len(comp_urls)):
            race_dict = women_get_races(comp_urls[j], race_urls)
            listof_race_urls = list(race_dict.keys())

            for i in range(len(listof_race_urls)):
                scrape_round(listof_race_urls[i], race_dict, list_of_rows, loc_year_type_list[j])
            race_urls = {}
    else:
        print("Please enter either 'Men' or 'Women'")
        main()

    df = pd.DataFrame()
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    list5 = []
    list6 = []
    list7 = [] # lap 1
    list8 = []  # lap 2
    list9 = []  # lap 3
    list10 = []  # lap 4
    list11 = []  # lap 5
    list12 = []  # lap 6
    list13 = []  # lap 7
    list14 = []  # lap 8
    list15 = []  # lap 9
    list16 = []  # lap 10
    list17 = []  # lap 11
    list18 = []  # lap 12
    list19 = []  # lap 13
    list20 = []  # lap 14

    for row in list_of_rows:
        list1.append(row.get_loc_year_type())
        list2.append(row.get_distance())
        list3.append(row.get_round())
        list4.append(row.get_name())
        list5.append(row.get_country())
        list6.append(row.get_time())
        splits = row.get_splits()
        for i in range(14):
            if i == 0:
                if i >= len(splits):
                    list7.append('-')
                else:
                    list7.append(splits[i])
            if i == 1:
                if i >= len(splits):
                    list8.append('-')
                else:
                    list8.append(splits[i])
            if i == 2:
                if i >= len(splits):
                    list9.append('-')
                else:
                    list9.append(splits[i])
            if i == 3:
                if i >= len(splits):
                    list10.append('-')
                else:
                    list10.append(splits[i])
            if i == 4:
                if i >= len(splits):
                    list11.append('-')
                else:
                    list11.append(splits[i])
            if i == 5:
                if i >= len(splits):
                    list12.append('-')
                else:
                    list12.append(splits[i])
            if i == 6:
                if i >= len(splits):
                    list13.append('-')
                else:
                    list13.append(splits[i])
            if i == 7:
                if i >= len(splits):
                    list14.append('-')
                else:
                    list14.append(splits[i])
            if i == 8:
                if i >= len(splits):
                    list15.append('-')
                else:
                    list15.append(splits[i])
            if i == 9:
                if i >= len(splits):
                    list16.append('-')
                else:
                    list16.append(splits[i])
            if i == 10:
                if i >= len(splits):
                    list17.append('-')
                else:
                    list17.append(splits[i])
            if i == 11:
                if i >= len(splits):
                    list18.append('-')
                else:
                    list18.append(splits[i])
            if i == 12:
                if i >= len(splits):
                    list19.append('-')
                else:
                    list19.append(splits[i])
            if i == 13:
                if i >= len(splits):
                    list20.append('-')
                else:
                    list20.append(splits[i])

    df['Location, Year, Type'] = list1
    df['Distance'] = list2
    df['Round'] = list3
    df['Name'] = list4
    df['Country'] = list5
    df['Time'] = list6
    df['Lap 1'] = list7
    df['Lap 2'] = list8
    df['Lap 3'] = list9
    df['Lap 4'] = list10
    df['Lap 5'] = list11
    df['Lap 6'] = list12
    df['Lap 7'] = list13
    df['Lap 8'] = list14
    df['Lap 9'] = list15
    df['Lap 10'] = list16
    df['Lap 11'] = list17
    df['Lap 12'] = list18
    df['Lap 13'] = list19
    df['Lap 14'] = list20

    file_name = input("The results are about to be saved in a file, please name the file: ")
    df.to_excel(f'{file_name}.xlsx')

main()


