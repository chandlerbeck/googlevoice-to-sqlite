'''
gvoice_parse.py

A parsing library for GoogleVoice html files. Has no dependencies to other files in project
(Though the <br> fix is not automatically done here)


@author: AviLevin
'''

import re
import datetime
from copy import deepcopy
from dateutil import tz
from dateutil.parser import *
import htmlentitydefs

#the classes of GVoice objects

#Contacts
class Contact:
    __slots__ = ['name', 'phonenumber']
    def __init__(self):
        self.phonenumber = None
        self.name = None
    def dump(self): #debug info
        return "%s (%s)" % (self.name, self.phonenumber)
    def test(self): #if has values
        return self.phonenumber != None or self.name != None  
    
#Text message
class Text:
    __slots__ = ['contact', 'date', 'text']
    def __init__(self):
        self.contact = Contact()
        self.date = None
        self.text = None
    def dump(self):
        return "%s; %s; \"%s\"" % (self.contact.dump(), self.date, self.text)

#Text "conversation"; the outer container for grouped texts (they are stored in HTML this way, too)
class TextConversation:
    __slots__ = ['contact', 'texts']
    def __init__(self):
        self.contact = Contact()
        self.texts = []
    def dump(self):
        returnstring = self.contact.dump()
        for i in self.texts:
            returnstring += "\n\t%s" % i.dump()
        return returnstring

#A phone call
class Call:
    __slots__ = ['contact', 'date', 'duration', 'calltype']
    def __init__(self):
        self.contact = Contact()
        self.date = None
        self.duration = None
        self.calltype = None #Missed, Placed, Received
    def dump(self):
        return "%s\n%s; %s(%s)" % (self.calltype, self.contact.dump(), self.date, self.duration)

class Audio:
    __slots__ = ['contact', 'audiotype', 'date', 'duration', 'text', 'confidence', 'filename']
    def __init__(self):
        self.contact = Contact()
        self.audiotype = None   #'Voicemail' or 'Recorded'
        self.date = None
        self.duration = None
        self.text = None        #the text of the recording/voicemail
        self.confidence = None  #confidence of prediction
        self.filename = None    #filename of audio file
    def dump(self):
        return "%s\n%s; %s(%s); [%s]%s" % (self.audiotype, self.contact.dump(), self.date, self.duration, self.confidence, self.text)
##---------------------------

#Parsing help functions

#from effbot.org. HTML unescape
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

#Parses a Gvoice-formatted date into a datetime object
def parse_date (datestring):
    returntime = parse(datestring).astimezone(tz.tzutc())
    return returntime.replace(tzinfo = None)
	
	
#Parses the "duration" tag into the number of seconds it encodes
def parse_time (timestring):
    #what does real pattern really mean
    timestringmatch = re.search('(\d\d+):(\d\d):(\d\d)', timestring)
    seconds = 0
    seconds += int(timestringmatch.group(3))
    seconds += int(timestringmatch.group(2)) * 60
    seconds += int(timestringmatch.group(1)) * 3600
    return seconds

#As the HTML has an XML namespace, it would need to be specified for every XPATH node. This automates that obnoxious step
def as_xhtml (path):
    return re.sub('/(?=\w)', '/{http://www.w3.org/1999/xhtml}', path)
##------------------------------------


#Gets a category label from the HTNL file
#TO DO: return Inbox, Starred flags
def get_label(node):
    labelNodes = node.findall(as_xhtml('./div[@class="tags"]/a[@rel="tag"]'))
    validtags = ('Placed', 'Received', 'Missed', 'Recorded', 'Voicemail') #Valid categories
    for i in labelNodes:
        label = i.findtext('.')
        if label in validtags:
            return label
    return None

#Finds the first contact contained within a node. Returns it
def find_Contact(node):
    contact_obj = Contact()
    
    #two places the node could be
    contactnode = node.find(as_xhtml('.//cite[@class="sender vcard"]/a[@class="tel"]'))
    if contactnode is None:
        contactnode = node.find(as_xhtml('.//div[@class="contributor vcard"]/a[@class="tel"]'))
    
    #name
    contact_obj.name = contactnode.findtext(as_xhtml('./span[@class="fn"]'))
    if contact_obj.name != None and len(contact_obj.name) == 0: #If a blank string. Should be an isinstance
        contact_obj.name = None
    #phone number
    contactphonenumber = re.search('\d+', contactnode.attrib['href'])
    if contactphonenumber != None:
        contact_obj.phonenumber = contactphonenumber.group(0)
        
    return contact_obj

