#!env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import subprocess

VERSION = [0, 0, 1]
DATE = [2013, 8, 3]

VERBOSE = False
def _I(s, *av):
    if not VERBOSE:
        return
    if len(av) > 0:
        print >> sys.stderr, ' '.join([s] + av)
    else:
        print >> sys.stderr, s

class ProcessorPython(object):
    TAG = 'python'
    def execute(self, script):
        p = subprocess.Popen(['python', '-c', script], stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return stdout

class ProcessorRuby(object):
    TAG = 'ruby'
    def execute(self, script):
        p = subprocess.Popen(['ruby', '-e', script], stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return stdout

def tag_to_processor(tag):
    try:
        cls = {
                ProcessorPython.TAG: ProcessorPython,
                ProcessorRuby.TAG: ProcessorRuby,
                }[tag.strip().lower()]
        return cls()
    except:
        return None

class ProgrammingLanguage(object):
    def _comment_block_re(self): pass
    def _comment_line_re(self): pass
    def _replaced_block_header(self, script_tag): pass
    def _replaced_block_footer(self, script_tag): pass
    def process_blocks(self, in_text):
        def rep(mo):
            org_block = mo.group(0)
            gd = mo.groupdict()
            header = gd['head'].rstrip()
            code_block = gd['body'].rstrip()
            _I('org_block:', org_block)
            _I('header:', header)
            _I('code_block:', code_block)
            processor = tag_to_processor(header)
            result = processor.execute(code_block).rstrip()
            insert_str = '\n'.join([
                    self._replaced_block_header(processor.TAG),
                    result,
                    self._replaced_block_footer(processor.TAG),
                    ])
            maybe_same_str = in_text[mo.end()+1:mo.end()+1+len(insert_str)]
            _I('insert_str:', insert_str)
            _I('maybe_same_str:', maybe_same_str)
            if insert_str == maybe_same_str:
                _I('no change!')
                return org_block
            else:
                _I('inserting!')
                return '\n'.join([
                    org_block,
                    insert_str
                    ])

        out_text = self._comment_block_re().sub(rep, in_text)
        return out_text

class LanguageCAndCPP(ProgrammingLanguage):
    def _comment_block_re(self):
        return re.compile(ur'/\*\?(?P<head>.*?\n)(?P<body>.*?)\*/', re.S)
    def _comment_line_re(self):
        return re.compile(ur'//\?(?P<head>.*?\n$)(//(?P<body>.*?$))*', re.M | re.S)
    def _replaced_block_header(self, script_tag):
        return '//?%s:replaced:begin' % script_tag
    def _replaced_block_footer(self, script_tag):
        return '//?%s:replaced:end' % script_tag

def process(in_text, in_language):
    out_text = in_language.process_blocks(in_text)
    return out_text

def extension_to_language(ext):
    if ext.startswith('.'):
        ext = ext[1:]
    try:
        cls = {
                'cpp': LanguageCAndCPP,
                'c': LanguageCAndCPP,
                }[ext.lower()]
        return cls()
    except:
        return None

def process_file(in_file_path, out_file_path):
    ext = extension_to_language(os.path.splitext(in_file_path)[1])
    with open(in_file_path, 'rb') as fi:
        in_text = fi.read()

    out_text = process(in_text, ext)
    if in_text != out_text:
        with open(out_file_path, 'wb') as fo:
            fo.write(out_text)
        return True
    return False

def help():
    import datetime
    print 'buriedecode - v%d.%d.%d (%s)' % tuple(VERSION + [datetime.datetime(*DATE).strftime('%Y/%m/%d')])
    print '  expanding buried script in another language\'s source code in-place.'
    print '  Takahiro SUZUKI <takahiro.suzuki.ja@gmail.com>'
    print
    print 'usage:'
    print '  $ buriedecode [files]'
    print
    print 'supported script languages:'
    print '  - Python'
    print '  - Ruby'
    print
    print 'burying example: burying Python in C/C++'
    print '  /*?python'
    print '  for i in range(3):'
    print '    print "#define NEXT_TO_%d (%d+1)" % (i, i)' 
    print '  */'

def main():
    if len(sys.argv) < 2:
        help()
        sys.exit(1)

    count = {True: 0, False: 0}
    for fi in sys.argv[1:]:
        changed = process_file(fi, fi)
        count[changed] += 1
        if changed:
            print 'Updated "%s".' % fi
        else:
            print '.'

    print '-'*80
    print 'Total number of changed files: %d' % count[True]
    print 'Total number of unchanged files: %d' % count[False]

if __name__=='__main__':
    main()

