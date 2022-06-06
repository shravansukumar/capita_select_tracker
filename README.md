This is a project for implementing a web crawler and analyzing the data from the crawl. This is part of the masters course for cyber security. More details about this course can be found [here](https://www.ru.nl/courseguides/science/vm/osirislinks/imc/nwi-imc067/).

## Library installation:
1. `selenium-wire`: <br>
    `pip3 install selenium-wire`
2. `tld`: (Used for extracting top level domains)<br>
    `pip install tld`
3. This runs on Chrome driver. The exact version depends on the version of Chrome in the system. Please refer [here](https://chromedriver.chromium.org/downloads) and download the corresponding driver, and place it in the project directory.

## Usage:
The crawler can be started from the command line. The basic command looks something like this: <br>

`python3 script.py -m desktop -i tranco-top-500-safe.csv`<br>

With the following arguments: <br>
- `-m`: argument to specify the crawler mode either      `mobile` or `desktop`.

- `-u`: argument to specify one URL to crawl takes a string input.

- `-i`: argument to take a `.csv` file containing URLs to be crawled.

- `-head`: argument to specify the crawling mode of the browser takes one of two options, either `headfull` or `headless`. Default is `headless`.

## Analysis
Please run the attached Jupyter Notebook file with the  crawl data in the same folder/file to get the analysis data.