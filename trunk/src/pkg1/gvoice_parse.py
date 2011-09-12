import xml.etree.ElementTree
import re
import datetime

def parseDate (datestring):
    #what does pattern really mean>
    parseddate = datetime.datetime.strptime(datestring, '%Y-%m-%dT%H:%M:%S.%fZ') 
    parseddate += datetime.timedelta(0, 0, parseddate.microsecond * 999)  #since input is milliesconds
    return parseddate

def parseTime (timestring):
    #what does real pattern really mean
    timestringmatch = re.search('(\d\d+):(\d\d):(\d\d)', timestring)
    seconds = 0
    seconds += int(timestringmatch.group(3))
    seconds += int(timestringmatch.group(2)) * 60
    seconds += int(timestringmatch.group(1)) * 3600
    return seconds

def asXHTML (path):
    return re.sub('/(?=\w)', '/{http://www.w3.org/1999/xhtml}', path)

def findContact(node):
    contact = node.find(asXHTML('.//cite[@class="sender vcard"]/a[@class="tel"]'))
    if contact is None:
        contact = node.find(asXHTML('.//div[@class="contributor vcard"]/a[@class="tel"]'))
    #name
    print contact.findtext(asXHTML('./span[@class="fn"]'))
    #phone number
    print re.search('\d+', contact.attrib['href']).group(0)

def processTextMsgs(textNodes, oneWayName):
    print oneWayName
    print '---------------------'
    for i in textNodes:
        findContact(i)
        print parseDate(i.find(asXHTML('./abbr[@class="dt"]')).attrib["title"])
        #text
        print i.findtext(asXHTML('./q'))
        #newline
        print '----'

def processCall(audioNode):
    findContact(audioNode)
    #time
    print parseDate(audioNode.find(asXHTML('./abbr[@class="published"]')).attrib["title"])
    durationNode = audioNode.findtext(asXHTML('./abbr[@class="duration"]'))
    if durationNode is not None:
        #duration
        print parseTime(durationNode.findtext('.'))
    for i in audioNode.findall(asXHTML('./div[@class="tags"]/a[@rel="tag"]')):
        print i.findtext('.')

def processAudio(audioNode):
    findContact(audioNode)
    #time
    #duration
    duration = parseTime(audioNode.findtext(asXHTML('./abbr[@class="duration"]')))
    time = parseDate(audioNode.find(asXHTML('./abbr[@class="published"]')).attrib["title"]) - datetime.timedelta(0, duration)
    print time
    print duration
    descriptionNode = audioNode.find(asXHTML('./span[@class="description"]'))
    if descriptionNode is not None:
        #fullText
        print descriptionNode.findtext(asXHTML('./span[@class="full-text"]'))
        #average confidence
        confidenceValues = descriptionNode.findall(asXHTML('./span/span[@class="confidence"]'))
        totalConfid = 0
        for i in confidenceValues:
            totalConfid += float(i.findtext('.'))
        print totalConfid / len(confidenceValues)
    #audio file
    print audioNode.find(asXHTML('./audio')).attrib["src"]    
    for i in audioNode.findall(asXHTML('./div[@class="tags"]/a[@rel="tag"]')):
        print i.findtext('.')



def process_file(tree):
    textNodes = tree.findall(asXHTML('.//div[@class="hChatLog hfeed"]/div[@class="message"]'))
    if len(textNodes) > 0:
        processTextMsgs(textNodes, re.match('Me to (.*)', tree.findtext(asXHTML('.//title'))))
    else:
        audioNode = tree.find(asXHTML('.//div[@class="haudio"]'))
        if audioNode.find(asXHTML('./audio')) is None: #Not actual call
            processCall(audioNode)
        else:
            processAudio(audioNode)