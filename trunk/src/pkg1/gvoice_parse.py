import re
import datetime
import copy

class Contact:
    def __init__(self):
        self.phonenumber = None
        self.name = None
    def dump(self):
        return "%s (%s)" % (self.name, self.phonenumber)
    def test(self):
        return self.phonenumber != None or self.name != None  
    
class Text:
    def __init__(self):
        self.contact = Contact()
        self.date = None
        self.text = None
    def dump(self):
        return "%s; %s; \"%s\"" % (self.contact.dump(), self.date, self.text)

class TextConversation:
    def __init__(self):
        self.contact = Contact()
        self.texts = []
    def dump(self):
        returnstring = self.contact.dump()
        for i in self.texts:
            returnstring += "\n\t%s" % i.dump()
        return returnstring

class Call:
    def __init__(self):
        self.contact = Contact()
        self.date = None
        self.duration = None
        self.calltype = None
    def dump(self):
        return "%s\n%s; %s(%s)" % (self.calltype, self.contact.dump(), self.date, self.duration)

class Audio:
    def __init__(self):
        self.contact = Contact()
        self.audiotype = None
        self.date = None
        self.duration = None
        self.text = None
        self.confidence = None
        self.filename = None
    def dump(self):
        return "%s\n%s; %s(%s); [%s]%s" % (self.audiotype, self.contact.dump(), self.date, self.duration, self.confidence, self.text)
##-------------

def parseDate (datestring):
    #what does pattern really mean>
    #print datestring
    parseddate = datetime.datetime.strptime(datestring, '%Y-%m-%dT%H:%M:%S.%fZ')
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
    #returnvalue = path
    returnvalue = re.sub('/(?=\w)', '/{http://www.w3.org/1999/xhtml}', path)
    #print returnvalue
    return returnvalue

##------------------------------------

def getLabel(node):
    labelNodes = node.findall(asXHTML('./div[@class="tags"]/a[@rel="tag"]'))
    validtags = ['Placed', 'Received', 'Missed', 'Recorded', 'Voicemail']
    for i in labelNodes:
        label = i.findtext('.')
        if label in validtags:
            return label
    return None

def findContact(node):
    content_obj = Contact()
    contactnode = node.find(asXHTML('.//cite[@class="sender vcard"]/a[@class="tel"]'))
    if contactnode is None:
        contactnode = node.find(asXHTML('.//div[@class="contributor vcard"]/a[@class="tel"]'))
    #name
    content_obj.name = contactnode.findtext(asXHTML('./span[@class="fn"]'))
    if content_obj.name != None and len(content_obj.name) == 0:
        content_obj.name = None
    #phone number
    contactphonenumber = re.search('\d+', contactnode.attrib['href'])
    if contactphonenumber != None:
        content_obj.phonenumber = contactphonenumber.group(0)
    return content_obj

def processTextMsgs(textNodes, oneWayName):
    text_collection = TextConversation()
    text_collection.texts = []
    #print oneWayName
    #print '---------------------'
    for i in textNodes:
        textmsg = Text()
        textmsg.contact = findContact(i)
        if textmsg.contact == None:
                print 'Oops!'
                break
        if text_collection.contact.test() == False:
                if textmsg.contact.name != None:
                    text_collection.contact = copy.deepcopy(textmsg.contact)
        textmsg.date = parseDate(i.find(asXHTML('./abbr[@class="dt"]')).attrib["title"])
        #text
        textmsg.text = i.findtext(asXHTML('./q')) #to do: html decoder
        text_collection.texts.append(copy.deepcopy(textmsg))
        #newline
    if not text_collection.contact.test():
        text_collection.contact.name = oneWayName
    return text_collection

def processCall(audioNode):
    call_obj = Call()
    call_obj.contact = findContact(audioNode)
    #time
    call_obj.date = parseDate(audioNode.find(asXHTML('./abbr[@class="published"]')).attrib["title"])
    durationNode = audioNode.findtext(asXHTML('./abbr[@class="duration"]'))
    if durationNode != None:
        #duration
        call_obj.duration = parseTime(durationNode)
    call_obj.calltype = getLabel(audioNode)
    return call_obj

def processAudio(audioNode):
    audio_obj = Audio()
    audio_obj.contact = findContact(audioNode)
    #time
    #duration
    audio_obj.duration = parseTime(audioNode.findtext(asXHTML('./abbr[@class="duration"]')))
    audio_obj.date = parseDate(audioNode.find(asXHTML('./abbr[@class="published"]')).attrib["title"]) - datetime.timedelta(0, audio_obj.duration)
    #print audio_obj.date
    #print audio_obj.duration
    descriptionNode = audioNode.find(asXHTML('./span[@class="description"]'))
    if descriptionNode != None and len(descriptionNode.findtext(asXHTML('./span[@class="full-text"]'))) > 0:
        #fullText
        fullText = descriptionNode.findtext(asXHTML('./span[@class="full-text"]')) #to do: html decoder
        if fullText != 'Unable to transcribe this message.':
            audio_obj.text = fullText
        #average confidence
        confidenceValues = descriptionNode.findall(asXHTML('./span/span[@class="confidence"]'))
        totalConfid = 0
        for i in confidenceValues:
            totalConfid += float(i.findtext('.'))
        audio_obj.confidence = totalConfid / len(confidenceValues)
    #audio file
    audio_obj.filename = audioNode.find(asXHTML('./audio')).attrib["src"]    
    audio_obj.audiotype = getLabel(audioNode)
    return audio_obj

##-------------------

def process_file(tree, filename = None):
    textNodes = tree.findall(asXHTML('.//div[@class="hChatLog hfeed"]/div[@class="message"]'))
    if len(textNodes) > 0:
        obj = processTextMsgs(textNodes, re.match('(.*?)(?= - \d\d\d\d-\d\d-\d\dT\d\d-\d\d-\d\dZ)', filename).group(0))
    else:
        audioNode = tree.find(asXHTML('.//div[@class="haudio"]'))
        if audioNode.find(asXHTML('./audio')) is None: #Not actual call
            obj = processCall(audioNode)
        else:
            obj = processAudio(audioNode)
    return obj