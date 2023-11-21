import requests
import pandas as pd
from bs4 import BeautifulSoup

def scrape_and_write_to_csv(name):
    base_url = 'https://cloud.octa.in/gstin?q='
    full_url = f'{base_url}{name}'
    
    try:
        # Fetching the initial page to get the total number of pages
        response = requests.get(full_url)
        response.raise_for_status()  # Raise an exception for bad response status
        soup = BeautifulSoup(response.content, 'html.parser')
        total_pages = int(re.search(r'of (\d+)', soup.find('p').get_text()).group(1)) + 1

        gst_data = []

        for page_number in range(1, total_pages):
            page_url = f'{base_url}{name}&adv=False&p={page_number}'
            page_response = requests.get(page_url)
            page_response.raise_for_status()  # Raise an exception for bad response status
            page_soup = BeautifulSoup(page_response.content, 'html.parser')

            for link in page_soup.find_all('a', href=True):
                gst_match = re.search(r'(\d{2}\w{5}\d{4}\w\d\w{2})', link['href'])
                if gst_match:
                    gst_number = gst_match.group(0)
                    gst_details = fetch_gst_details(gst_number)
                    if gst_details and gst_details['sts'] == 'Active' and gst_details['api_property']['ctb'] == 'Proprietorship':
                        gst_data.append([gst_details['gstin'], gst_details['legal_name']])
        
        create_csv(gst_data)

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")

def fetch_gst_details(gst_number):
    url = 'https://app.sahigst.com/ajax/do_search_single_gstin'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    cookies = {
        'sstoken': 'Pb7sHq1bP8Q4UrEqP0E44ooeTWOLVxVG',
    }
    data = f'gstin={gst_number}'
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, verify=False)
        response.raise_for_status()  # Raise an exception for bad response status
        result = response.json()
        if result['success']:
            return result['data']
    
    except requests.exceptions.RequestException as e:
        print(f"Error during request for GSTIN {gst_number}: {e}")
    
    except (KeyError, ValueError) as e:
        print(f"Error parsing JSON for GSTIN {gst_number}: {e}")
    
    return None

def create_csv(data):
    if data:
        df = pd.DataFrame(data, columns=['GSTIN', 'Legal Name'])
        df.to_csv('gst.csv', mode='a', index=False, header=False)
        print("Data successfully written to gst.csv")

def main():
    name = input('Enter Your Name: ')
    scrape_and_write_to_csv(name)

if __name__ == "__main__":
    main()
