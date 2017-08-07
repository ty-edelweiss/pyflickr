## A Python Flickr Crawling Project

This project aim to collecting photos.

#### Starting crawling application

this application is able to used for command line application tool.

```
# (Example) bin/crawl -s 20xx-xx-xx -e 20yy-yy-yy
bin/crawl -s {start date} -e {end date}


# (Example) bin/crawl -t -s 20xx-xx-xx hh:mm:ss -e 20yy-yy-yy hh:mm:ss
bin/crawl -t -s {start datetime} -e {end datetime}
```

#### Comannd line options

Usage: bin/crawl [options]

Options:
* -h, --help            show this help message and exit
* -s START, --start=START
                        collecting start date. mysql format date.
* -e END, --end=END     collecting end date. mysql format date.
* -t, --time            changing input date is mysql format datetime.
