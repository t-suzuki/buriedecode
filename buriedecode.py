#!env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import subprocess

VERSION = (0, 0, 2)
DATE = (2013, 8, 3)

VERBOSE = False
def _I(s, *av):
    if not VERBOSE:
        return
    if len(av) > 0:
        print >> sys.stderr, ' '.join([s] + list(av))
    else:
        print >> sys.stderr, s

def create_script_engine_processor(tag, cmd, option):
    class ProcessorScriptEngine(object):
        TAG = tag
        def execute(self, script):
            p = subprocess.Popen([cmd, option, script], stdout=subprocess.PIPE)
            stdout, stderr = p.communicate()
            return stdout
    return ProcessorScriptEngine

ProcessorPython = create_script_engine_processor('python', 'python', '-c')
ProcessorRuby = create_script_engine_processor('ruby', 'ruby', '-e')

def create_C_or_CPP_processor(tag, suffix, compiler):
    class ProcessorCorCPP(object):
        TAG = tag
        def execute(self, script):
            import tempfile
            with tempfile.NamedTemporaryFile('wb', suffix=suffix) as tmp:
                tmp.write(script)
                tmp.flush()
                _I('temp file path:', tmp.name)
                with tempfile.NamedTemporaryFile('wb', suffix='.exe') as exe:
                    p = subprocess.Popen([compiler, tmp.name, '-o', exe.name],
                            stdout=subprocess.PIPE)
                    stdout, stderr = p.communicate()
                    if stdout: _I('compiler:', stdout)
                    if stderr: _I('compiler:', stderr)

                    p = subprocess.Popen([exe.name], stdout=subprocess.PIPE)
                    stdout, stderr = p.communicate()

            return stdout
    return ProcessorCorCPP

ProcessorC = create_C_or_CPP_processor('c', '.c', 'gcc')
ProcessorCPP = create_C_or_CPP_processor('cpp', '.cpp', 'g++')

def tag_to_processor(tag):
    try:
        cls = {
                ProcessorPython.TAG: ProcessorPython,
                ProcessorRuby.TAG: ProcessorRuby,
                ProcessorC.TAG: ProcessorC,
                ProcessorCPP.TAG: ProcessorCPP,
                }[tag.strip().lower()]
        return cls()
    except:
        return None

class ProgrammingLanguage(object):
    def _comment_block_re(self): pass
    def _comment_line_re(self): pass
    def _replaced_block_header(self, script_tag): pass
    def _replaced_block_footer(self, script_tag): pass
    def _block_body_to_str(self, block_body): return block_body
    def _line_body_to_str(self, line_body): return line_body
    def process_blocks(self, in_text):
        def rep(is_block):
            def real_rep(mo):
                org_block = mo.group(0)
                gd = mo.groupdict()
                header = gd['head'].rstrip()
                code_block = self._line_body_to_str(gd['body'].rstrip())
                _I('org_block:', org_block)
                _I('header:', header)
                _I('code_block:', code_block)
                processor = tag_to_processor(header)
                if processor is None:
                    return org_block
                result = processor.execute(code_block).rstrip()
                insert_str = '\n'.join([
                        self._replaced_block_header(processor.TAG),
                        result,
                        self._replaced_block_footer(processor.TAG),
                        ])
                # block comments do not have a terminating line break, so insert one.
                if is_block:
                    insert_str = '\n' + insert_str
                maybe_same_str = in_text[mo.end():mo.end()+len(insert_str)]
                _I('insert_str:', '[%s]' % insert_str)
                _I('maybe_same_str:', '[%s]' % maybe_same_str)
                if insert_str == maybe_same_str:
                    _I('no change!')
                    return org_block
                else:
                    _I('inserting!')
                    if is_block:
                        # trailing line break is left to the original text, so append nothing.
                        return org_block + insert_str
                    else:
                        # line comments end with line breaks, so do nothing.
                        return org_block + insert_str + '\n'
            return real_rep

        tmp_text = in_text

        block_re = self._comment_block_re()
        if block_re:
            tmp_text = block_re.sub(rep(True), tmp_text)

        line_re = self._comment_line_re()
        if line_re:
            tmp_text = line_re.sub(rep(False), tmp_text)

        return tmp_text

class LanguageC(ProgrammingLanguage):
    def _comment_block_re(self):
        return re.compile(ur'/\*\?(?P<head>([^/]|[^*]/)*?\n)(?P<body>.*?)\*/', re.S)
    def _comment_line_re(self):
        return None
    def _replaced_block_header(self, script_tag):
        return '/*?%s:replaced:begin*/' % script_tag
    def _replaced_block_footer(self, script_tag):
        return '/*?%s:replaced:end*/' % script_tag

class LanguageCPP(LanguageC):
    def _comment_line_re(self):
        return re.compile(ur'//\?(?P<head>.*?\n)(?P<body>(//(?!\?).*?\n)+)')
    def _line_body_to_str(self, line_body):
        return re.compile(ur'^//(.*?)$', re.M).sub(ur'\1', line_body)
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
                'cpp': LanguageCPP,
                'hpp': LanguageCPP,
                'c': LanguageC,
                'h': LanguageCPP, # we do not know whether it is C or C++.
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

def readme_str():
    import datetime
    versionstr = '%d.%d.%d' % VERSION
    datestr = datetime.datetime(*DATE).strftime('%Y/%m/%d')
    return '''buriedecode
===========
  expanding buried script in another language\'s source code in-place.

  - version: %s
  - date: %s
  - Takahiro SUZUKI <takahiro.suzuki.ja@gmail.com>
  - https://github.com/t-suzuki/buriedecode

usage:
------
    $ python buriedecode.py [files]

supported script(buried, embeded) languages:
--------------------------------------------
  - Python (python)
  - Ruby (ruby)
  - C (gcc)
  - C++ (g++)

supported host languages:
-------------------------
  - C/C++ (.c, .cpp, .h, .hpp)

burying example: burying Python in C/C++
----------------------------------------
    /*?python
    for i in range(3):
        print "#define NEXT_TO_%%d (%%d+1)" %% (i, i)
    */
''' % (versionstr, datestr)

def main():
    if len(sys.argv) < 2:
        print readme_str()
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