def process_TextConversation(textnodes, onewayname): #a list of texts, and the title used in special cases
    text_collection = TextConversation()
    text_collection.texts = []
    for i in textnodes:
        textmsg = Text()
        textmsg.contact = find_Contact(i)
        if text_collection.contact.test() == False: #if we don't have a contact for this conversation yet
                if textmsg.contact.name != None:    #if contact not self
                    text_collection.contact = deepcopy(textmsg.contact)    #They are other participant
        textmsg.date =parse_date(i.find(as_xhtml('./abbr[@class="dt"]')).attrib["title"])
 #date
        textmsg.text = unescape(i.findtext(as_xhtml('./q'))) #Text. TO DO: html decoder
        text_collection.texts.append(deepcopy(textmsg))
        #newline
    if not text_collection.contact.test():  #Outgoing-only conversations don't contain the recipient's contact info.
        text_collection.contact.name = onewayname #Pull fron title. No phone number, but fixed in other finction
    return text_collection

#process phone calls. Returns Call object
def process_Call(audionode):
    call_obj = Call()
    call_obj.contact = find_Contact(audionode)
    #time
    call_obj.date = parse_date(audionode.find(as_xhtml('./abbr[@class="published"]')).attrib["title"])
    #duration
    duration_node = audionode.findtext(as_xhtml('./abbr[@class="duration"]'))
    if duration_node != None:
        call_obj.duration = parse_time(duration_node)
    #Call type (Missed, Recieved, Placed)
    call_obj.calltype = get_label(audionode)
    return call_obj

#Processes voicemails, recordings
def process_Audio(audionode):
    audio_obj = Audio()
    audio_obj.contact = find_Contact(audionode)
    #time
    #duration
    audio_obj.duration = parse_time(audionode.findtext(as_xhtml('./abbr[@class="duration"]')))
    audio_obj.date = parse_date(audionode.find(as_xhtml('./abbr[@class="published"]')).attrib["title"]) - datetime.timedelta(0, audio_obj.duration)
    #print audio_obj.date
    #print audio_obj.duration
    descriptionNode = audionode.find(as_xhtml('./span[@class="description"]'))
    if descriptionNode != None and len(descriptionNode.findtext(as_xhtml('./span[@class="full-text"]'))) > 0:
        #fullText
        fullText = descriptionNode.findtext(as_xhtml('./span[@class="full-text"]')) #TO DO: html decoder
        if fullText != 'Unable to transcribe this message.':
            audio_obj.text = fullText
        #average confidence - read each confidence node (word) and average out results
        confidence_values = descriptionNode.findall(as_xhtml('./span/span[@class="confidence"]'))
        totalconfid = 0
        for i in confidence_values:
            totalconfid += float(i.findtext('.'))
        audio_obj.confidence = totalconfid / len(confidence_values)
    #location of audio file
    audio_obj.filename = audionode.find(as_xhtml('./audio')).attrib["src"]    
    #label
    audio_obj.audiotype = get_label(audionode)
    return audio_obj

##-------------------

#The main function. Takes in the file name and an ElementTree
def process_file(tree, filename = None):
    #texts
    textNodes = tree.findall(as_xhtml('.//div[@class="hChatLog hfeed"]/div[@class="message"]'))
    if len(textNodes) > 0: #is actually a text file
        #process the text files
        obj = process_TextConversation(textNodes, re.match('(.*?)(?= - \d\d\d\d-\d\d-\d\dT\d\d-\d\d-\d\dZ)', filename).group(0))
    else:
        #look for call/audio
        audioNode = tree.find(as_xhtml('.//div[@class="haudio"]'))
        if audioNode.find(as_xhtml('./audio')) is None: #no audio enclosure. Just the call record
            obj = process_Call(audioNode)
        else: #audio
            obj = process_Audio(audioNode)
    return obj