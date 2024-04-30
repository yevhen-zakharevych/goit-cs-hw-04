import pathlib
import os
import time
from queue import Queue
from threading import Thread, Event
import logging


class Writer:
    def __init__(self, keywords, e: Event):
        self.keywords = keywords
        self.files_for_handling = Queue()
        self.result = {keyword: [] for keyword in keywords}
        self.event = e

    def __call__(self, *args, **kwargs):
        while True:
            if self.files_for_handling.empty():
                if self.event.is_set():
                    break
            else:
                keyword, path = self.files_for_handling.get()
                self.result[keyword].append(path)

        return self.result


def reader(files_for_reading: Queue, keywords, files_for_handling: Queue):
    while True:
        if files_for_reading.empty():
            break
        file = files_for_reading.get()
        logging.info(f"Reading file {file.name}")
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
            for keyword in keywords:
                if keyword in content:
                    files_for_handling.put((keyword, str(file)))
        except Exception as e:
            logging.error(f"Error reading {file}: {e}")


if __name__ == "__main__":
    message_format = "%(threadName)s %(asctime)s: %(message)s"
    logging.basicConfig(format=message_format, level=logging.INFO, datefmt="%H:%M:%S")

    start_time = time.time()
    files_for_reading = Queue()
    event = Event()

    keywords = ['appendChild', 'Promise']
    list_files = pathlib.Path(".").joinpath("files").glob("*.txt")
    [files_for_reading.put(file) for file in list_files]

    if files_for_reading.empty():
        logging.info("Folder is empty")
    else:
        writer = Writer(keywords, event)
        th_writer = Thread(target=writer, name="Writer")
        th_writer.start()

        threads = []
        for i in range(2):
            tr = Thread(
                target=reader, args=(files_for_reading, keywords, writer.files_for_handling), name=f"Reader#{i}"
            )
            tr.start()
            threads.append(tr)

        [th.join() for th in threads]
        event.set()

        end_time = time.time() - start_time

        print(writer.result)
        print(f"Time elapsed: {end_time}")
