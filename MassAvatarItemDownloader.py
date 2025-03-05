import requests
import hashlib
import shutil
import math
import os
import datetime
import xml.etree.ElementTree as ET

XMLNamespaces = {'default': 'http://marketplace.xboxlive.com/resource/product/v1', 'a': 'http://www.w3.org/2005/Atom'}

def time2DOSTIME(hours, minutes, seconds):
    if int(hours) > 24:
        hours = '24'
    if int(minutes) > 59:
        minutes = '59'
    if math.floor(int(seconds)/2) > 29:
        seconds = '58'
        
    dosTime = ((((int(hours) << 6) | int(minutes)) << 5) | math.floor(int(seconds)/2)).to_bytes(2, byteorder="little")
    return dosTime
    
def date2DOSDATE(year, month, day):
    if int(year) > 2099:
        year = '2099'
    if int(month) > 12:
        month = '12'
    if int(day) > 31:
        day = '31'
    
    dosDate = ((((int(year)-1980 << 4) | int(month)) << 5) | int(day)).to_bytes(2, byteorder="little")
    return dosDate
    
def cleanPathString(string):
    badChars = '<>:"/\|?*'
    for char in badChars:
        string = string.replace(char, '')
        
    return string

def makeFolder(folderPath):
    try:
        os.makedirs(folderPath)
    except(FileExistsError):
        if folderPath == 'avataritems_raw' or folderPath == 'avataritems_compiled' or folderPath == 'avataritems_compiled_sorted':
            return
        print(f'folder: {folderPath}, already exists')

makeFolder('avataritems_raw')
makeFolder('avataritems_compiled')
makeFolder('avataritems_compiled_sorted')

