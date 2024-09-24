from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup
import json

app = FastAPI()

# Model for the book data response
class Book(BaseModel):
    id: str
    title: str
    description: str
    level: str
    type: str
    file: str
    cover: str
    created_at: str

class BooksResponse(BaseModel):
    count: int
    books: list[Book]
    message: str = None
    Dasturchi: str = '@DilyorbekPHP or @Dilyorbek_Web'

async def fetch_next_data(query: str):
    if not query.strip():
        return BooksResponse(
            count=0,
            books=[],
            message='Search query is empty',
            Dasturchi='@DilyorbekPHP or @Dilyorbek_Web'
        )

    print(f'Fetching data for query: {query}')
    encoded_query = query.replace(" ", "%20")
    url = f"https://ziyonet.uz/uz/search?search={encoded_query}&audios=1&books=1"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses

        print('Received response from the site.')

        soup = BeautifulSoup(response.text, 'html.parser')
        next_data_script = soup.find('script', id="__NEXT_DATA__")

        if next_data_script:
            json_data = json.loads(next_data_script.string)

            # Adjust this path based on actual JSON structure
            search_result = json_data.get('props', {}).get('pageProps', {}).get('searchResult', {})
            books = search_result.get('data', {}).get('books', [])

            # Process the books to keep only the required fields
            processed_books = [
                Book(
                    id=str(book['id']),  # Convert id to string
                    title=book['title'],
                    description=book['description'],
                    level=book['level'],
                    type=book['type'],
                    file=book['file'],
                    cover=book['cover'],
                    created_at=book['created_at']
                )
                for book in books
            ]

            return BooksResponse(
                count=len(processed_books),
                books=processed_books
            )
        else:
            print('__NEXT_DATA__ script not found')
            return BooksResponse(
                count=0,
                books=[],
                message='No books data found on the page',
                Dasturchi='@DilyorbekPHP or @Dilyorbek_Web'
            )
    except httpx.HTTPError as error:
        print(f"Error fetching the page: {error}")
        return BooksResponse(
            count=0,
            books=[],
            message='Error fetching data'
        )

@app.get("/api/books", response_model=BooksResponse)
async def get_books(search: str = Query(..., min_length=1)):
    print(f"API request received with search query: {search}")
    result = await fetch_next_data(search)

    if result.count > 0:
        return result
    else:
        raise HTTPException(status_code=404, detail=result.message)

# Run the FastAPI app
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)
