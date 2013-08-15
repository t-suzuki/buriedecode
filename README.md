buriedecode
===========
  expanding buried script in another language's source code in-place.

  - version: 0.0.3
  - date: 2013/08/15
  - Takahiro SUZUKI <takahiro.suzuki.ja@gmail.com>
  - https://github.com/t-suzuki/buriedecode

usage:
------
    $ python buriedecode.py [files]

supported script(buried, embeded) languages:
--------------------------------------------
  - Python (python)
  - Ruby (ruby)
  - Haskell (ghc)
  - C (gcc)
  - C++ (g++)

supported host languages:
-------------------------
  - C/C++ (.c, .cpp, .h, .hpp)

burying example: Python in C
----------------------------------------
    /*?python
    for i in range(3):
        print "#define NEXT_TO_%d (%d+1)" % (i, i)
    */
    /*?python:replaced:begin*/
    #define NEXT_TO_0 (0+1)
    #define NEXT_TO_1 (1+1)
    #define NEXT_TO_2 (2+1)
    /*?python:replaced:end*/

burying example: Haskell in C++
----------------------------------------
    int arr[] = {
    /*?haskell
    join s [] = ""
    join s (x:[]) = x
    join s (x:xs) = x ++ s ++ (join s xs)
    main = putStrLn $ join ", " $ take 10 $ map show $ iterate (*2) 1
    */
    //?haskell:replaced:begin
    1, 2, 4, 8, 16, 32, 64, 128, 256, 512
    //?haskell:replaced:end
    };

