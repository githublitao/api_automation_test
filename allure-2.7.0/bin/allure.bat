@if "%DEBUG%" == "" @echo off
@rem ##########################################################################
@rem
@rem  allure startup script for Windows
@rem
@rem ##########################################################################

@rem Set local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" setlocal

set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.
set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%..

@rem Add default JVM options here. You can also use JAVA_OPTS and ALLURE_OPTS to pass JVM options to this script.
set DEFAULT_JVM_OPTS=

@rem Find java.exe
if defined JAVA_HOME goto findJavaFromJavaHome

set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if "%ERRORLEVEL%" == "0" goto init

echo.
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:findJavaFromJavaHome
set JAVA_HOME=%JAVA_HOME:"=%
set JAVA_EXE=%JAVA_HOME%/bin/java.exe

if exist "%JAVA_EXE%" goto init

echo.
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME%
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:init
@rem Get command-line arguments, handling Windows variants

if not "%OS%" == "Windows_NT" goto win9xME_args

:win9xME_args
@rem Slurp the command line arguments.
set CMD_LINE_ARGS=
set _SKIP=2

:win9xME_args_slurp
if "x%~1" == "x" goto execute

set CMD_LINE_ARGS=%*

:execute
@rem Setup the command line

set CLASSPATH=%APP_HOME%\lib\allure-commandline-2.7.0.jar;%APP_HOME%\lib\allure-generator-2.7.0.jar;%APP_HOME%\lib\jcommander-1.72.jar;%APP_HOME%\lib\jetty-server-9.4.11.v20180605.jar;%APP_HOME%\lib\slf4j-log4j12-1.7.25.jar;%APP_HOME%\lib\jackson-dataformat-xml-2.9.6.jar;%APP_HOME%\lib\allure-plugin-api-2.7.0.jar;%APP_HOME%\lib\jackson-dataformat-yaml-2.9.6.jar;%APP_HOME%\lib\commons-io-2.6.jar;%APP_HOME%\lib\allure2-model-api-1.0.0.jar;%APP_HOME%\lib\allure1-model-1.0.jar;%APP_HOME%\lib\httpclient-4.5.6.jar;%APP_HOME%\lib\allure2-model-jackson-1.0.0.jar;%APP_HOME%\lib\allure2-model-pojo-1.0.0.jar;%APP_HOME%\lib\tika-core-1.18.jar;%APP_HOME%\lib\javax.servlet-api-3.1.0.jar;%APP_HOME%\lib\jetty-http-9.4.11.v20180605.jar;%APP_HOME%\lib\jetty-io-9.4.11.v20180605.jar;%APP_HOME%\lib\slf4j-api-1.7.25.jar;%APP_HOME%\lib\log4j-1.2.17.jar;%APP_HOME%\lib\jackson-module-jaxb-annotations-2.9.6.jar;%APP_HOME%\lib\jackson-databind-2.9.6.jar;%APP_HOME%\lib\jackson-core-2.9.6.jar;%APP_HOME%\lib\jackson-annotations-2.9.0.jar;%APP_HOME%\lib\woodstox-core-5.0.3.jar;%APP_HOME%\lib\stax2-api-3.1.4.jar;%APP_HOME%\lib\opencsv-4.2.jar;%APP_HOME%\lib\flexmark-0.34.8.jar;%APP_HOME%\lib\jaxb-api-2.3.0.jar;%APP_HOME%\lib\freemarker-2.3.28.jar;%APP_HOME%\lib\snakeyaml-1.18.jar;%APP_HOME%\lib\properties-2.0.RC5.jar;%APP_HOME%\lib\jaxb-utils-1.0.jar;%APP_HOME%\lib\httpcore-4.4.10.jar;%APP_HOME%\lib\commons-beanutils-1.9.3.jar;%APP_HOME%\lib\commons-logging-1.2.jar;%APP_HOME%\lib\commons-codec-1.10.jar;%APP_HOME%\lib\jetty-util-9.4.11.v20180605.jar;%APP_HOME%\lib\commons-text-1.4.jar;%APP_HOME%\lib\commons-lang3-3.7.jar;%APP_HOME%\lib\commons-collections4-4.1.jar;%APP_HOME%\lib\flexmark-util-0.34.8.jar;%APP_HOME%\lib\commons-collections-3.2.2.jar;%APP_HOME%\lib\config

@rem Execute allure
"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %ALLURE_OPTS%  -classpath "%CLASSPATH%" io.qameta.allure.CommandLine %CMD_LINE_ARGS%

:end
@rem End local scope for the variables with windows NT shell
if "%ERRORLEVEL%"=="0" goto mainEnd

:fail
rem Set variable ALLURE_EXIT_CONSOLE if you need the _script_ return code instead of
rem the _cmd.exe /c_ return code!
if  not "" == "%ALLURE_EXIT_CONSOLE%" exit 1
exit /b 1

:mainEnd
if "%OS%"=="Windows_NT" endlocal

:omega
