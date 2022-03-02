import discord
from bs4 import BeautifulSoup
import requests
import sys
from datetime import datetime
import asyncio

from dotenv import load_dotenv
import os
load_dotenv()

token = os.getenv('TOKEN')

url="https://www.bbc.com/news/live/world-europe-60582327"
allowed_stop = [395927930057916434, 494203882973429781, 356492770531344387, 494191985712955394, 513696958087430144]
allowed_eval = [395927930057916434]

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="bbc news"))
        postTime, title, texts, imgs_url= await self.fetch_new_post()
        #first postTime running

        
        with open('last_post.txt', 'r') as f:
            last_post = f.read()
        while True:
            try:
                if last_post != title:
                    #to the loop
                    postTime, title, texts, imgs_url= await self.fetch_new_post()
                    url = await self.check_for_new_link(title, texts)
                    if title.startswith("Breaking"):
                        embed = discord.Embed(title=title[8:], description="\n\n".join([x.text for x in texts]) , color=0xff0000)       
                    else:
                        embed = discord.Embed(title=title, description="\n\n".join([x.text for x in texts]) , color=0x00ff00)

                    embed.timestamp = datetime.now()
                    embed.set_author(name="bbc news", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/BBC_News_2019.svg/1200px-BBC_News_2019.svg.png", url=url)
                    

                    await self.get_channel(947236103381983285).send(embed=embed)
                    if len(imgs_url) > 0:
                      await self.get_channel(947236103381983285).send("\n".join(imgs_url))


                    last_post = title
                    with open('last_post.txt', 'w') as f:
                        f.write(last_post)
                else:
                    postTime, title, texts, imgs_url = await self.fetch_new_post()
                    url = await self.check_for_new_link(title, texts)
                await asyncio.sleep(60)
            except Exception as e:
                print(e)

    async def check_for_new_link(self, title, texts):
        if title != "Our live coverage is moving":
            return url
        else:
            return texts[0].a['href']
            
    

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == '!stop' and message.author.id in allowed_stop:
            await sys.exit()
        
        elif message.content == '!online':
            await message.channel.send('I am online')
    
        

    async def fetch_new_post(self):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        posts = soup.findAll("li", {"class": "lx-stream__post-container"})
        time = posts[0].find("span", {"class": "qa-post-auto-meta"}).text
        title = posts[0].find("h3", {"class": "qa-post-title"}).text
        texts = posts[0].findAll("p")
        imgs = posts[0].findAll("img")
        imgs_url = []
        for img in imgs:
            imgs_url.append(img['data-src'].replace('{width}', '1024'))
        return (time, title, texts, imgs_url)

            


client = MyClient()
client.run(token)
