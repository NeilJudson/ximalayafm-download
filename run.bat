python ximalayafm-analyze.py http://www.ximalaya.com/28757246/album/2842242?feed=reset
for /f "tokens=1,2 delims=|" %%i in (download-list.txt) do aria2c.exe -s 10 -j 10 %%j --out=%%i
del download-list.txt