# Python Audiobookshelf API

This is a python implementation for the API of the popular self hosted Audiobook and Podcast management software [Audiobookshelf](https://audiobookshelf.org).

## Note

This Libarary is currently still in early development and not ready for use

## Example use


Deleting all Authors that have no books associated with them.
```py
from audiobookshelf import ABSClient
import asyncio


ABS_URL = 'https://abs.example.com'
ABS_USER = 'root'
ABS_PASSWORD = 'test123'


async def run_test():
    client = ABSClient(ABS_URL)
    await client.authorize(ABS_USER, ABS_PASSWORD)
    libs = await client.get_libraries()
    for lib in libs:
        authors = await client.get_library_authors(lib.id)
        for author in authors:
            if author.num_books == 0:
                print(f'{author.name} in {lib.name} has no books, deleting...')
                await client.delete_author(author.id)


asyncio.run(run_test())
```
