# fin_mcp/tools/sec_tools.py
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; SECAPIMCP/1.0; +https://yourdomain.com/contact)'
}

def lookup_ticker(company_name: str) -> str | None:
    # print("REACHED LOOKUP TICKER")
    url = "https://www.sec.gov/files/company_tickers.json"
    r = requests.get(url, headers=HEADERS)
    data = pd.DataFrame.from_dict(r.json(), orient="index")
    # print(data.head())

    matches = data[data["title"].str.contains(company_name, case=False, na=False)]
    if not matches.empty:
        # print("REACHED MATCHES")
        # print(matches)
        return matches.iloc[0]["ticker"]
    
    return None

def get_cik(ticker: str) -> str:
    url = "https://www.sec.gov/files/company_tickers.json"
    company_tickers = requests.get(url, headers=HEADERS).json()
    company_data = pd.DataFrame.from_dict(company_tickers, orient='index')

    cik = company_data[company_data['ticker'] == ticker]['cik_str'].values[0].astype(str).zfill(10)
    # print(f"CIK for {ticker}: {cik}")
    return cik

def get_accession_numbers(cik: str, form_type='10-K') -> dict:
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    r = requests.get(url, headers=HEADERS)
    data = r.json()
    accessions = data['filings']['recent']['accessionNumber']
    forms = data['filings']['recent']['form']
    filings = [a for a, f in zip(accessions, forms) if f == form_type]
    def extract_year(acc_num):
        # Extract the year from the accession number
        return 2000 + int(acc_num.split('-')[1])

    acc_map = {}
    for f in filings:
        acc_map[extract_year(f)] = f

    return dict(sorted(acc_map.items(), reverse=True))  # Sort by year descending

def parse_10k(accession_number: str, cik: str) -> dict:
    clean_acc = accession_number.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{clean_acc}/{accession_number}.txt"
    # print(url)
    r = requests.get(url, headers=HEADERS)
    raw_10k = r.text

    # Regex to find <DOCUMENT> tags
    doc_start_pattern = re.compile(r'<DOCUMENT>')
    doc_end_pattern = re.compile(r'</DOCUMENT>')
    # Regex to find <TYPE> tag prceeding any characters, terminating at new line
    type_pattern = re.compile(r'<TYPE>[^\n]+')

    # Extract the 10-K section
    doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10k)]
    doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10k)]
    doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10k)]

    document = {}
    for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
        if doc_type == '10-K':
            document[doc_type] = raw_10k[doc_start:doc_end]

    # Match headings like "Item 1A", "ITEM 1B.", etc.
    regex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(1A|1B|7A|7|8)\.{0,1})|(ITEM\s(1A|1B|7A|7|8))')
    matches = list(regex.finditer(document['10-K']))

    df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])
    df.columns = ['item', 'start', 'end']
    # Get rid of unnesesary charcters from the dataframe
    df.replace({'&#160;': ' ', '&nbsp;': ' ', ' ': '', '>': '', r'\.': ''}, regex=True, inplace=True)
    # convert item names to lowercase and remove non-alphanumeric characters
    df['item'] = df['item'].str.lower().str.replace(r'[^a-z0-9]', '', regex=True)

    pos_dat = df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')
    pos_dat.set_index('item', inplace=True)

    def get_section(start_item, end_item):
        """Helper function to extract section text from the document."""
        try:
            start = pos_dat['start'].loc[start_item]
            end = pos_dat['start'].loc[end_item]
            raw_section = document['10-K'][start:end]
            return BeautifulSoup(raw_section, 'lxml').get_text("\n\n")
        
        except KeyError as e:
            print(e)
            return "COULD NOT FIND SECTION"
        
    # Extract sections
    result = {}
    result['item_1a'] = get_section('item1a', 'item1b')
    result['item_7'] = get_section('item7', 'item7a')
    result['item_7a'] = get_section('item7a', 'item8')
    

    return result
