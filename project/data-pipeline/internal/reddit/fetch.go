package reddit

import (
	"encoding/json"
	"io"
	"net/http"
	"sync"

	"github.com/shreyashsri79/metadata-analyser/data-pipeline/models"
)

func RetriveData(ch chan<- float64, user string, endpoint string, wg *sync.WaitGroup, BASE_URL string) {
	defer wg.Done()
	res, err := http.Get(BASE_URL + user + endpoint)
	if err != nil {
		panic(err)
	}
	defer res.Body.Close()

	var redditData models.RedditResponse
	body, _ := io.ReadAll(res.Body)
	if err := json.Unmarshal(body, &redditData); err != nil {
		panic(err)
	}

	for _, child := range redditData.Data.Children {
		ch <- child.Data.CreatedUTC
	}
}
