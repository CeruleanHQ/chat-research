# Youtube Chat Parser and Processor
Matt Katz - 2021

## Features

* Parse Youtube video's comments
* Save as text file if requested
  
* Parse plain text file instead of parsing a YouTube video 
* Load keywords list file
* Generate report based on chat messages vs keywords, creating a timeline based on time intervals.
  * Save report as CSV file
    
  * Show report as a graph


## Roadmap 

* Option to have elapsed time 
* Support for Twitch Chat parsing

* More configuration options
* More detailed information on README file
* Unit testing
* Split script into proper classes 

## Usage

```
usage: main.py [-h] [-f CHAT_FILE] [-yt YOUTUBE_ID] [-o OUTPUT_CSV] [-k KEYWORDS_FILE] [-t TIME_INTERVAL]

optional arguments:
  -h, --help            show this help message and exit
  -f CHAT_FILE, --file CHAT_FILE
                        Chat text file to process
  -yt YOUTUBE_ID, --youtube YOUTUBE_ID
                        Youtube ID to get the chat from
  -o OUTPUT_CSV, --output OUTPUT_CSV
                        Output CSV file name
  -k KEYWORDS_FILE, --keywords-file KEYWORDS_FILE
                        Keywords file
  -t TIME_INTERVAL, --time-interval TIME_INTERVAL
                        Time interval range for stats

```

For time interval / frequency information, refer to https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
