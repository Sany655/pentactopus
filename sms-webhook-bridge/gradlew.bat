@rem SMS Webhook Bridge Gradle Launcher
@if "%DEBUG%"=="" @echo off
@setlocal

set DIRNAME=%~dp0
if "%DIRNAME%"=="" set DIRNAME=.

set GRADLE_EXEC=C:\Users\Sany\.gradle\wrapper\dists\gradle-8.14.3-all\10utluxaxniiv4wxiphsi49nj\gradle-8.14.3\bin\gradle.bat

if exist "%GRADLE_EXEC%" (
    call "%GRADLE_EXEC%" %*
) else (
    gradle %*
)
