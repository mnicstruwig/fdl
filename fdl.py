"""A minimal CLI download utility."""
import click
import requests
from tqdm import tqdm
import warnings


def download(url):
    """Download a file from `url` and stream/save it to disk."""
    local_path = url.split('/')[-1]
    try:
        with requests.get(url, stream=True) as r:
            try:
                total_length = int(r.headers.get('content-length'))
            except TypeError:
                warnings.warn(('Unable to get file size. Are you sure the URL
                               is correct?'),
                              stacklevel=2)
                total_length = 0
            with tqdm(total=total_length,
                      unit='B',
                      unit_scale=True,
                      unit_divisor=1024) as pbar:
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=4*1024):
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
def download_files(urls):
    if not urls:  # If not manually specified
        # See if the user piped in the urls
        urls = click.get_text_stream('stdin').readlines()
    urls = [url.strip() for url in urls]
    for url in urls:
        download(url)


if __name__ == '__main__':
    download_files()
