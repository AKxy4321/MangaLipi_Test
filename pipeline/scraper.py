import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
import time
import os 


# headers = {
#     'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
#     'accept-language': 'en-US,en;q=0.9',
#     'cache-control': 'no-cache',
#     'pragma': 'no-cache',
#     'priority': 'i',
#     'referer': 'https://mangapill.com/',
#     'sec-ch-ua': '"Brave";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Linux"',
#     'sec-fetch-dest': 'image',
#     'sec-fetch-mode': 'no-cors',
#     'sec-fetch-site': 'cross-site',
#     'sec-gpc': '1',
#     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
# }

# params = {
#     't': '1717584475',
# }

# page_number = 1
# response = requests.get(f'https://cdn.readdetectiveconan.com/file/mangap/723/10180000/{page_number}.jpeg', params=params, headers=headers)

# print(response.status_code)
# with open('data/images/scraped.jpeg', 'wb') as f:
#     f.write(response.content)


class ScrapingObject(BaseModel):
    """
    ScrapingObject represents the structure for scraping data from a given URL.
    Attributes:
        url (str): The URL to scrape, formatted as an f-string. It must be parsed as an f-string only, providing a page_number.
        Example : 
            url.format(page_number=4) to get -> https://cdn.readdetectiveconan.com/file/mangap/723/10180000/4.jpeg

        total_pages (int): The total number of pages to scrape.
    """
    name: str
    url: str
    image_format: str
    total_pages: int    
    

class MangaScraper:
    def __init__(self):
        self.headers = {
            'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'i',
            'referer': 'https://mangapill.com/',
            'sec-ch-ua': '"Brave";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'image',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'cross-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome',
        }

        self.params = {
            't': '1717584475',
        }

    def _get_scraping_object(self, first_number, second_number, total_pages, name, image_format) -> ScrapingObject:
        """
        Returns a ScrapingObject object with the given first and second numbers.

        Args:
            first_number (str): The first number of the manga page.
            second_number (str): The second number of the manga page.

        Returns:
            ScrapingObject: A ScrapingObject object.
        """
        cdn_link = f"https://cdn.readdetectiveconan.com/file/mangap/{first_number}/{second_number}/{{page_number}}.{image_format}"
        return ScrapingObject(url=cdn_link, total_pages=total_pages, name=name, image_format=image_format)


    def _get_page_info(self, raw_link_of_page: str) -> tuple:
        response = requests.get(raw_link_of_page)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            images = soup.find_all('img', {'loading': 'lazy'})
            print(images[0])
            total_pages = len(images)
            image_format = images[0]['data-src'].split('.')[-1] if images else 'jpeg'
            return total_pages, image_format
        else:
            return 0, 'jpeg'

        
    def _get_manga_pill_scraping_object(self, raw_link: str) -> ScrapingObject:
        """
        Extracts and returns the first and second numbers from a given manga page URL.

        Args:
            raw_link (str): The URL of the manga page.

        Returns:
            ScrapingObject: A ScrapingObject object.
        """
        manga_numbers = raw_link.split('/')[4]
        name = raw_link.split('/')[-1]
        first_number, second_number = manga_numbers.split('-')
        total_pages, image_format = self._get_page_info(raw_link)

        return self._get_scraping_object(first_number, second_number, total_pages, name, image_format= image_format)
    


    def scrape_manga_pill(self, raw_link_of_page: str):
        """
        Scrapes the manga page and saves the images inside a folder
        
        Args:
            raw_link_of_page (str): The URL of the manga page.
        
        Returns:
            ScrapingObject: A ScrapingObject object.
        """

        try:
            scrapingObject = self._get_manga_pill_scraping_object(raw_link_of_page)


            try:
                print("Creating directory : ", f'data/images/{scrapingObject.name}')
                os.mkdir(f'data/images/{scrapingObject.name}')
            except OSError:
                print ("Creation of the directory failed")

            try:
                with open(f'data/images/{scrapingObject.name}/meta.json', 'wb') as f:
                    f.write(scrapingObject.model_dump_json().encode())

            except OSError:
                print ("Creation of the meta file failed")




            
            for index in range(1,scrapingObject.total_pages + 1):
                response = requests.get(scrapingObject.url.format(page_number=index), params=self.params, headers=self.headers)
                response.raise_for_status()
                with open(f'data/images/{scrapingObject.name}/{index}.{scrapingObject.image_format}', 'wb') as f:
                    f.write(response.content)

                time.sleep(5)

                
            return True
        except requests.RequestException as e:
            print(f"An error occurred while scraping: {e}")
            return False



manga_scraper = MangaScraper()
if(manga_scraper.scrape_manga_pill('https://mangapill.com/chapters/2067-10095000/jojo-no-kimyou-na-bouken-part-7-steel-ball-run-chapter-95')):
    print("Manga has been scraped successfully")
else:
    print("An error occurred while scraping the manga")



