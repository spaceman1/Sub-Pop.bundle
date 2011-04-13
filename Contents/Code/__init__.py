import re, string, datetime

NAMESPACE   = {'media':'http://search.yahoo.com/mrss/'}
VIDEO_PREFIX      = "/video/subpop"
PHOTO_PREFIX      = "/photos/subpop"
MUSIC_PREFIX      = "/music/subpop"

BASE_URL = "http://www.subpop.com"
PHOTOS_RSS = BASE_URL + "/rss/image"
PODCAST_RSS = BASE_URL + "/podcast"
CACHE_INTERVAL    = 86400 #24hrs
ICON = "icon-default.png"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenuVideo, "Sub Pop Records", ICON, "art-default.png")
  Plugin.AddPrefixHandler(PHOTO_PREFIX, MainMenuPictures, "Sub Pop Records", ICON, "art-default.png")
  Plugin.AddPrefixHandler(MUSIC_PREFIX, MainMenuMusic, "Sub Pop Records", ICON, "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.png')
  MediaContainer.title1 = 'Sub Pop Records'
  HTTP.SetCacheTime(CACHE_INTERVAL)
  
# Aggressive cache to avoid navigation to empty dirs
def UpdateCache():
    HTTP.Request(BASE_URL, errors='ignore')
    for item in HTML.ElementFromURL(BASE_URL).xpath('//div[@id="artist-list"]//li/a'):
       url = BASE_URL + item.get('href')
       HTTP.Request(url, errors='ignore')
    
    
def MainMenuMusic():
    dir = MediaContainer(mediaType='music')  
    thumb = "http://www.subpop.com/images/feed_image.jpg"
    dir.Append(Function(DirectoryItem(RecentMusic, "Recent Music", thumb=thumb)))
    for item in H.ElementFromURL(BASE_URL).xpath('//div[@id="artist-list"]//li/a'):
        if(item.text is not None):
          url = BASE_URL + item.get('href')
          music = HTML.ElementFromURL(url).xpath('//ul[@class="downloads"]/li[@class="track"]')
          if(len(music) > 0):
            name = item.text.strip()
            thumb = HTML.ElementFromURL(url).xpath('//ul[@class="slideshow column1"]/li/a')[0].get('href')
            dir.Append(Function(DirectoryItem(ArtistMusic, name, thumb=thumb), url = url))
    return dir

def RecentMusic(sender):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)  
    podcast = RSS.FeedFromURL(PODCAST_RSS)
    thumb = podcast.channel.image.url
    for entry in podcast['items']: 
        if(entry.links[1].type == 'audio/mp3'):
            updated = Datetime.ParseDate(entry.updated).strftime('%a %b %d, %Y')
            summary = "Author: "+entry.author 
            dir.Append(TrackItem(entry.links[0].href, title=entry.title, summary=summary, thumb=thumb, subtitle=updated))
    return dir

def ArtistMusic(sender, url):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    thumb = HTML.ElementFromURL(url).xpath('//ul[@class="slideshow column1"]/li/a')[0].get('href')
    for item in HTML.ElementFromURL(url).xpath('//ul[@class="downloads"]/li[@class="track"]'):
       title = item.xpath('span[@class="dlasset"]/a')[0].text
       title = title.replace('(MP3)','').strip()
       href = item.xpath('span[@class="dlasset"]/a')[0].get('href')
       updated = item.xpath('span[@class="dlposted"]')[0].get('title')
       subtitle = Datetime.ParseDate(updated).strftime('%a %b %d, %Y')
       dir.Append(TrackItem(href, title=title, subtitle=subtitle, thumb=thumb))
    return dir

#################################
def MainMenuVideo():
    dir = MediaContainer(mediaType='video')  
    thumb = "http://www.subpop.com/images/feed_image.jpg"
    dir.Append(Function(DirectoryItem(RecentVideos, "Recent Videos", thumb=thumb)))
    for item in HTML.ElementFromURL(BASE_URL).xpath('//div[@id="artist-list"]//li/a'):
        if(item.text is not None):
            # This takes a while. Other option is navigation to empty dirs
          url = BASE_URL + item.get('href')
          videos = HTML.ElementFromURL(url).xpath('//ul[@class="downloads"]/li[@class="video"]')
          if(len(videos) > 0):
            name = item.text.strip()
            thumb = None
            if len(HTML.ElementFromURL(url).xpath('//ul[@class="slideshow column1"]/li/a')) > 0:
                thumb = HTML.ElementFromURL(url).xpath('//ul[@class="slideshow column1"]/li/a')[0].get('href')
            dir.Append(Function(DirectoryItem(ArtistVideos, name, thumb=thumb), url = url))
    return dir
    