def CreateAvatarSTFS(id):
    titleId = id[-8:]

    icon128 = 0
    icon64 = 0

    asset_v2 = requests.get(f'http://download.xboxlive.com/content/{titleId}/avataritems/v2/{id}.bin')
    XMLFile = requests.get(f'http://marketplace-xb.xboxlive.com/marketplacecatalog/v1/product/en-US/{id}?tiers=1.2.3.4.5.6.7.8.9.10&offerfilter=1')
    assetXML = ET.fromstring(XMLFile.text)

    for node in assetXML.findall('.//default:fullTitle', XMLNamespaces):
        if node.text != "Query Result":
            name = node.text.rstrip()
            print(name)
            break

    for node in assetXML.findall('.//default:fullDescription', XMLNamespaces):
        if node.text != "Query Result":
            desc = node.text.rstrip()
            print(desc)
            break

    for node in assetXML.findall('.//default:publisherName', XMLNamespaces):
        if node.text != "Query Result":
            publisher = node.text.rstrip()
            print(publisher)
            break

    for node in assetXML.findall('.//default:gameReducedTitle', XMLNamespaces):
        if node.text != "Query Result":
            gameName = node.text.rstrip()
            print(gameName)
            break

    for node in assetXML.findall('.//default:globalOriginalReleaseDate', XMLNamespaces):
        if node.text != "Query Result":
            dateTimeXMLString = node.text.rstrip().replace('Z','')
            print(dateTimeXMLString)
            break
    
    if len(assetXML.findall('.//default:globalOriginalReleaseDate', XMLNamespaces)) < 1:
        for node in assetXML.findall('.//default:visibilityDate', XMLNamespaces):
            if node.text != "Query Result":
                dateTimeXMLString = node.text.rstrip().replace('Z','').split('.', 1)[0]
                print(dateTimeXMLString)
                break
    
    if len(assetXML.findall('.//default:visibilityDate', XMLNamespaces)) < 1:
        dateTimeXMLString = 'invalidDateTime'
    
    for node in assetXML.find('.//a:entry', XMLNamespaces):
        if node.tag == '{'+XMLNamespaces['a']+'}' + "updated":
            updDateTimeXMLString = node.text.split('.', 1)
            updDateTimeXMLString = updDateTimeXMLString[0].rstrip().replace('Z','')
            print(updDateTimeXMLString)
            break
    
    if not 'desc' in locals():
        desc = name
    if not 'publisher' in locals():
        publisher = name
    if not 'gameName' in locals():
        gameName = name

    namewithspaces = ' '.join(name.split('-'))
    idnodash = ''.join(id.split('-'))

    print(f'{name}:{id}')

    path = os.getcwd()+'/avataritems_raw/'+cleanPathString(gameName)+'/'+cleanPathString(name)+'/'
    compiledPath = os.getcwd()+'/avataritems_compiled/'+titleId.upper()+'/'+"00009000"+'/'
    compiledSortedPath = os.getcwd()+'/avataritems_compiled_sorted/'+cleanPathString(gameName)+'/'+cleanPathString(name)+'/'

    print(path+'\n'+compiledSortedPath+'\n'+compiledPath)

    makeFolder(path)
    makeFolder(compiledPath)
    makeFolder(compiledSortedPath)
    
    
    assetv2Path = path+'asset_v2.bin'
    idTxtPath = path+'ID.TXT'
    xmlPath = path+f'{id}.xml'
    icon128Path = path+'ICON.PNG'
    icon64Path = path+'ICON64.PNG'
    assetNum = 0
    
    while os.path.exists(assetv2Path):
        assetNum += 1
        assetv2Path = path+f'asset_v2_{assetNum}.bin'
        
    while os.path.exists(idTxtPath):
        idTxtPath = path+f'ID_{assetNum}.TXT'
        
    while os.path.exists(xmlPath):
        assetv2Path = path+f'{id}_{assetNum}.xml'
        
    while os.path.exists(icon128Path):
        icon128Path = path+f'ICON_{assetNum}.PNG'
        
    while os.path.exists(icon64Path):
        icon64Path = path+f'ICON64_{assetNum}.PNG'
        
    
    with open(assetv2Path,'wb') as file:
        file.write(asset_v2.content)
        asset_v2 = asset_v2.content[320:]

    with open(idTxtPath,'w') as file:
        file.write(id + "\n")
        file.write(titleId)
        
    with open(xmlPath,'w',encoding="utf-8") as file:
        file.write(XMLFile.text)

    with open(icon128Path,'wb') as file:
        icon = requests.get(f'http://avatar.xboxlive.com/global/t.{titleId}/avataritem/{id}/128')
        file.write(icon.content)
        icon128 = icon.content

    with open(icon64Path,'wb') as file:
        icon = requests.get(f'http://avatar.xboxlive.com/global/t.{titleId}/avataritem/{id}/64')
        file.write(icon.content)
        icon64 = icon.content


    nullName = ('\x00' + "".join([char + '\x00' for char in name])).encode('utf-8')
    nullDesc = ('\x00' + "".join([char + '\x00' for char in desc])).encode('utf-8')
    nullPublisher = ('\x00' + "".join([char + '\x00' for char in publisher])).encode('utf-8')
    nullGameName = ('\x00' + "".join([char + '\x00' for char in gameName])).encode('utf-8')
    
    if len(nullName) > 0x100:
        nullName = nullName[:-(len(nullName)-0x100)]
    if len(nullDesc) > 0x100:
        nullDesc = nullDesc[:-(len(nullDesc)-0x100)]
    if len(nullPublisher) > 0x80:
        nullPublisher = nullPublisher[:-(len(nullPublisher)-0x80)]
    if len(nullGameName) > 0x80:
        nullGameName = nullGameName[:-(len(nullGameName)-0x80)]

    if dateTimeXMLString != 'invalidDateTime':
        dateString, timeString = dateTimeXMLString.split('T', 1)
    else:
        curDateTime = datetime.datetime.now().split('.', 1)
        curDateTime = curDateTime[0]
        
        dateString, timeString = curDateTime.split(' ', 1)
        

    hours, minutes, seconds = timeString.split(':', 2)
    year, month, day = dateString.split('-', 2)

    dosTime = time2DOSTIME(hours, minutes, seconds)
    dosDate = date2DOSDATE(year, month, day)

    if updDateTimeXMLString:
        updDateString, updTimeString = updDateTimeXMLString.split('T', 1)
    else:
        curDateTime = datetime.datetime.now().split('.', 1)
        curDateTime = curDateTime[0]
        
        updDateString, updTimeString = curDateTime.split(' ', 1)
        

    uHours, uMinutes, uSeconds = updTimeString.split(':', 2)
    uYear, uMonth, uDay = updDateString.split('-', 2)

    updDosTime = time2DOSTIME(uHours, uMinutes, uSeconds)
    updDosDate = date2DOSDATE(uYear, uMonth, uDay)

    container = b'LIVE'
    container += b'\x00' * 0x0100 #0x100 bytes of Package Signature, ignore for now.
    container += b'\x00' * 0x0128 #0x128 bytes of padding to licenses.

    container += b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00' #First entry in Licenses portion, always 0xFF * 8 as XUID, 0x00 * 4 as bits, and 0x00 * 4 as flags.
    for i in range(len(xuid)):
        container += bytes.fromhex(xuid[i]) #Insert XUID.
        container += b'\x00\x00\x00\x00\x00\x00\x00\x00' #No flags or bits to set, wonder what those do.

    container += b'\x00' * (0x032c - len(container)) #Padding.

    container += b'HEADERSHA1HASHINHERE' #Header SHA1 Hash in V1 Metadata. Replace later as theres nothing to hash atm. Stored at offset 0x32C - 0x340.
    container += b'\x00\x00\xAD\x0E' #HeaderSize. Always 00 00 AD 0E (?).

    container += b'\x00\x00\x90\x00' #Content Type. Set to Avatar Item.
    container += b'\x00\x00\x00\x02' #Metadata Version. Hex is 0x00000002 but its actually version 1? weird.
    container += b'CONTSIZE' #Content Size. Replace later.

    container += b'\x00' * 0x04 #Media ID. Unused(?) on Avatar items so write 0x00.
    container += b'\x00' * 0x04 #Version. Unused(?) on Avatar items so write 0x00.
    container += b'\x00' * 0x04 #Base Version. Unused(?) on Avatar items so write 0x00.

    container += bytes.fromhex(titleId)

    container += b'\x00' #Platform. Unused(?).
    container += b'\x00' #Executable Type. Unused(?).
    container += b'\x00' #Disc Number. Unused(?).
    container += b'\x00' #Disc In Set. Unused(?).
    container += b'\x00' * 0x04 #Save Game ID. Unused(?) on Avatar items so write 0x00.
    container += b'\x00' * 0x05 #Console ID. Unused(?) on Avatar items so write 0x00.
    container += b'\x00' * 0x08 #Profile ID. Unused(?) on Avatar items so write 0x00.

    container += b'\x24' #Volume descriptor size, always 0x24.
    container += b'\x00' #Reserved. Unknown.
    container += b'\x01' #Block Seperation, always 0x01.
    container += b'\x01\x00' #File Table Block Count, always 0x01 0x00.
    container += b'\x00' * 0x03 #File Table Block Number, always 0x00 0x00 0x00.
    container += b'TOPHASHTABLEHASHHERE' #Top Hash Table Hash (Hash of Top Hash's Table), replace later.
    container += b'bCNT' #Total Allocated Block Count. Replace Later.
    container += b'\x00' * 0x04 #Total Unallocated Block Count. Always 0.

    container += b'\x00' * 0x04 #Data File Count. Unused(?) on Avatar items so write 0x00.
    container += b'\x00' * 0x08 #Data File Combined Size. Unused(?) on Avatar items so write 0x00.
    container += b'\x00' * 0x04 #Descriptor Type. Always 0x00 0x00 0x00 0x00 to represent STFS.
    container += b'\x00' * 0x04 #Reserved. Unknown.
    
    #This Block of code is supposedly only supposed to be 0x00 * 0x4C of padding yet it clearly isnt, free60.org has some wrong info on STFS.
    container += b'\x00' * 0x30 #Padding.
    container += bytes.fromhex(idnodash) #ID of the Avatar Item
    container += b'\x03' #VERY IMPORTANT BYTE, without the byte after idnodash being 0x03 the XBox wont recognize the Avatar Item. It will show without an icon and be unselectable, disappearing next time the closet is loaded.
    container += b'\x00' * 0x0B #Padding.
    container += b'\x00' * 0x14 #Device ID. Unused(?) on Avatar items so write 0x00.

    #9 Display Names, 9 Descriptions. 1 Publisher, 1 Title (Game) Name.

    for i in range(9):
        container += nullName
        container += b'\x00' * (0x100 - len(nullName))

    for i in range(9):
        container += nullDesc
        container += b'\x00' * (0x100 - len(nullDesc))

    container += nullPublisher
    container += b'\x00' * (0x80 - len(nullPublisher))
    container += nullGameName
    container += b'\x00' * (0x80 - len(nullGameName))

    #Actual Data (Images and BIN)
    container += b'\xC0' #Transfer Flags. 11000000 in Binary, meaning Device ID + Profile ID Transfer(able? idk)
    container += len(icon64).to_bytes(4, byteorder="big") #Thumbnail Image Size. 4 Byte Int with Big Endian order.
    container += len(icon64).to_bytes(4, byteorder="big") #Title Thumbnail Image Size. 4 Byte Int with Big Endian order.

    container += icon64 #Thumbnail Image Data.
    container += b'\x00' * (0x4000 - len(icon64)) #Padding.

    container += icon64 #Title Thumbnail Image Data.
    container += b'\x00' * (0x58E6 - len(icon64)) #Padding.

    #0xC000, File Table.
    assetBlockCount = math.ceil((len(asset_v2)/0x1000)).to_bytes(3, byteorder="little")
    iconBlockCount = math.ceil((len(icon128)/0x1000)).to_bytes(3, byteorder="little")
    secStart = len(container)

    container += b'asset_v2.bin' #Bin Name.
    container += b'\x00' * (0x28 - len(b'asset_v2.bin')) #Padding.
    container += len(b'asset_v2.bin').to_bytes(1, byteorder="big") #Length of file name, plus flags
    container += assetBlockCount #Number of blocks allocated for file (little endian)
    container += assetBlockCount #Number of blocks allocated for file (little endian)
    container += b'\x01\x00\x00' #asset_v2.bin Block Location (little endian). Its always in Block 1 hence 0x01 0x00 0x00.
    container += b'\xFF\xFF' #Path Indicator. Always 0xFF 0xFF.
    container += len(asset_v2).to_bytes(4, byteorder="big") #Size of asset in bytes.
    container += updDosTime #Update DOSTIME (0x02 bytes at 0xC038)
    container += updDosDate #Update DOSDATE (0x02 bytes at 0xC03A)
    container += dosTime #Access DOSTIME (0x02 bytes at 0xC03C)
    container += dosDate #Access DOSDATE (0x02 bytes at 0xC03E)

    container += b'icon.png' #Bin Name.
    container += b'\x00' * (0x28 - len(b'icon.png')) #Padding.
    container += len(b'icon.png').to_bytes(1, byteorder="big") #Length of file name, plus flags
    container += iconBlockCount #Number of blocks allocated for file (little endian)
    container += iconBlockCount #Number of blocks allocated for file (little endian)
    container += (math.ceil((len(asset_v2)/0x1000))+1).to_bytes(3, byteorder="little") #icon.png Block Location (little endian). Its always in Block 1 hence 0x01 0x00 0x00.
    container += b'\xFF\xFF' #Path Indicator. Always 0xFF 0xFF.
    container += len(icon128).to_bytes(4, byteorder="big") #Size of asset in bytes.
    container += updDosTime #Update DOSTIME (0x02 bytes at 0xC038)
    container += updDosDate #Update DOSDATE (0x02 bytes at 0xC03A)
    container += dosTime #Access DOSTIME (0x02 bytes at 0xC03C)
    container += dosDate #Access DOSDATE (0x02 bytes at 0xC03E)

    container += b'\x00' * (0x1000 - (len(container) - secStart)) #Padding to next block.

    #0xD000, asset_v2.bin Blocks Start.
    secStart = len(container)
    container += asset_v2
    container += b'\x00' * (0x1000 - ((len(container) - secStart) % 0x1000)) #Padding to next block.

    #Non-Constant Block Address, icon.png Blocks Start.
    secStart = len(container)
    container += icon128
    container += b'\x00' * (0x1000 - ((len(container) - secStart) % 0x1000)) #Padding to next block.

    #0xB000, First (and only) Hash Table.
    hashTable = b'' #Empty Hashtable.
    croppedContainer = container[0xB000:] #Container cropped to only contain Blocks (0xC000 and beyond).
    blockCount = int(len(croppedContainer)/0x1000)

    for i in range(blockCount):
        if i == blockCount:
            break
        curBlock = croppedContainer[(0x1000 * i):-(0x1000 * (blockCount - i - 1))]
        
        blockHash = hashlib.sha1(curBlock)
        blockHash = blockHash.digest()
        hashTable += blockHash
        hashTable += b'\x80'
        
        if i == 0 or i == int.from_bytes(assetBlockCount, byteorder="little") or i == int.from_bytes(assetBlockCount, byteorder="little") + int.from_bytes(iconBlockCount, byteorder="little"):
            hashTable += b'\xFF\xFF\xFF'
        else:
            hashTable += (i+1).to_bytes(3, byteorder="big")

    container = container[:0xB000] + hashTable + (b'\x00' * (0x1000-len(hashTable)) + container[0xB000:])

    container = container.replace(b'CONTSIZE', len(container[0xB000:]).to_bytes(8, byteorder="big"))

    container = container.replace(b'TOPHASHTABLEHASHHERE', hashlib.sha1(hashTable + (b'\x00' * (0x1000-len(hashTable)))).digest()) #Replace Top Hash Table Hash with the Hash Table's SHA-1 Hash.
    container = container.replace(b'bCNT', blockCount.to_bytes(4, byteorder="big"))

    container = container.replace(b'HEADERSHA1HASHINHERE', hashlib.sha1(container[0x0344:-(0x1000*(blockCount+1))]).digest()) #Insert Header SHA-1 Hash.

    newContainer = open(compiledPath+f"/{idnodash.upper()}", 'wb')
    newContainer.write(container)
    newContainer.close()
    
    newContainer = open(compiledSortedPath+f"/{idnodash.upper()}", 'wb')
    newContainer.write(container)
    newContainer.close()
    
    

