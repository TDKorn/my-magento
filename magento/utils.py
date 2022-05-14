import requests
from bs4 import BeautifulSoup as bs

BACKUP_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'


def get_agent():
    r = requests.get('https://www.whatismybrowser.com/guides/the-latest-user-agent/chrome')
    if r.ok:
        soup = bs(r.text, 'html.parser')
        if soup_agents := soup.find_all('span', {'class': 'code'}):
            return soup_agents[0].text
    # If function fails to scrape, will use hardcoded user agent
    return BACKUP_AGENT
