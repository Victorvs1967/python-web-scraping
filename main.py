import queue
from threading import Thread
import requests
from bs4 import BeautifulSoup


# config constants
config = {
  'startUrl': 'https://scrapeme.live/shop/page/1/', # start link
  'data': [], # content storage
  'visited': set(), # list of visited links
  'max_visits': 100, # max number links to visit
  'num_worker': 5, # number thread to create
  'proxies': {  # free proxy list - https://free-proxy-list.net
    'http': 'http://91.209.11.132:80',
    'http': 'http://8.219.176.202:8080',
  },
  'headers': {
    'authority': 'httpbin.org',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    'sec-ch-ua-mobile': '?0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-US,en;q=0.9',
  },
}

# get html content
def get_html(url):
	try:
		# response = requests.get(url)
		response = requests.get(url, headers=config['headers'], proxies=config['proxies'])
		return response.content
	except Exception as e:
		print(e)
		return ''

# get list of links
def extract_links(soup):
  return [a.get('href') for a in soup.select('a.page-numbers') if a.get('href') not in config['visited']]

# get need content
def extract_content(soup):
  for product in soup.select('.product'):
    config['data'].append({
      'id': product.find('a', attrs={'data-product_id': True})['data-product_id'],
      'name': product.find('h2').text,
      'price': product.find('span', {'class': 'amount'}).text
    })

# main crawler function
def crawl(url, q):
  config['visited'].add(url)
  print('Crawl: ', url)
  html = get_html(url)
  soup = BeautifulSoup(html, 'lxml')
  extract_content(soup)
  links = extract_links(soup)
  [q.put(link) for link in links if link not in config['visited']]

# create crawl queue worker
def queue_worker(i, q):
  while True:
    url = q.get()  # get an item from the queue
    if (len(config['visited']) < config['max_visits'] and url not in config['visited']):
      crawl(url, q)
    q.task_done()  # notifies the queue that the item has been processed

# scrap data
def main():
  q = queue.Queue()
  # oganize threeding queue
  for i in range(config['num_worker']):
    Thread(target=queue_worker, args=(i, q), daemon=True).start()
  q.put(config['startUrl'])
  q.join()

  # output result
  print('\nVisited: ')
  [print(visit) for visit in config['visited']]
  print('\nProducts:')
  [print(product) for product in config['data']]
  print('\nDone')

# probe features...
def get_origin():
   responseIP = requests.get(
    'http://httpbin.org/ip', 
    proxies=config['proxies'], 
    headers=config['headers']
   )
   responseUA = requests.get(
    'http://httpbin.org/headers', 
    proxies=config['proxies'], 
    headers=config['headers']
   )
   print('Origin: ', responseIP.json()['origin'])
   print('Headers: ', responseUA.json()['headers']['User-Agent'])

if __name__ == '__main__':
  # main()
  get_origin()
