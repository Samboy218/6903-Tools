This is a tool to take a screenshot of the desktop of a Windows machine.

Rename the file ScreenCap to ScreenCap.exe.
Run the file.
The program takes one screenshot (We can easily change it to run for some time and capture screenshots time to time).
Make sure that there is a file named 'testScreenCap.jpg'.
Make sure that the file has the screenshot of your entire desktop.

Compilation:
I compiled this cpp file in Visual Studio by including it as a source file into a C++ project. You can change a project setting (Runtime Library) if you want to have the required DLLs complied into the executable. These DLLs are required to run most executables that need a Windows specific c++ package.

You can access this setting from Project Proprties > C/C++ > Code Generation > Runtime Library. You need to set this value to 'Multi-threaded DLL (/MD)' or 'Multi-threded Debug DLL (/MDd)'. Now build the project and you should have the executable with the required DLLs.

Also, you can easily modify the code to take the screenshots periodically.
