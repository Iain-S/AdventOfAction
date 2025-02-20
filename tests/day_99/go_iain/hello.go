package main

import (
    "bytes"
    "fmt"
    "os"
)

func main() {
    data, err := os.ReadFile("input.txt")
    if err != nil {
        panic(err)
    }
	lines := bytes.Split(data, []byte("\n"))

	for i, line := range lines {
		lines[i] = bytes.ToLower(line)
	}

    if len(os.Args) > 1 {
      if os.Args[len(os.Args)-1] == "one" {
        fmt.Println(string(lines[0]))
        return
      } else if os.Args[len(os.Args)-1] == "two" {
        fmt.Println(string(lines[1]))
        return
      }
  }
  panic("Invalid argument")
}
