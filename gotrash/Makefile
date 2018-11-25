dropper = godropper
client = gotrash

all: windows linux

windows: windows-dropper windows-client
linux: linux-dropper linux-client

windows-dropper: $(dropper).go
	GOOS=windows GOARCH=386 go build -o release/$(dropper).exe $(dropper).go
	cp release/$(dropper).exe ../c2trash/static/

windows-client: $(client).go
	GOOS=windows GOARCH=386 go build -o release/$(client).exe $(client).go
	cp release/$(client).exe ../c2trash/static/

linux-client: $(client).go
	GOOS=linux GOARCH=386 go build -o release/$(client) $(client).go
	cp release/$(client) ../c2trash/static/

linux-dropper: $(dropper).go
	GOOS=linux GOARCH=386 go build -o release/$(dropper) $(dropper).go
	cp release/$(client) ../c2trash/static/

setup:
	apt install golang -y
	go get crypto/tls
