@echo off
setlocal ENABLEEXTENSIONS

rem Generates a new SECRET_KEY, writes it to backend/.env.local, and prints it.
rem Uses PowerShell to create a 32-byte random value, Base64 URL-safe.

set TARGET_ENV=backend\.env.local

for /f "usebackq tokens=*" %%i in (`powershell -Command "$raw=[System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32); $b64=[Convert]::ToBase64String($raw); $safe=$b64.Replace('+','-').Replace('/','_'); echo $safe"`) do set NEW_KEY=%%i

if not defined NEW_KEY (
  echo Failed to generate SECRET_KEY.
  exit /b 1
)

echo SECRET_KEY=%NEW_KEY%> %TARGET_ENV%
echo Generated SECRET_KEY and wrote to %TARGET_ENV%
echo Value: %NEW_KEY%

endlocal
