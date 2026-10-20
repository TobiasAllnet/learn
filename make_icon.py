import zlib, struct, sys
def png(path, size):
    # gradient square with a white lightning-bolt-ish "spark" made of a polygon test
    def inside(px, py, poly):
        n=len(poly); c=False; j=n-1
        for i in range(n):
            xi,yi=poly[i]; xj,yj=poly[j]
            if (yi>py)!=(yj>py) and px < (xj-xi)*(py-yi)/(yj-yi)+xi: c=not c
            j=i
        return c
    s=size
    bolt=[(.56,.14),(.30,.54),(.47,.54),(.40,.86),(.70,.44),(.52,.44)]
    bolt=[(x*s,y*s) for x,y in bolt]
    rows=[]
    for y in range(s):
        row=bytearray([0])
        for x in range(s):
            t=(x+y)/(2*s)
            r=int(79+(139-79)*t); g=int(70+(92-70)*t); b=int(229+(246-229)*t)
            if inside(x+.5,y+.5,bolt): r=g=b=255
            row+=bytes((r,g,b))
        rows.append(bytes(row))
    raw=b''.join(rows)
    def chunk(t,d):
        c=struct.pack('>I',len(d))+t+d
        return c+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',s,s,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
    open(path,'wb').write(data)
png('icon-180.png',180); png('icon-192.png',192); png('icon-512.png',512)
