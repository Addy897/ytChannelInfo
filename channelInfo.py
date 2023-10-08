from urllib.request import Request, urlopen
from fake_useragent import UserAgent
import re,json


def numberCount(subs:str) -> int:
    subs=subs.replace("subscribers","").replace("subscriber","")
    count=0
    if("M" in subs):
        count=float(subs.replace("M",""))
        count*=10e6
    elif("K" in subs):
        count=float(subs.replace("K",""))
        count*=10e3
    elif("B" in subs):
        count=float(subs.replace("B",""))
        count*=10e9
    else:
        count=float(subs)
    return int(count)


def getYtInitial(url:str):
    ua = UserAgent().random
    headers = {"User-Agent": ua}
    try:
        raw_data=urlopen(Request(url=url,method="GET",headers=headers)).read()
    except Exception as e:
        print(e)
        return None
    ytInitial=re.findall(b"(?:ytInitialData...)(\{\"res.*)(?:\;..script..scrip)",raw_data)[0]
    ytInitial=json.loads(ytInitial.decode())
    
    return ytInitial


def search(dictionary, key):
    stack = [dictionary]
    while stack:
        elem = stack.pop()
        if isinstance(elem, dict):
            for nkey, value in elem.items():
                if nkey == key:
                    yield value
                else:
                    stack.append(value)
        elif isinstance(elem, list):
            for i in elem:
                stack.append(i)
                    

def getChannelBaseInfo(ytInitial,channelName)->list:
    
    subCount=0
    for i in search(ytInitial, "channelRenderer"):

        tempName=i.get("title",{}).get("simpleText",None)
        tempId=i.get("navigationEndpoint",{}).get('browseEndpoint',{}).get("canonicalBaseUrl",None)

        tempSub=i.get('videoCountText',{}).get("simpleText",None)


        if(tempSub is None or tempName is None):
            continue

        tempSub=numberCount(tempSub)

        if(tempSub==channelName or tempId==channelName):
            channelId=i.get("channelId",None)
            channel_Name=i.get("title",{}).get("simpleText",None)
            channelUrl=i.get("navigationEndpoint",{}).get('browseEndpoint',{}).get("canonicalBaseUrl",None)
            subscribers=i.get('videoCountText',{}).get("simpleText",None)
            verified=i.get('ownerBadges',[{}])[0].get("metadataBadgeRenderer",{}).get("tooltip",None)
            break
        elif(tempSub>subCount):
            subCount=tempSub
            channelId=i.get("channelId",None)
            channel_Name=i.get("title",{}).get("simpleText",None)
            channelUrl=i.get("navigationEndpoint",{}).get('browseEndpoint',{}).get("canonicalBaseUrl",None)
            subscribers=i.get('videoCountText',{}).get("simpleText",None)
            verified=i.get('ownerBadges',[{}])[0].get("metadataBadgeRenderer",{}).get("tooltip",None)
        
    return [channelUrl,channelId,channel_Name,subscribers,verified]


def getVideosList(ytData) -> list:
    videosList=[]
    for i in search(ytData, "videoRenderer"):
        for j in search(i, "viewCountText"):
            views = j.get("simpleText", "Error")
            t = i.get("thumbnail").get("thumbnails")
            videoId=i.get("videoId")
        for j in search(i, "title"):
            for k in search(i,"text"):
                title2=k
        length=i.get("lengthText",[{}]).get("simpleText")
        publishedTime=i.get("publishedTimeText",{}).get("simpleText")
        videosList.append([videoId, title2,length , views, publishedTime, t[-1].get("url"),[t[-1].get("width"),t[-1].get("height")]])
    return videosList


def getAllChannels(ytData):
    channels=[]
    for i in search(ytData, "gridChannelRenderer"):
        sb, vd = None, None
        cid = i.get("navigationEndpoint",{}).get('browseEndpoint',{}).get("canonicalBaseUrl",None)

        thumbnail:str = i.get("thumbnail").get("thumbnails")[-1].get("url")
        title1=i.get('title').get('simpleText')
        width=i.get("thumbnail").get("thumbnails")[-1].get("width")
        height=i.get("thumbnail").get("thumbnails")[-1].get("height")
        if(not thumbnail.startswith("http")):
            thumbnail="https:"+thumbnail
        for j in search(i, "subscriberCountText"):
            sb = j.get("simpleText")
        for k in search(i, "videoCountText"):
            vd = k.get("runs")[0].get("text") if k.get("runs") != None else None
        channels.append([title1, vd, sb, cid, thumbnail,[int(width),int(height)]])
    return(channels)


def getChannelInfo(channelName:str):
    url=f"https://www.youtube.com/results?search_query={channelName.replace(' ','+').replace('@','')}&sp=EgIQAg%253D%253D"
    ytInitial=getYtInitial(url)
    cUrl,cId,cName,sub,verify=getChannelBaseInfo(ytInitial,channelName)

    url=f"https://www.youtube.com/{cUrl}/about"
    ytInitialAbout=getYtInitial(url)
    video,views,joined,desc,thumbnail,width,height,familySafe,fbId,keywords=[None]*10
    for i in search(ytInitialAbout, "viewCountText"):
        views = i.get("simpleText",0)
    for i in search(ytInitialAbout, "joinedDateText"):
        joined = i.get("runs",[{}])[1].get("text",0)

    url=f"https://www.youtube.com/{cUrl}"
    ytInitialHome=getYtInitial(url)
    with open("ytInitialHome.json","w") as f:
        f.write(json.dumps(ytInitial))
    for i in search(ytInitialHome, "videosCountText"):
        video = i.get("runs",[{}])[0].get("text")
    
    for i in search(ytInitialHome, "channelMetadataRenderer"):
        desc=i.get("description")
        thumbnail=i.get("avatar",{}).get("thumbnails",[{}])[-1].get("url")
        width=i.get("avatar",{}).get("thumbnails",[{}])[-1].get("width")
        height=i.get("avatar",{}).get("thumbnails",[{}])[-1].get("height")
        familySafe=i.get("isFamilySafe")
        fbId=i.get("facebookProfileId")
        keywords=i.get("keywords")
    if(thumbnail == None):
        
        for i in search(ytInitialHome,"channelRenderer"):
            desc=i.get("description",None)
            thumbnail=i.get("thumbnail",{}).get("thumbnails",[{}])[-1].get("url")
            width=i.get("thumbnail",{}).get("thumbnails",[{}])[-1].get("width")
            height=i.get("avatar",{}).get("thumbnails",[{}])[-1].get("height")
            familySafe=i.get("isFamilySafe")
            fbId=i.get("facebookProfileId")
            keywords=i.get("keywords")
            break
        
    metadata=[cName,cId,cUrl,sub, video,desc , thumbnail,familySafe, fbId,keywords , views, joined, verify,[width,height]]
    channels=getAllChannels(ytInitialHome)
    url=f"https://www.youtube.com/{cUrl}/videos"
    ytInitialVideos=getYtInitial(url)
    videosList=getVideosList(ytInitialVideos)
    return metadata,channels,videosList