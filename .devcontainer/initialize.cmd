:: Copyright (c) 2023 Eliah Kagan
::
:: Permission to use, copy, modify, and/or distribute this software for any
:: purpose with or without fee is hereby granted.
::
:: THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
:: WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
:: MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
:: SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
:: WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
:: OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
:: CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

@echo off
setlocal enableextensions

:: Use the code page for UTF-8.
chcp 65001 >NUL

set "conf_path=.inherited-configuration"
set "script_name=%~nx0"

goto begin

:msg
    echo/%script_name%: %* >&2
    exit /b

:push_in
    setlocal
    set "name=%1"

    git config -- "%name%" >NUL

    if %ERRORLEVEL% NEQ 0 (
        call :msg skipping: %name%
        exit /b 0
    )

    for /f "usebackq delims=" %%G in (`git config -- "%name%"`) do (
        set "value=%%G"
    )

    call :msg carrying in: %name%=%value%
    echo/%name% %value% >>"%conf_path%"
    exit /b

:begin
    del "%conf_path%" 2>NUL

    :: Usually these are automatically set in the container, but not always.
    call :push_in user.name
    call :push_in user.email
