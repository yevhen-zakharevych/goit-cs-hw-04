import pathlib
import os
import time
from queue import Queue
from threading import Thread, Event
import logging


class Writer:
    def __init__(self, keyword: str, e: Event):
        self.keyword = keyword
        self.files_for_handling = Queue()
        self.result = {self.keyword: []}
        self.event = e

    def __call__(self, *args, **kwargs):
        while True:
            if self.files_for_handling.empty():
                if self.event.is_set():
                    break
            else:
                path = self.files_for_handling.get()
                self.result[self.keyword].append(path)

        return self.result


def reader(files_for_handling: Queue):
    while True:
        if files_for_reading.empty():
            break
        file: pathlib.Path = files_for_reading.get()
        logging.info(f"read file {file.name}")
        with open(file, "r", encoding="utf-8") as f:
            if keyword in f.read():
                files_for_handling.put(os.path.dirname(file) + "/" + os.path.basename(file))


if __name__ == "__main__":
    message_format = "%(threadName)s %(asctime)s: %(message)s"
    logging.basicConfig(format=message_format, level=logging.INFO, datefmt="%H:%M:%S")

    start_time = time.time()
    files_for_reading = Queue()
    event = Event()

    list_files = pathlib.Path(".").joinpath("files").glob("*.txt")
    keyword = 'appendChild'

    [files_for_reading.put(file) for file in list_files]

    if files_for_reading.empty():
        logging.info("Folder is empty")
    else:
        writer = Writer(keyword, event)
        th_writer = Thread(target=writer, name="Writer")
        th_writer.start()

        threads = []
        for i in range(2):
            tr = Thread(
                target=reader, args=(writer.files_for_handling,), name=f"Reader#{i}"
            )
            tr.start()
            threads.append(tr)

        [th.join() for th in threads]
        event.set()  # файлів для зчитування немає

        end_time = time.time() - start_time

        print(writer.result)
        print(f"time: {end_time}")
