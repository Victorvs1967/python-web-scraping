import queue
from threading import Thread
import requests
from bs4 import BeautifulSoup


startUrl = 'https://scrapeme.live/shop/page/1/'

to_visit = set()
visited = set()
max_visits = 4
num_worker = 5

q = queue.Queue()

# free proxy list - https://free-proxy-list.net
proxies = {
	'http': 'http://91.209.11.132:80',
	'https': 'http://8.219.176.202:8080',
}

headers = {
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
}

def get_html(url):
	try:
		response = requests.get(url, headers=headers, proxies=proxies)
		return response.content
	except Exception as e:
		print(e)
		return ''

# create queue worker
def queue_worker(i, q):
  while True:
    url = q.get() # get an item from the queue
    if (len(visited) < max_visits and url not in visited):
      crawl(url)
    q.task_done() # notifies the queue that the item has been processed

# get html content
def get_html(url):
  try:
    return requests.get(url).content
  except Exception as e:
    print(e)
    return ''

# get list of links
def extract_links(soup):
  return [a.get('href') for a in soup.select('a.page-numbers') if a.get('href') not in visited]

# get need content
def extract_content(soup):
  for product in soup.select('.product'):
    print(product.find('h2').text)

# main crawler function
def crawl(url):
  if not url or url in visited:
    return
  print('Crawl: ', url)
  visited.add(url)
  html = get_html(url)
  soup = BeautifulSoup(html, 'lxml')
  extract_content(soup)
  links = extract_links(soup)
  [q.put(link) for link in links if link not in visited]
  to_visit.update(links)

# scrap data with recurcive
def main():
  # oganize threeding queue
  for i in range(num_worker):
    Thread(target=queue_worker, args=(i, q), daemon=True).start()

  q.put(startUrl)
  q.join()
  print('Done')


if __name__ == '__main__':

  main()
