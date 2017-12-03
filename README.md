# Pittsburgh has a lot of service outages.

It's an old city with old infrastructure. And it's not always easy to track information about Pittsburgh Water & Sewer Authority service disruptions.

Hence this little scraper. It collects available data about reported outages and community updates -- time of the update, the pdf of the information released, etc. -- and organizes it should anyone desire to parse it further to their own ends.

Written in `Python 3.6`, this little scraper will go to the PWSA's site and grab whatever documents and metadata are published on the outages page, then save out the docs and a `JSON` map of the original document url, its timestamp, the original document title from the site, and the filename it saved to for you.

Kinda like this:

```JSON
{
    "filename": "PWSA-LTD-PUS-12-9-16.pdf",
    "timestamp": "11/27/17 @ 4:31 pm",
    "title": "PWSA Update on the South Bouquet Street Waterline Relay Project - 11-27-17",
    "url": "http://apps.pittsburghpa.gov/pwsa/PWSA-LTD-PUS-12-9-16.pdf"
}
```

All this assumes is that you install the reqs.txt dependencies and have a directory ready to take the pdfs as they come in as this runs.

```python
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
```