mode = input('Input Mode ([FB] for batch filename conversion, [TB] for batch text list conversion, [I] for entering single ID): ')

if mode.lower() == 'fb':
    pathInput = input('Path to Folder with Item IDs: ')
elif mode.lower() == 'tb':
    pathInput = input('Path to Text File with Item IDs (newline after each ID): ')
else:
    idInput = input('Item ID (EX. 00XXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX): ')

xuid = []

for i in range(15):
    xuid.append(input(f'XUID No. {i+1} (EX. 00090000XXXXXXXX) (Press Enter without typing to stop): '))
    if xuid[i] == '':
        del xuid[i]
        break

if mode.lower() == 'fb':
    existingFileNames = []
    for folder, subs, files in os.walk('avataritems_compiled'):
        for filename in files:
            existingFileNames.append(filename)
            
    existingFileNames = set(existingFileNames)

    for folder, subs, files in os.walk(pathInput):
        for filename in files:
            if filename[-3:] == 'bin' and not (''.join(filename[:-4].split('-')).upper() in existingFileNames):
                if (''.join(filename[:-4].split('-')) in existingFileNames):
                    continue
                CreateAvatarSTFS(filename[:-4])
elif mode.lower() == 'tb':
    textFile = open(pathInput, 'r')
    splitIDs = textFile.read().splitlines()
    
    for i, textID in enumerate(splitIDs):
        CreateAvatarSTFS(textID)
else:
    CreateAvatarSTFS(idInput)
