!bin/zsh

cd data-pipeline
go run ./cmd
cd ..
cd data-processor
py analyser.py
cd ..