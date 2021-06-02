from bs4 import BeautifulSoup
from aiohttp import ClientSession
from asyncio import gather, create_task, run 
import os

from config import *

class ArxivParser(object):
    def __init__(self,path=PATH,*args,**kwargs):
        self.path = path
        self.archives = ARCHIVES
        self.bib_info = BIB_INFO
        self.action_list  = {
                            'url': lambda html, callback=None: self.process_archives(html,callback),
                           'item': lambda html, callback=None: self.process_entry(html,callback),
                           'html': lambda html, callback=None: html,
                           }
        self.action_cache = dict()
        self.options = {'searchtype':'all',
                      'abstracts':'show',
                      'order':'-announced_date_first',
                      'size':'100'}

    async def fetch_all(self,urls,action,headers=dict(),callback=None):
        tasks = [create_task(self.fetch_entry(url,action,headers,callback))
                    for url in urls]
        await gather(*tasks)
        return [task.result() for task in tasks]

    async def fetch_entry(self,url,action,headers=dict(),callback=None):
        try:
            async with ClientSession() as session:
                async with session.get(url,headers=headers) as response:
                    html = await response.text()
                    html = BeautifulSoup(html,'html.parser')
                    return self.action_list[action](html,callback=callback)
        except Exception as e:
            print(url)
            print(f'Exception found: {str(e)}.')

    def fetch_author(self,authors): 
        author = []
        for aut in authors:
            names = aut.attrs['content'].split(',')
            name = [word.strip()[0]+'.' for word in names[1:]]
            name.append(names[0])
            author.append(' '.join(name))
        if len(author)>1:
            return ', '.join(author[:-1])+ ', and ' + author[-1]
        else:
            return author[0]

    def process_entry(self,res,callback=None):
        extract = lambda res, key: res.find('meta',attrs={'name':'citation_'+key}).attrs['content']
        entry_dict = { key: extract(res,key) for key in self.bib_info}
        authors = res.find_all('meta',attrs={'name':'citation_author'})
        entry_dict['author'] = self.fetch_author(authors)
        try:
            entry_dict['doi'] = extract(res, 'doi')
        except Exception as e:
            print(f'Exception: No DOI. Parsing instead ArXiv url...')
        if callback is not None:
            return callback(entry_dict)
        return entry_dict

    def process_archives(self,archive,callback=None):
        new_, cross_, *repl_ = archive.find_all('dl')
        def match(tag):
            return ( tag.has_attr('href') and tag['href'].startswith('/abs/') )
        urls_new_ = [self.path+el.attrs['href'] for el in new_.find_all(match)]
        urls_cross_ = [self.path+el.attrs['href'] for el in cross_.find_all(match)]
        urls = urls_new_+ urls_cross_
        if callback is not None:
            abstracts_new_   = new_.find_all('p',class_='mathjax')
            abstracts_cross_ = cross_.find_all('p',class_='mathjax')
            abstracts = abstracts_new_+abstracts_cross_
            abstracts = [a.get_text().lower() for a in abstracts]
            urls = callback(urls,abstracts)
        return urls

    def fetch_query(self,*args,**kwargs):
        action = 'search'
        query ='?query='
        query+='+'.join(args)
        options = self.options
        query += '&'+'&'.join(f'{k}={v}' for k,v in options.items())
        query_url = os.path.join(self.path,action,query)
        tags = run(self.fetch_entry(query_url,action='html'))

        def match(tag):
            return (
                tag.has_attr('href') and tag['href'].startswith(ABSTRACT)
            )
        return [ tag.attrs['href'] for tag in tags.find_all(match)]

