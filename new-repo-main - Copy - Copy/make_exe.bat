pyinstaller --noconfirm ^
    --onefile ^
    --noconsole ^
    --name "Source Meter UI" ^
    --add-data="logos\logo.png;logos" ^
    --add-data="logos\logo.ico;logos" ^
    --icon "logos\logo.ico" ^
    --splash "logos\splash.png" ^
    main.py
