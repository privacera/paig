import uvicorn

host = "127.0.0.1"
port = 4547
workers = 1

def main():
    uvicorn.run(
        app="server:app",
        host=host,
        port=port,
        workers=workers,
    )

if __name__ == "__main__":
    main()