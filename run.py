import uvicorn

from app.config import settings


def main():
    print(f"using workers: {settings.workers}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        loop="uvloop",
        http="httptools",
        reload=False,
        access_log=True,
    )


if __name__ == "__main__":
    main()
