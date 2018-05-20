py -2 ximalayafm-analyze.py %1
for /f "tokens=1,2 delims=|" %%i in (download-list.txt) do aria2c.exe -s 10 -j 10 %%j --out=%%i
del download-list.txt