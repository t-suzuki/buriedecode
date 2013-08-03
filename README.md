buriedecode
===========
  expanding buried script in another language's source code in-place.

  - version: 0.0.2
  - date: 2013/08/03
  - Takahiro SUZUKI <takahiro.suzuki.ja@gmail.com>
  - https://github.com/t-suzuki/buriedecode

usage:
------
    $ buriedecode [files]

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
        print "#define NEXT_TO_%d (%d+1)" % (i, i)' )
    */

