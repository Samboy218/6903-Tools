all: windows linux

windows:
	GOOS=windows GOARCH=386 go build -o release/gotrash.exe gotrash.go
	cp release/gotrash.exe ../c2trash/static/
linux:
	GOOS=linux GOARCH=386 go build -o release/gotrash gotrash.go
	cp release/gotrash ../c2trash/static/
