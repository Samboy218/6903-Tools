// Compile: g++ -o mian.exe .\main.cpp -mwindows -lgdi32
#include <Windows.h>
#include <iostream>
using namespace std;

HWND hWndMain;
HINSTANCE hInst;

LRESULT CALLBACK LowLevelKeyboardProc(int nCode, WPARAM wParam, LPARAM lParam);
BOOL SetPrivilege(HANDLE hToken, LPCTSTR lpszPrivilege, BOOL bEnablePrivilege);
LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam);

// Main window callback procedure
LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam) {
    //PAINTSTRUCT ps;
    //HDC hdc;
    
    switch(message) {
        case WM_PAINT:
            //hdc = BeginPaint(hWnd, &ps);
            //TextOut(hdc, 5, 5, "Hello there!", 12);
            //EndPaint(hWnd, &ps);
            break;

        case WM_DESTROY:
            PostQuitMessage(0);
            break;

        default:
            return DefWindowProc(hWnd, message, wParam, lParam);
            break;
    }

    return 0;
}

// Set process privileges
BOOL SetPrivilege(HANDLE hToken, LPCTSTR lpszPrivilege, BOOL bEnablePrivilege) {
    TOKEN_PRIVILEGES tp;
    LUID luid;

    if(!LookupPrivilegeValue(NULL, lpszPrivilege, &luid))
        return FALSE; 

    tp.PrivilegeCount = 1;
    tp.Privileges[0].Luid = luid;
    if(bEnablePrivilege)
        tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
    else
        tp.Privileges[0].Attributes = 0;


    if(!AdjustTokenPrivileges(hToken, FALSE, &tp, sizeof(TOKEN_PRIVILEGES), (PTOKEN_PRIVILEGES) NULL, (PDWORD)NULL))
        return FALSE; 

    if (GetLastError() == ERROR_NOT_ALL_ASSIGNED)
          return FALSE;

    return TRUE;
}

// Keyboard hook, does nothing when key is pressed
LRESULT CALLBACK LowLevelKeyboardProc(int nCode, WPARAM wParam, LPARAM lParam)
{
    if (nCode >= 0) {
        switch (wParam) {
            case WM_KEYDOWN:
            case WM_SYSKEYDOWN:
            case WM_KEYUP:
            case WM_SYSKEYUP:
                break;
        }
    }

    // Cancel key press
    return 1;//CallNextHookEx(NULL, nCode, wParam, lParam);
}

// Enumerates through all opened windows and kills them
BOOL EnumWindowsProc(HWND hwnd, LPARAM lParam) {
	char    cl[512];		// For keeping track of window titles
	char    st[512];		// For keeping track of window styles
	DWORD	dwPID;			// For keeping of PIDs

	GetWindowThreadProcessId(hwnd, &dwPID);	// Get process PID
	RealGetWindowClass(hwnd, cl, 512);		// Get window title
	GetWindowText(hwnd, st, 512);			// Get window style

    // If window is a parent and it's not out process - kill it
	if((GetParent(hwnd) == 0) && (dwPID != (DWORD)lParam) && (hwnd != hWndMain)) {
        // Fire everything we got
		ShowWindow(hwnd, SW_HIDE);
		PostMessage(hwnd, WM_QUIT, SC_MINIMIZE, 0);
		PostMessage(hwnd, WM_CLOSE, SC_MINIMIZE, 0);
		PostMessage(hwnd, WM_DESTROY, SC_MINIMIZE, 0);
		SendMessage(hwnd, WM_ENDSESSION, 1, 0);
	}

    return true;
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    // Kill all open windows (idealy we want to do it in a thread)
    EnumWindows((WNDENUMPROC)EnumWindowsProc, (LPARAM)GetCurrentProcessId());
    // Block keyborad
    HHOOK hhkLowLevelKybd = SetWindowsHookEx(WH_KEYBOARD_LL, LowLevelKeyboardProc, 0, 0);
    //TODO: restrict mouse movement
    //...
    
    // Create a GUI just for fun
    WNDCLASSEX wcex;
    wcex.cbSize         = sizeof(WNDCLASSEX);
    wcex.style          = CS_HREDRAW | CS_VREDRAW;
    wcex.lpfnWndProc    = WndProc;
    wcex.cbClsExtra     = 0;
    wcex.cbWndExtra     = 0;
    wcex.hInstance      = hInstance;
    wcex.hIcon          = NULL;
    wcex.hCursor        = NULL;
    wcex.hbrBackground  = (HBRUSH)(COLOR_WINDOW+2);
    wcex.lpszMenuName   = NULL;
    wcex.lpszClassName  = "TestWindowClass";
    wcex.hIconSm        = NULL;

    if(!RegisterClassEx(&wcex))  {  
        MessageBox(NULL, "Call to RegisterClassEx failed!", "Win32 Guided Tour", MB_OK);
        return 1;
    }

    hInst = hInstance;

    // Create main window
    hWndMain = CreateWindow("TestWindowClass", "My window title", WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, 500, 500, NULL, NULL, hInstance, NULL);
    if(!hWndMain) {  
        MessageBox(NULL, "Call to CreateWindow failed!", "Win32 Guided Tour", MB_OK);
        return 1;
    }

    // Create a text box
    HWND hEdit = CreateWindow("edit", "", WS_CHILD | WS_VISIBLE | WS_TABSTOP, 5, 5, 475, 18, hWndMain, NULL, hInstance, NULL);
    if(!hEdit) {
        MessageBox(NULL, "Call to CreateWindowEX failed while creating edit box!", "Win32 Guided Tour", MB_OK);
        return 1;
    }

    ShowWindow(hWndMain, nCmdShow);
    UpdateWindow(hWndMain);

    MSG msg;
    while(GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    // Unhook all keys
    UnhookWindowsHookEx(hhkLowLevelKybd);

    return (int)msg.wParam;
}