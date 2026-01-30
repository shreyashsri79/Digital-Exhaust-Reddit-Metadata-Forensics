package main

import (
	"fmt"
	"os"
	"sync"

	"github.com/joho/godotenv"
	"github.com/shreyashsri79/metadata-analyser/data-pipeline/internal/reddit"
	"github.com/shreyashsri79/metadata-analyser/data-pipeline/internal/writer"
)

const BASE_URL = "https://www.reddit.com/user/"

func main() {

	if err := godotenv.Load(); err != nil {
		panic(err)
	}

	fmt.Println("hi mom")
	user := os.Getenv("user")
	ch := make(chan float64, 100)
	done := make(chan bool)
	var wg sync.WaitGroup

	endpoints := []string{
		"/submitted.json",
		"/comments.json",
	}
	go writer.PushData(ch, done)

	wg.Add(len(endpoints))

	for _, endpoint := range endpoints {
		go reddit.RetriveData(ch, user, endpoint, &wg, BASE_URL)
	}

	go func() {
		wg.Wait()
		close(ch)
	}()

	wg.Wait()
	<-done

}
