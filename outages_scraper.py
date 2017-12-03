#!usr/bin/env python3

'''
A simple scraper for collecting documents about outages from the
Pittsburgh Water & Sewer Authority
'''

import os
import io
import json
import requests
from lxml import etree

OUTAGES_URL = 'http://www.pgh2o.com/outages'
PDF_DIR_LOCATION = 'pdfs/'


def open_url(url):
    '''
    params:
    a url string

    returns:
    a Requests response object or breaks if the url is bad
    '''
    response = requests.get(url)
    if response.status_code == 200:
        return response
    else:
        print('You gave me a bad URL: {}. Let\'s try that again.'.format(url))
        return None


def parse_response(response_obj):
    '''
    creates a traverseable DOM tree

    params:
    a Requests response object

    returns:
    the DOM tree
    '''
    parser = etree.HTMLParser()
    return etree.parse(io.StringIO(response_obj.text), parser)


def find_pdfs(tree):
    '''
    hunts for pdf links in the anchor tags of a given page

    params:
    a DOM tree

    returns:
    a generator object containing full url paths to pdfs
    '''
    # grab data
    titles = tree.xpath('//*[@class="blurbTitle"]//text()')
    # duplicate urls help literally no one, and there's at least one here
    urls = set(tree.xpath('//*[@class="blurbDescription"]//a/@href'))
    tstamps = tree.xpath('//*[@class="blurbStamp"]//text()')

    # make sure this is structured how we expect, otherwise yell about it
    if len(titles) == len(urls) and len(urls) == len(tstamps):
        data = list(zip(titles, urls, tstamps))
        return data
    else:
        print('''The numbers of titles, urls and timestamps don\'t match
                for some reason. Should probably take a look:\n
                titles: {}\n urls: {}\n timestamps: {}'''.format(
                    len(titles),
                    len(urls),
                    len(tstamps)
                ))


def add_filenames_to_data(data):
    '''
    creates dicts containing urls and filenames parsed from the urls

    params:
    a tuple containing relevant file data

    returns:
    a generator object containing dicts with keys of:
    dict['title']: the original document title,
    dict['filename']: a filename parsed from a url string
    dict['url']: the url
    dict['timestamp']: the recorded timestamp from the original data
    '''
    return ({'title': datum[0],
             'filename': datum[1].split('/')[-1],
             'url': datum[1],
             'timestamp': datum[2]} for datum in data)


def scrape_pdfs(filenames_obj):
    '''
    given a generator object containing dicts, hands each item off for parsing,
    scraping and storage

    params:
    a generator or iterable

    returns:
    none
    '''
    # unpack the generator obj
    files_data = [data for data in filenames_obj]
    for file_obj in files_data:
        save_pdf(file_obj)

    create_timestamp_map(files_data)
    return None


def save_pdf(data_dict):
    '''
    takes each dict and uses its keys to scrape from a url and apply the
    correct corresponding filename

    params:
    a dict with keys of:
    dict['title']: the original document title,
    dict['filename']: a filename parsed from a url string
    dict['url']: the url
    dict['timestamp']: the recorded timestamp from the original data

    returns:
    none; saves the file
    '''
    # filenames are unique, so make sure we haven't collected it before.
    existing_filenames = os.listdir(PDF_DIR_LOCATION)
    if data_dict['filename'] not in existing_filenames:
        print('Scraping {} ....'.format(data_dict['filename']))
        pdf = open_url(data_dict['url'])
        # only proceed with a good response from the URL
        if pdf:
            with open(PDF_DIR_LOCATION + data_dict['filename'], 'wb') as ofile:
                ofile.write(pdf.content)


def create_timestamp_map(dicts):
    j = json.dumps(dicts, sort_keys=True, indent=4)
    filename = 'timestamp_mapping.json'
    with open(PDF_DIR_LOCATION + filename, 'w') as f:
        print(j, file=f)


def run_scrape(url):
    '''
    given where to begin, does the damn thang
    '''
    response = open_url(url)
    tree = parse_response(response)
    print('Good response. All parsed and ready ....')
    data = find_pdfs(tree)
    print('URLs collected ....')
    targets = add_filenames_to_data(data)
    print('Target objects created; starting the scrape ....')
    scrape_pdfs(targets)
    print('All done. Who else wants a nap?')


if __name__ == '__main__':
    run_scrape(OUTAGES_URL)
