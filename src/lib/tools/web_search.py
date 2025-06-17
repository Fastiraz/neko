#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import random
import httpx
from warnings import warn
from typing import Union, List
# from bs4 import BeautifulSoup
import re
from html.parser import HTMLParser


class ResultDict(dict):
    def __init__(self, title: str, description: str, url: str):
        self.title = title
        self.description = description
        self.url = url
        super().__init__(title=title, description=description, url=url)


DDG_URL = "https://html.duckduckgo.com/html"


class BaseClient:
    def __init__(self, proxies: Union[list, str] = None, default_user_agents: Union[list, str] = None, random_ua: bool = None):
        if random_ua is not None:
            warn("The random_ua parameter has been deprecated in favor of the default_user_agents parameter and will be removed in a future release.", DeprecationWarning, 2)
        self.proxies = proxies
        self.default_user_agents = default_user_agents


class Client(BaseClient):
    def search(self, query: str, exact_match: bool = False, **kwargs) -> List[ResultDict]:
        if exact_match:
            query = '"%s"' % query
        if isinstance(self.proxies, str):
            proxy = self.proxies
        elif isinstance(self.proxies, list):
            proxy = random.choice(self.proxies) if self.proxies else None
        else:
            proxy = None
        if isinstance(self.default_user_agents, str):
            ua = self.default_user_agents
        elif isinstance(self.default_user_agents, list):
            ua = random.choice(self.default_user_agents) if self.default_user_agents else None
        else:
            ua = None
        headers = {'User-Agent': ua} if ua else None
        with httpx.Client(proxy=proxy) as http:
            r = http.post(DDG_URL, data=dict(q=query, **kwargs), headers=headers)
            data = r.read()
            return parse_page(data)


class AsyncClient(BaseClient):
    def __init__(self, proxies: Union[list, str] = None, default_user_agents: Union[list, str] = None, random_ua: bool = None):
        self.loop = asyncio.get_event_loop()
        super().__init__(proxies=proxies, default_user_agents=default_user_agents, random_ua=random_ua)
    async def search(self, query: str, exact_match: bool = False, **kwargs) -> List[ResultDict]:
        if exact_match:
            query = '"%s"' % query
        if isinstance(self.proxies, str):
            proxy = self.proxies
        elif isinstance(self.proxies, list):
            proxy = random.choice(self.proxies) if self.proxies else None
        else:
            proxy = None
        if isinstance(self.default_user_agents, str):
            ua = self.default_user_agents
        elif isinstance(self.default_user_agents, list):
            ua = random.choice(self.default_user_agents) if self.default_user_agents else None
        else:
            ua = None
        headers = {'User-Agent': ua} if ua else None
        async with httpx.AsyncClient(proxies=proxy, http2=True) as http:
            r = await http.post(DDG_URL, data=dict(q=query, **kwargs), headers=headers)
            data = r.read()
            return await self.loop.run_in_executor(None, parse_page, data)


# def parse_page(html: Union[str, bytes]) -> List[ResultDict]:
#     soup = BeautifulSoup(html, "html.parser")
#     results = []
#     for i in soup.find_all('div', {'class': 'links_main'}):
#         if i.find('a', {'class': 'badge--ad'}):
#             continue
#         try:
#             title = i.h2.a.text
#             description = i.find('a', {'class': 'result__snippet'}).text
#             url = i.find('a', {'class': 'result__url'}).get('href')
#             results.append(ResultDict(title=title, description=description, url=url))
#         except AttributeError:
#             pass
#     return results


def parse_page(html: Union[str, bytes]) -> List[ResultDict]:
    if isinstance(html, bytes):
        html = html.decode('utf-8')
    results = []
    # Find all content between links_main divs (much simpler pattern)
    sections = re.split(r'<div[^>]*links_main', html)[1:]
    for section in sections:
        # Skip ads
        if 'badge--ad' in section:
            continue
        try:
            # Find title in h2 tag
            title = re.search(r'<h2[^>]*>.*?>(.*?)</a>', section, re.DOTALL)
            title = re.sub(r'<[^>]+>', '', title.group(1)).strip() if title else None
            # Find description 
            desc = re.search(r'result__snippet[^>]*>(.*?)</a>', section, re.DOTALL)
            description = re.sub(r'<[^>]+>', '', desc.group(1)).strip() if desc else None
            # Find URL
            url = re.search(r'result__url[^>]*href="([^"]*)"', section)
            url = url.group(1) if url else None
            
            if title and description and url:
                results.append(ResultDict(title=title, description=description, url=url))
        except:
            pass
    return results


def ddg_search(query: str) -> list:
    """
    Make a web search using DuckDuckGo.

    Args:
      query (str): The query to search for

    Returns:
      list: A list of top 3 results that contains titles, urls and descriptions.
    """
    client = Client()
    results = client.search(query)
    return results[:3]

if __name__ == "__main__":
    results = ddg_search("What is Gitlab?")
    for result in results:
        print("Title:", result.title)
        print("URL:", result.url)
        print("Description:", result.description)
        print("---")