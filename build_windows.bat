@echo off
setlocal
cd /d "%~dp0"
title Building Slide Remote

echo.
echo  Building Slide Remote...
echo.

where python >nul 2>nul || (
  echo  Python was not found. Install it from https://www.python.org/downloads/
  echo  and tick "Add python.exe to PATH" during setup. Then run this file again.
  goto :fail
)

echo  [1/4] Installing packages
python -m venv .venv || goto :fail
set "PY=%CD%\.venv\Scripts\python.exe"
"%PY%" -m pip install --quiet -r requirements-build.txt || goto :fail

echo  [2/4] Creating the app icon
"%PY%" SlideRemote.pyw --make-icon || goto :fail

echo  [3/4] Building Slide Remote.exe (takes about a minute)
"%PY%" -m PyInstaller --noconfirm --clean --onefile --windowed --name "Slide Remote" --specpath build --icon "%CD%\icon.ico" SlideRemote.pyw >build.log 2>&1 || (
  echo  Build failed. See build.log for details.
  goto :fail
)

echo  [4/4] Adding shortcuts to your Desktop and Start menu
set "SLIDE_REMOTE_DIST=%CD%\dist"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$exe = Join-Path $env:SLIDE_REMOTE_DIST 'Slide Remote.exe';" ^
  "$w = New-Object -ComObject WScript.Shell;" ^
  "foreach ($dir in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {" ^
  "  $s = $w.CreateShortcut((Join-Path $dir 'Slide Remote.lnk')); $s.TargetPath = $exe; $s.IconLocation = $exe; $s.WorkingDirectory = (Split-Path $exe); $s.Save() }"

echo.
echo  Done. Open "Slide Remote" from your Desktop or Start menu.
echo  The first time, Windows asks about network access: choose "Private networks" and Allow.
echo.
pause
exit /b 0

:fail
echo.
pause
exit /b 1
