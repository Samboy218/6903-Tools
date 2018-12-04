This keylogger works on any Windows machine and cannot be detected by any anti-virus software (e.g., Windows Defender).

Rename the file 'Keylogger' to 'Keylogger.exe' or something else. Make sure that the extension (*.exe) is there.
Run the executable.
Your keylogger should be running now as a background process.
Type anything on your keyboard.
A file named 'mylog.txt' should be created in the same directory as the executable.
To close the keylogger, open the task manager.
In the process list, find the process named 'Keylogger.exe' and kill it.
Make sure that no other keystrokes are logged into the log file.

Compilation:
I compiled this cpp file in Visual Studio by including it as a source file into a C++ project. You can change a project setting (Runtime Library) if you want to have the required DLLs complied into the executable. These DLLs are required to run most executables that need a Windows specific c++ package.

You can access this setting from Project Proprties > C/C++ > Code Generation > Runtime Library. You need to set this value to 'Multi-threaded DLL (/MD)' or 'Multi-threded Debug DLL (/MDd)'. Now build the project and you should have the executable with the required DLLs.
