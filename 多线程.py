import os
import sys
import threading
import requests

def download_chunk(url, start, end, chunk_num, filename):
    headers = {'Range': f'bytes={start}-{end}'}
    response = requests.get(url, headers=headers, stream=True)
    chunk_filename = f"{filename}.part{chunk_num}"
    with open(chunk_filename, 'wb') as f:
        f.write(response.content)

def merge_chunks(filename, num_chunks):
    with open(filename, 'wb') as outfile:
        for i in range(num_chunks):
            chunk_filename = f"{filename}.part{i}"
            with open(chunk_filename, 'rb') as infile:
                outfile.write(infile.read())
            os.remove(chunk_filename)

def multi_threaded_download(url, filename, num_threads=4):
    response = requests.head(url)
    file_size = int(response.headers['Content-Length'])
    chunk_size = file_size // num_threads
    threads = []

    for i in range(num_threads):
        start = i * chunk_size
        end = start + chunk_size - 1 if i < num_threads - 1 else file_size - 1
        thread = threading.Thread(target=download_chunk, args=(url, start, end, i, filename))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    merge_chunks(filename, num_threads)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python downloader.py <URL> <FILENAME>")
        sys.exit(1)

    url = sys.argv[1]
    filename = sys.argv[2]

    multi_threaded_download(url, filename)
