import requests
from fake_useragent import UserAgent
import logging
import json
import os

INDEX_URL = 'https://careers.tencent.com/tencentcareer/api/post/Query?keyword={keyword}&pageIndex={page}&pageSize=10'
DETAIL_URL = 'https://careers.tencent.com/tencentcareer/api/post/ByPostId?postId={post_id}'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
UA = UserAgent()
FILENAME = '{dirname}/{keyword}{page}.json'


def scrape_api(url):
    logging.info('scraping %s', url)
    headers = {'User-Agent': UA.random}
    try:
        response = requests.get(url, timeout=10, headers=headers)
        if response.status_code == 200:
            return response.json()
        logging.error('get invalid status code %s while scraping %s', response.status_code, url)
    except Exception:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def get_total_page(keyword):
    url = INDEX_URL.format(keyword=keyword, page=1)
    count = scrape_api(url).get('Data').get('Count')
    page = count // 10 + 1 if count % 10 else count // 10
    return page


def scrape_index(keyword, page):
    url = INDEX_URL.format(keyword=keyword, page=page)
    return scrape_api(url)


def parse_index(index_json):
    jobs = index_json.get('Data')
    if not jobs:
        return
    for job in jobs.get('Posts'):
        yield job.get('PostId')


def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def scrape_detail(post_id):
    url = DETAIL_URL.format(post_id=post_id)
    return scrape_api(url)


def main():
    keyword = input('请输入搜素关键词(所有职位则不输入)：')
    total_page = get_total_page(keyword)
    dirname = f'./{keyword}' if keyword else './all_jobs'
    os.path.exists(dirname) or os.makedirs(dirname)
    for page in range(1, total_page + 1):
        jobs = []
        index_json = scrape_index(keyword, page)
        if not index_json:
            continue
        for post_id in parse_index(index_json):
            data = scrape_detail(post_id)
            if data.get('Code') != 200:
                logging.error('get invalid data while scraping %s', detail_url)
                continue
            jobs.append(data)
        logging.info('saving page %s data', page)
        save_data(jobs, FILENAME.format(dirname=dirname, keyword=keyword, page=page))


if __name__ == '__main__':
    main()
