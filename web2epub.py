#!python
# -*- coding: utf-8 -*-

# web2epub is a command line tool to convert a set of web/html pages to epub.
# Copyright 2012 Rupesh Kumar

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import zipfile
import urllib
import sys
import os.path
import mimetypes
import time
import urlparse
import cgi
from optparse import OptionParser
from readability.readability import Document
from BeautifulSoup import BeautifulSoup,Tag

class MyZipFile(zipfile.ZipFile):
    def writestr(self, name, s, compress=zipfile.ZIP_DEFLATED):
        zipinfo = zipfile.ZipInfo(name, time.localtime(time.time())[:6])
        zipinfo.compress_type = compress
        zipfile.ZipFile.writestr(self, zipinfo, s)



def build_command_line():
    parser = OptionParser(usage="Usage: %prog [options] url1 url2 ...urln")
    parser.add_option("-t", "--title", dest="title", help="title of the epub")
    parser.add_option("-a", "--author", dest="author", help="author of the epub")
    parser.add_option("-c", "--cover", dest="cover", help="path to cover image")
    parser.add_option("-o", "--outfile", dest="outfile", help="name of output file")
    return parser


if __name__ == '__main__':
    parser = build_command_line()
    (options, args) = parser.parse_args()
    cover = options.cover
    nos = len(args)
    cpath = 'data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
    ctype = 'image/gif'
    if cover is not None:
        cpath = 'images/cover' + os.path.splitext(os.path.abspath(cover))[1]
        ctype = mimetypes.guess_type(os.path.basename(os.path.abspath(cover)))[0]

    epub = MyZipFile(options.outfile, 'w', zipfile.ZIP_DEFLATED)
    #Metadata about the book
    info = dict(title=options.title,
            author=options.author,
            rights='Copyright respective page authors',
            publisher='Rupesh Kumar',
            ISBN='978-1449921880',
            subject='Blogs',
            description='Articles extracted from blogs for archive purposes',
            date=time.strftime('%Y-%m-%d'),
            front_cover= cpath,
            front_cover_type = ctype
            )

    # The first file must be named "mimetype"
    epub.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
    # We need an index file, that lists all other HTML files
    # This index file itself is referenced in the META_INF/container.xml file
    epub.writestr("META-INF/container.xml", '''<container version="1.0"
        xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
        <rootfiles>
            <rootfile full-path="OEBPS/Content.opf" media-type="application/oebps-package+xml"/>
        </rootfiles>
        </container>''')

    # The index file is another XML file, living per convention
    # in OEBPS/content.opf
    index_tpl = '''<package version="2.0"
        xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid">
        <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>%(title)s</dc:title>
        <dc:creator>%(author)s</dc:creator>
        <dc:language>en</dc:language>
        <dc:rights>%(rights)s</dc:rights>
        <dc:publisher>%(publisher)s</dc:publisher>
        <dc:subject>%(subject)s</dc:subject>
        <dc:description>%(description)s</dc:description>
        <dc:date>%(date)s</dc:date>
        <dc:identifier id="bookid">%(ISBN)s</dc:identifier>
        <meta name="cover" content="cover-image" />
        </metadata>
        <manifest>
          <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
          <item id="cover" href="cover.html" media-type="application/xhtml+xml"/>
          <item id="cover-image" href="%(front_cover)s" media-type="%(front_cover_type)s"/>
          <item id="css" href="stylesheet.css" media-type="text/css"/>
            %(manifest)s
        </manifest>
        <spine toc="ncx">
            <itemref idref="cover" linear="no"/>
            %(spine)s
        </spine>
        <guide>
            <reference href="cover.html" type="cover" title="Cover"/>
        </guide>
        </package>'''

    toc_tpl = '''<?xml version='1.0' encoding='utf-8'?>
        <!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
                 "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
        <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
        <head>
        <meta name="dtb:uid" content="%(ISBN)s"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
      </head>
      <docTitle>
        <text>%(title)s</text>
      </docTitle>
      <navMap>
        <navPoint id="navpoint-1" playOrder="1"> <navLabel> <text>Cover</text> </navLabel> <content src="cover.html"/> </navPoint>
        %(toc)s
      </navMap>
    </ncx>'''

    cover_tpl = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <title>Cover</title>
        <style type="text/css"> img { max-width: 100%%; } </style>
        </head>
        <body>
        <h1>%(title)s</h1>
        <div id="cover-image">
        <img src="%(front_cover)s" alt="Cover image"/>
        </div>
        </body>
        </html>'''

    stylesheet_tpl = '''
        p, body {
            font-weight: normal;
            font-style: normal;
            font-variant: normal;
            font-size: 1em;
            line-height: 2.0;
            text-align: left;
            margin: 0 0 1em 0;
            orphans: 2;
            widows: 2;
        }
        h1{
            color: blue;
        }
        h2 {
            margin: 5px;
        }
    '''

    manifest = ""
    spine = ""
    toc = ""

    epub.writestr('OEBPS/cover.html', cover_tpl % info)
    if cover is not None:
        epub.write(os.path.abspath(cover),'OEBPS/images/cover'+os.path.splitext(cover)[1],zipfile.ZIP_DEFLATED)

    for i,url in enumerate(args):
        print "Reading url no. %s of %s --> %s " % (i+1,nos,url)
        html = urllib.urlopen(url).read()
        readable_article = Document(html).summary().encode('utf-8')
        readable_title = Document(html).short_title()

        manifest += '<item id="article_%s" href="article_%s.html" media-type="application/xhtml+xml"/>\n' % (i+1,i+1)
        spine += '<itemref idref="article_%s" />\n' % (i+1)
        toc += '<navPoint id="navpoint-%s" playOrder="%s"> <navLabel> <text>%s</text> </navLabel> <content src="article_%s.html"/> </navPoint>' % (i+2,i+2,cgi.escape(readable_title),i+1)

        soup = BeautifulSoup(readable_article)
        #Add xml namespace
        soup.html["xmlns"] = "http://www.w3.org/1999/xhtml"
        #Insert header
        body = soup.html.body
        h1 = Tag(soup, "h1", [("class", "title")])
        h1.insert(0, cgi.escape(readable_title))
        body.insert(0, h1)

        #Add stylesheet path
        head = soup.find('head')
        if head is None:
            head = Tag(soup,"head")
            soup.html.insert(0, head)
        link = Tag(soup, "link", [("type","text/css"),("rel","stylesheet"),("href","stylesheet.css")])
        head.insert(0, link)
        article_title = Tag(soup, "title")
        article_title.insert(0, cgi.escape(readable_title))
        head.insert(1, article_title)

        #Download images
        for j,image in enumerate(soup.findAll("img")):
            #Convert relative urls to absolute urls
            imgfullpath = urlparse.urljoin(url, image["src"])
            #Remove query strings from url
            imgpath = urlparse.urlunsplit(urlparse.urlsplit(imgfullpath)[:3]+('','',))
            print "    Downloading image: %s %s" % (j+1, imgpath)
            imgfile = os.path.basename(imgpath)
            filename = 'article_%s_image_%s%s' % (i+1,j+1,os.path.splitext(imgfile)[1])
            if imgpath.lower().startswith("http"):
                epub.writestr('OEBPS/images/'+filename, urllib.urlopen(imgpath).read())
                image['src'] = 'images/'+filename
                manifest += '<item id="article_%s_image_%s" href="images/%s" media-type="%s"/>\n' % (i+1,j+1,filename,mimetypes.guess_type(filename)[0])

        epub.writestr('OEBPS/article_%s.html' % (i+1), str(soup))

    info['manifest'] = manifest
    info['spine'] = spine
    info['toc']= toc

    # Finally, write the index and toc
    epub.writestr('OEBPS/stylesheet.css', stylesheet_tpl)
    epub.writestr('OEBPS/Content.opf', index_tpl % info)
    epub.writestr('OEBPS/toc.ncx', toc_tpl % info)
