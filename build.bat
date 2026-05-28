@echo off
chcp 65001 >nul 2>&1
echo ============================================
echo   Gacha Simulator - Build Script
echo ============================================
echo.

REM Check if PyInstaller is installed
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [Info] Installing PyInstaller...
    pip install pyinstaller
)

echo [Step 1/4] Cleaning old build files...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"

echo [Step 2/4] Building executable (onefile mode)...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --noconfirm ^
    --clean ^
    --name="GachaSimulator" ^
    --distpath=dist ^
    --workpath=build ^
    main.py

if errorlevel 1 (
    echo.
    echo [Error] Build failed! Check error messages above.
    pause
    exit /b 1
)

echo.
echo [Step 3/4] Checking output file...
if not exist "dist\GachaSimulator.exe" (
    echo [Error] Output file not found!
    pause
    exit /b 1
)

echo.
echo [Step 4/4] Build completed successfully!
echo.
echo Output: dist\GachaSimulator.exe
for %%A in ("dist\GachaSimulator.exe") do echo Size: %%~zA bytes
echo.
echo You can distribute this exe file without Python installed.
echo.
pause
