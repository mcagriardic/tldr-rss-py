import uvicorn


def main() -> None:
    uvicorn.run("src.server:app", host="0.0.0.0", port=8800, reload=True)


if __name__ == "__main__":
    main()
