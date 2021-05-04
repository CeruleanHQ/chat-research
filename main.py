#!/usr/bin/env python3

import os
import re

import pandas as pd
import pandas.plotting
import pytchat
from matplotlib import pyplot


def get_yt_chat() -> None:
    """Get Youtube Chat messages"""
    # We're not using this right now
    # https://pypi.org/project/pytchat/
    chat = pytchat.create("FIjfTgueG70")
    while chat.is_alive():
        chat_data = chat.get()
        for chat_info in chat_data.items:
            print(
                f"{chat_info.datetime} - {chat_info.author.name} - {chat_info.message}"
            )


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


def get_keywords() -> list:
    """Return a list of keywords"""
    keywords = read_file("keywords.txt")
    return keywords


def create_data_frame(chat_content: list, keywords: list) -> pd.DataFrame:
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
    time_groups = df.groupby([pd.Grouper(key="datetime", freq="5T")])

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
        str_timestamp = group_data.strftime("%m-%d-%Y %H:%M:%S")

        # Initialise the Dictionary structure so I can fill it with stats
        stats[str_timestamp] = {}
        """
        For each keyword in the list, count how many times it appears in the
        subset, and save that number in a new data structure, that later will
        be converted to another data set for graph generation.
        """
        for keyword in keywords:
            stats[str_timestamp][keyword] = messages.count(keyword)

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
        rot=25,  # rotation of x axis Labels
        # stacked=True,
        sort_columns=True,
        # subplots=True
    )

    pyplot.show()


def process_chat_content() -> None:
    """Process everything"""
    chat_content = read_file("chat1.txt")
    keywords = get_keywords()

    df = create_data_frame(chat_content, keywords)
    show_graph(df)


if __name__ == "__main__":
    process_chat_content()
