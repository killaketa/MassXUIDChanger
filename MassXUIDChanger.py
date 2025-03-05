import os

def ChangeSTFSXUID(filePath):
    stfsFile = open(filePath, 'rb+')
    stfsBinary = stfsFile.read()
    xuidTable = b''
    
    stfsFile.truncate(0)
    stfsFile.seek(0)
    
    for i, xuidVal in enumerate(xuid):
        xuidTable += bytes.fromhex(xuidVal)
        xuidTable += b'\x00\x00\x00\x00\x00\x00\x00\x00'
    
    xuidTable += b'\x00' * (0x0F0 - len(xuidTable)) #Padding.

    newStfsFile = stfsBinary[:0x023C] + xuidTable + stfsBinary[-(len(stfsBinary) - 0x032C):]

    stfsFile.write(newStfsFile)
    stfsFile.close()
    
    print(filePath)
    
    

mode = input('Input Mode ([FB] for batch STFS file XUID change, [P] for single STFS file XUID change): ')

if mode.lower() == 'fb':
    pathInput = input('Path to Folder with STFS Files: ')
else:
    pathInput = input('Path to STFS File: ')

xuid = []

for i in range(15):
    xuid.append(input(f'XUID No. {i+1} (EX. 00090000XXXXXXXX) (Press Enter without typing to stop): '))
    if xuid[i] == '':
        del xuid[i]
        break

if mode.lower() == 'fb':
    for folder, subs, files in os.walk(pathInput):
        for filename in files:
            filePath = os.path.join(folder, filename)
            openFile = open(filePath, 'rb')
            if (openFile.read(4) == b'LIVE'):
                openFile.close()
                ChangeSTFSXUID(filePath)
            else:
                print(f'Invalid STFS file at {filePath}')
else:
    openFile = open(pathInput, 'rb')
    if (openFile.read(4) == b'LIVE'):
        openFile.close()
        ChangeSTFSXUID(pathInput)
    else:
        print(f'Invalid STFS file at {pathInput}')