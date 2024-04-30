import pathlib
import os
import logging
import time
from multiprocessing import Process, Queue, Event
from sys import exit

message_format = "%(processName)s %(asctime)s: %(message)s"
logging.basicConfig(format=message_format, level=logging.INFO, datefmt="%H:%M:%S")


class Writer:
    def __init__(self,  keywords, e: Event):
        self.keywords = keywords
        self.files_for_handling = Queue()
        self.event = e
        self.result = {keyword: [] for keyword in keywords}
        self.queue = Queue()

    def __call__(self, *args, **kwargs):
        while True:
            if self.files_for_handling.empty():
                if self.event.is_set():
                    self.queue.put(self.result)
                    exit(0)
            else:
                keyword, path = self.files_for_handling.get()
                self.result[keyword].append(path)


def reader(files_for_reading: Queue, files_for_handling: Queue, keywords):
    while True:
        if files_for_reading.empty():
            break
        file: pathlib.Path = files_for_reading.get()
        logging.info(f"read file {file.name}")
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                for keyword in keywords:
                    if keyword in content:
                        files_for_handling.put((keyword, str(file)))
        except Exception as e:
            logging.error(f"Error reading {file}: {e}")


if __name__ == "__main__":
    start_time = time.time()

    keywords = ["appendChild", "Promise"]

    files_for_reading = Queue()
    event = Event()

    list_files = pathlib.Path(".").joinpath("files").glob("*.txt")
    [files_for_reading.put(file) for file in list_files]

    if files_for_reading.empty():
        logging.info("Folder is empty")
    else:
        writer = Writer(keywords, event)
        th_writer = Process(target=writer, name="Writer")
        th_writer.start()

        threads = []
        for i in range(2):
            tr = Process(
                target=reader, args=(files_for_reading, writer.files_for_handling, keywords), name=f"Reader#{i}"
            )
            tr.start()
            threads.append(tr)

        [th.join() for th in threads]
        event.set()

        result = writer.queue.get()
        end_time = time.time() - start_time
        print(result)
        print(f'Time elapsed: {end_time}')
