package writer

import (
	"encoding/json"
	"os"

	"github.com/shreyashsri79/metadata-analyser/data-pipeline/models"
)

func PushData(ch <-chan float64, done chan<- bool) {
	file, err := os.Create("../raw-data/output.json")
	if err != nil {
		panic(err)
	}
	defer file.Close()

	output := models.Output{
		Timestamps: make([]float64, 0, 128),
	}

	for timestamps := range ch {
		output.Timestamps = append(output.Timestamps, timestamps)
	}

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", " ")

	if err := encoder.Encode(output); err != nil {
		panic(err)
	}
	close(done)
}