##################################
def RecentVideos(sender):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)  
    podcast = RSS.FeedFromURL(PODCAST_RSS)
    thumb = podcast.channel.image.url
    for entry in podcast['items']: 
        if(entry.links[1].type == 'video/mov'):
            updated = Datetime.ParseDate(entry.updated).strftime('%a %b %d, %Y')
            summary = "Author: "+entry.author 
            dir.Append(VideoItem(entry.links[0].href, title=entry.title, summary=summary, thumb=thumb, subtitle=updated))
    return dir

#########################################
def ArtistVideos(sender, url):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    page = HTML.ElementFromURL(url)
    thumb = page.xpath('//ul[@class="slideshow column1_wide"]/li/a')[0].get('href')
    for item in page.xpath('//ul[@class="downloads"]/li[@class="video"]'):
       title = item.xpath('span[@class="dlasset"]/a')[0].text
       title = title.replace('(MOV)','').strip()
       href = item.xpath('span[@class="dlasset"]/a')[0].get('href')
       updated = item.xpath('span[@class="dlposted"]')[0].get('title')
       subtitle = Datetime.ParseDate(updated).strftime('%a %b %d, %Y')
       dir.Append(VideoItem(href, title=title, subtitle=subtitle, thumb=thumb))
    return dir

#########################################################
def MainMenuPictures():
  dir = MediaContainer(mediaType='pictures')
  thumb = "http://www.subpop.com/images/feed_image.jpg"
  dir.Append(Function(DirectoryItem(RecentPictures, "Recent Pictures", thumb=thumb)))
  for item in HTML.ElementFromURL(BASE_URL).xpath('//div[@id="artist-list"]//li/a'):
        if(item.text is not None):
            
           url = BASE_URL + item.get('href')
           promoPhotos = HTML.ElementFromURL(url).xpath('//ul[@id="promo_photo"]')
           albumCovers = HTML.ElementFromURL(url).xpath('//ul[@id="album-covers"]')
           if(len(promoPhotos) > 0 or len(albumCovers) > 0):
              name = item.text.strip()
              if len(HTML.ElementFromURL(url).xpath('//ul[@class="slideshow column1"]/li/a')) > 0:
                  thumb = HTML.ElementFromURL(url).xpath('//ul[@class="slideshow column1"]/li/a')[0].get('href')
                  dir.Append(Function(DirectoryItem(ArtistPictures, name, thumb=thumb), url = url))
  return dir
  
def ArtistPictures(sender, url):
    dir = MediaContainer(title2=sender.itemTitle) 
    thumb = HTML.ElementFromURL(url).xpath('//ul[@class="slideshow column1"]/li/a')[0].get('href')
    for item in HTML.ElementFromURL(url).xpath('//ul[@id="promo_photo"]/li'):
       title = item.xpath('span[@class="dlasset"]/a')[0].text
       href = item.xpath('span[@class="dlasset"]/a')[0].get('href')
       updated = item.xpath('span[@class="dlposted"]')[0].get('title')
       subtitle = Datetime.ParseDate(updated).strftime('%a %b %d, %Y')
       dir.Append(PhotoItem(href, title=title, subtitle=subtitle))
    for item in HTML.ElementFromURL(url).xpath('//ul[@id="album-covers"]/li'):
       title = item.xpath('span[@class="dlasset"]/a')[0].text
       href = item.xpath('span[@class="dlasset"]/a')[0].get('href')
       updated = item.xpath('span[@class="dlposted"]')[0].get('title')
       subtitle = Datetime.ParseDate(updated).strftime('%a %b %d, %Y')
       dir.Append(PhotoItem(href, title=title, subtitle=subtitle))
    return dir

##################################
def RecentPictures(sender):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)  
    podcast = RSS.FeedFromURL(PHOTOS_RSS)
    for entry in podcast['items']: 
        updated = Datetime.ParseDate(entry.updated).strftime('%a %b %d, %Y')
        summary = StripHTML(entry.summary, True)
        summary = summary + "Author: "+entry.author 
        pictureUrl = entry.links[0].href
        dir.Append(PhotoItem(pictureUrl, title=entry.title, summary=summary, subtitle=updated))
    return dir

######################################################
# Thanks to Gordon J.
def StripHTML(stringToStrip,paragraphsToNewLines):
  # Srips HTML tags from a string
  if paragraphsToNewLines:
    stringToStrip = re.sub(r'<\s*/p>', r'\n\n', stringToStrip)
  stringToStrip = re.sub(r'<[^>]*>', r'', stringToStrip)
  return stringToStrip