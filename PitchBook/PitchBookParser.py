import csv
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import os

####################################################################
## Data Ingestion : Code to parse HTML files, convert them into csv.
####################################################################

# *************
# Max rows to be set to 250. Set this to low number e.g. 10 to test the code(runs faster)
max_rows = 250;

# Set path of html file here
path = r"C:\equvis\mapping\rawdata\round3\Deals"
files = [f for f in os.listdir(path) if '.html' in f]

df_list = []
# Loop through files
for file in tqdm(files[0:1]):  # loop through files and run all the code below for each file
    with open(os.path.join(path, file), encoding="utf8") as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    names = []
    links = []

    # Extract Company names and links
    for entity_element in soup.find_all('div', attrs={"class": "custom-cell-format__fixed-entity"}):
        names.append(entity_element.find('a').contents[0])
        link_text = entity_element.find('a')['href']
        id = link_text.split('profile/')[1].split('/company')[0]
        links.append("https://pitchbook.com/profiles/company/" + id)
        # https://pitchbook.com/profiles/company/436733-65

    # Extract columns Headers
    headers = ['Pitchbook Link']
    for spans in (soup.find_all('div', attrs={"class": "smart-caption smart-caption__static"})):
        field = '';
        for span in spans.find_all('span'):
            field += span.contents[0]
        headers.append(field)
    # Empty DF
    df_ = pd.DataFrame([], columns=headers, index=names)

    # Limiting rows to maximums vailable companies
    row_count = min(max_rows, len(names))
    # Extract Cells
    regStr = r"search-results-data-table-row-\d{1,3}-cell-\d{1,3}"
    regStr = r"search-results-data-table-row-[0-9A-Za-z ]+-cell-[0-9A-Za-z ]+"
    res = soup.findAll("div", {"id": re.compile(regStr)})
    # First Columns >  links
    df_.iloc[:, 0] = links
    # Second Columns >  names

    df_.iloc[:, 1] = names
    # Iterate through cells and copy data
    for t in res:
        cell_id = t.get("id")
        row = re.search("row-\d{1,3}", cell_id)[0]
        row = int(row.split('-')[1])
        col = re.search("cell-\d{1,3}", cell_id)[0]
        col = int(col.split('-')[1]) + 2
        df_.iloc[row, col] = t.text.replace('\xa0', '').replace('\n', ' ').replace('\r', '')

    df_list.append(df_)

ren = {'Companies (4,732)': 'Company Name'}
df_comb = pd.concat(df_list).rename(columns=ren).sort_values(by=['Company Name', 'Deal No.'])
df_comb.to_csv(os.path.join(path, 'Deals_Combined__.csv'))