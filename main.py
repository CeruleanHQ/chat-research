#!/usr/bin/env python3

import argparse
import logging
import os
import re

import pandas as pd
import pytchat
from matplotlib import pyplot


def process_yt_chat(youtube_id: str) -> dict:
    """Get Youtube Chat messages
    Args:
        youtube_id: YouTube video ID
    """

    # https://pypi.org/project/pytchat/
    chat = pytchat.create(youtube_id)
    chat_messages = {}
    while chat.is_alive():
        chat_data = chat.get()
        for chat_info in chat_data.items:
            chat_messages[chat_info.datetime] = {
                "datetime": chat_info.datetime,
                "name": chat_info.author.name,
                "message": chat_info.message,
            }

    return chat_messages


def save_file(contents: str, filename: str) -> None:
    """Save contents into a text file

    Args:
        contents: Contents to save
        filename: file name
    """
    text_file = open(filename, "w")
    text_file.write(contents)
    text_file.close()


def read_file(filename: str) -> list:
    """Read File

    Args:
        filename (str): file name.

    Returns:
        list: file line list
    """
    if not os.path.isfile(filename):
        print("File does not exist.")
    else:
        with open(filename) as f:
            file_content = f.read().splitlines()
        return file_content


def get_keywords(keywords_file) -> list:
    """Return a list of keywords"""
    keywords = read_file(keywords_file)
    return keywords


def create_data_frame(
    chat_content: list, keywords: list, time_interval: str = "4T"
) -> pd.DataFrame:
    """
    Generate a usable Data Set from the chat content

    Args:
        chat_content: List with chat content
        keywords: The List of keywords
    """
    proc_beats = {}
    for item in chat_content:
        # RegEx to process the chat line format
        x = re.match(
            r"^(?P<datetime>\[.+?\])\s+(?P<name>[^:]+):\s+(?P<message>[\s\S]+?)$",
            item,
        )
        # Remove the brackets in the timestamp, those are not needed
        clean_datetime = x.group("datetime").replace("[", "").replace("]", "")

        # Convert the timestamp into something Pandas can understand
        clean_datetime = pd.to_datetime(clean_datetime)

        # Create the Dictionary structure with clean data
        proc_beats[clean_datetime] = {
            "datetime": clean_datetime,
            "name": x.group("name"),
            "message": x.group("message"),
        }

    # Inject the Dict into Pandas so we have our first Data Set
    df = pd.DataFrame(data=proc_beats).T

    # Make the DateTime field the index for faster processing
    df.index = pd.DatetimeIndex(df.index)

    """
    Time frequency table
    https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    
    X + freq, e.g.:
    30S = Intervals of 30 Seconds
    5T = Intervals of 5 minutes
    1H = Intervals of 1 Hour
    """
    # Group the data into time intervals
    time_groups = df.groupby([pd.Grouper(key="datetime", freq=time_interval)])

    # Get all the generated groups for processing
    groups_data = time_groups.groups

    # With the generated data set, we create a new one with the keyword count
    stats = {}

    # For each subset (time interval set) do all this...
    for group_data in groups_data:

        # Get the subset group
        group = time_groups.get_group(group_data)

        # We convert a List structure into a single String so it's easier to
        # count words
        messages = " ".join(group.message.values)

        # This timestamp format can be changed if needed
        str_timestamp = group_data.strftime("%Y-%m-%d %H:%M:%S")
        # str_timestamp = group_data.strftime("%m-%d-%Y %H:%M:%S")
        # str_timestamp = group_data.strftime("%H:%M:%S")

        # Initialise the Dictionary structure so I can fill it with stats
        stats[str_timestamp] = {}
        """
        For each keyword in the list, count how many times it appears in the
        subset, and save that number in a new data structure, that later will
        be converted to another data set for graph generation.
        """
        for keyword in keywords:
            msg_count = messages.upper().count(keyword.upper())
            stats[str_timestamp][keyword] = msg_count

    return pd.DataFrame(data=stats).T


def show_graph(df: pd.DataFrame) -> None:
    """
    Create and show a graph based on the provided data set

    Args:
        df: Pandas DataFrame set

    """
    df.plot.area(
        # xlabel="Time",
        # ylabel="Sum of Key",
        # rot=25,  # rotation of x axis Labels
        stacked=True,
        sort_columns=True,
        # subplots=True
    )

    pyplot.show()


def save_to_csv(df: pd.DataFrame, csv_file: str) -> None:
    """Save the DataFrame into a csv file"""
    df.to_csv(csv_file)


def process_chat_content(
    text_filename: str,
    keywords_file: str,
    csv_file: str = "",
    time_interval: str = "4T",
) -> None:
    """Process a chat filename and show the graph or output a CSV file"""
    chat_content = read_file(text_filename)
    keywords = get_keywords(keywords_file)

    df = create_data_frame(chat_content, keywords, time_interval=time_interval)

    if csv_file:
        logging.info(f"Saving results to {csv_file}")
        save_to_csv(df, csv_file)
    else:
        logging.info("Generating graph")
        show_graph(df)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Chat Processor")
    parser.add_argument(
        "-f",
        "--file",
        dest="chat_file",
        help="Chat text file to process",
        default="chat.txt",
    )
    parser.add_argument(
        "-yt",
        "--youtube",
        help="Youtube ID to get the chat from",
        dest="youtube_id",
    )

    parser.add_argument(
        "-yto",
        "--youtube-output",
        help="Will save chat contents in the given filename",
        dest="youtube_text_file",
    )

    parser.add_argument(
        "-o", "--output", dest="output_csv", help="Output CSV file name"
    )

    parser.add_argument(
        "-k",
        "--keywords-file",
        dest="keywords_file",
        default="keywords.txt",
        help="Keywords file",
    )

    parser.add_argument(
        "-t",
        "--time-interval",
        dest="time_interval",
        help="Time interval range for stats",
        default="4T",
    )

    return parser.parse_args()


def config_logger() -> None:
    """Set up the logging information, for prettier messages."""
    logging.basicConfig(
        format="%(asctime)s:%(levelname).1s:" " %(message)s",
        datefmt="%y-%m-%dT%H:%M:%S",
        level=logging.INFO,
    )


if __name__ == "__main__":
    config_logger()

    # Use command line arguments for flexibility
    args = parse_arguments()

    logging.info(20 * "➿")
    logging.info("         💬 CHAT PARSER 1.0 💬")
    logging.info(20 * "➿")

    if args.youtube_id:
        logging.info(f"Received YouTube ID {args.youtube_id}")
        chat_data = process_yt_chat(args.youtube_id)

        lines = []
        if args.youtube_text_file:
            logging.info(f"Saving YT chat in {args.youtube_text_file}")
            for chat_timestamp, chat_info in chat_data.items():
                chat_msg = (
                    f"{chat_info['datetime']} "
                    f"{chat_info['name']}: {chat_info['message']}"
                )
                lines.append(chat_msg)
        save_file("\n".join(lines), args.youtube_text_file)

    else:
        logging.info(f"Processing chat file {args.chat_file}")
        process_chat_content(
            args.chat_file,
            args.keywords_file,
            args.output_csv,
            args.time_interval,
        )
