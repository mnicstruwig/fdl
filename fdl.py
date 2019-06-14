
"""A minimal CLI download utility."""
import click
import requests
from tqdm import tqdm
import warnings


def download(url, chunk_size=4096):
    """Download a file from `url` and stream/save it to disk."""
    local_path = url.split('/')[-1]
    try:
        with requests.get(url, stream=True) as r:
            try:
                total_length = int(r.headers.get('content-length'))
            except TypeError:
                warnings.warn('Unable to get file size.\
                Are you sure the URL is correct?',
                              stacklevel=2)
                total_length = 0
            with tqdm(total=total_length,
                      desc=local_path,
                      unit='B',
                      unit_scale=True,
                      unit_divisor=1024) as pbar:
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                            pbar.update(len(chunk))
    except requests.exceptions.MissingSchema:
        print(f'Error! Badly-formed url: {url}')

    pbar.close()
    return local_path


@click.command()
@click.argument('urls', required=False, nargs=-1)
@click.option('--chunk-size', default=4096, help='Set the chunk size in bytes. Default is 4096.')
def download_files(urls, chunk_size):
    """Download a list of URLs to the current directory. FDL also accepts piped
    values - see the examples.

    \b
    Examples:
        python fdl.py url1 url2 url3
        echo 'url-to-download' | python fdl.py
        cat urls.txt | python fdl.py

    """
    if not urls:  # If not manually specified
        # See if the user piped in the urls
        urls = click.get_text_stream('stdin').readlines()
    urls = [url.strip() for url in urls]
    for url in urls:
        download(url, chunk_size)


if __name__ == '__main__':
    download_files()
