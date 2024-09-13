const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const app = express();
const port = 3000;

console.clear();

async function fetchNextData(query) {
    if (!query.trim()) {
        console.log('Empty search query provided.');
        return {
            count: 0,
            books: [],
            message: 'Search query is empty',
            "Dasturchi": '@DilyorbekPHP or @Dilyorbek_Web'
        };
    }

    console.log(`Fetching data for query: ${query}`);
    const encodedQuery = encodeURIComponent(query);
    const url = `https://ziyonet.uz/uz/search?search=${encodedQuery}&audios=1&books=1`;

    try {
        const response = await axios.get(url);
        console.log('Received response from the site.');

        const $ = cheerio.load(response.data);
        const nextDataScript = $('script#__NEXT_DATA__').html();

        if (nextDataScript) {
            const jsonData = JSON.parse(nextDataScript);

            // Adjust this path based on actual JSON structure
            const searchResult = jsonData.props.pageProps.searchResult || {};
            const books = searchResult.data && searchResult.data.books ? searchResult.data.books : [];

            // Process the books to keep only the required fields
            const processedBooks = books.map(book => ({
                id: book.id,
                title: book.title,
                description: book.description,
                level: book.level,
                type: book.type,
                file: book.file,
                cover: book.cover,
                created_at: book.created_at
            }));

            // Save the full books array to a file
            // fs.writeFileSync('books.json', JSON.stringify(processedBooks, null, 2));
            // console.log('Processed books data saved to books.json');

            return {
                count: processedBooks.length,
                books: processedBooks
            };
        } else {
            console.log('__NEXT_DATA__ script not found');
            return {
                count: 0,
                books: [],
                message: 'No books data found on the page',
                "Dasturchi": '@DilyorbekPHP or @Dilyorbek_Web'
            };
        }
    } catch (error) {
        console.error('Error fetching the page:', error.message);
        return {
            count: 0,
            books: [],
            message: 'Error fetching data'
        };
    }
}

app.get('/api/books', async (req, res) => {
    const query = req.query.search;  // Updated to use the correct query parameter name

    if (!query || query.trim() === '') {
        return res.status(400).json({
            message: 'Missing or empty search parameter',
            "Dasturchi": '@DilyorbekPHP or @Dilyorbek_Web'
        });
    }

    console.log(`API request received with search query: ${query}`);
    const { count, books, message } = await fetchNextData(query);

    if (count > 0) {
        res.json({ count, books });
    } else {
        res.status(404).json({ message, count });
    }
});

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});
