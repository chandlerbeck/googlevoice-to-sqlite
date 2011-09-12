'''
Created on Sep 9, 2011

@author: Arithmomaniac 

'''
import os
import gvoice_parse




if __name__ == '__main__':
    os.chdir('C:\Users\AviLevin\Downloads\conversations')
    files = os.listdir('.')
    for fl in files:
        if fl.endswith('.html'):
            with open(fl, 'r') as f:
                print f.read(256)
            #tree = xml.etree.ElementTree.ElementTree()
            # do indirectly so can handle brs
            # tree.fromstring(f.read().replace('<br>', '<br />'))
                #gvoice_parse.process_file(tree)