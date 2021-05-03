#!/usr/bin/env python3

import os
import re
from pprint import pprint
import pandas as pd
import pytchat

from matplotlib import pyplot
from dateutil.parser import parse


# https://pypi.org/project/pytchat/


def get_yt_chat() -> None:
    """Get Youtube Chat messages"""
    chat = pytchat.create("FIjfTgueG70")
    while chat.is_alive():
        chat_data = chat.get()
        for chat_info in chat_data.items:
            print(f"{chat_info.datetime} - {chat_info.author.name} - {chat_info.message}")


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


def process_with_regex(chat_content: list) -> dict:
    """Process the chat chat_content with regex"""
    proc_beats = {}
    for item in chat_content:
        x = re.match(
            r"^(?P<datetime>\[.+?\])\s+(?P<name>[^:]+):\s+(?P<message>[\s\S]+?)$",
            item,
        )
        clean_datetime = x.group("datetime").replace("[", "").replace("]", "")
        clean_datetime = pd.to_datetime(clean_datetime)
        proc_beats[clean_datetime] = {
            "datetime": clean_datetime,
            "name": x.group("name"),
            "message": x.group("message")
        }

    df = pd.DataFrame(data=proc_beats).T
    df.index = pd.DatetimeIndex(df.index)

    time_groups = df.groupby([pd.Grouper(key="datetime", freq="30S")])
    groups_data = time_groups.groups

    keywords = get_keywords()
    stats = {}
    for group_data in groups_data:
        group = time_groups.get_group(group_data)
        messages = " ".join(group.message.values)

        str_timestamp = group_data.strftime("%m-%d-%Y %H:%M:%S")
        stats[str_timestamp] = {}
        for keyword in keywords:
            stats[str_timestamp][keyword] = messages.count(keyword)

    return stats

def show_graph():
    # x-axis values
    roll_num = [0, 1000, 2000, 3000, 4000, 5000]

    # y-axis values
    timestamps = [13, 15, 18, 22, 30, 35]
    amount = [4500, 3500, 23, 2400, 0, 1234]
    pyplot.plot(timestamps, roll_num, color="green", label="bboobs")
    pyplot.plot(timestamps, amount, color="red", label="cringe")
    # pyplot.plot(roll_num, amount, color = 'blue', label = 'Amount')
    pyplot.legend(loc="upper left", frameon=True)

    pyplot.show()

def generate_graph(stats: dict) -> None:
    ...

def process_chat_content(chat_content: list, keywords: list) -> None:
    """
    Will process things

    """
    stats = process_with_regex(chat_content)

    # print(keywords)


if __name__ == "__main__":
    process_chat_content(read_file("chat1.txt"), get_keywords())
