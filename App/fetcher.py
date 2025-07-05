import requests
from bs4 import BeautifulSoup

def fetch_and_parse(url: str) -> str:
    """
    Fetches the content of a given URL and parses the HTML to extract text.

    Args:
        url: The URL to fetch.

    Returns:
        The extracted text content from the URL, or an empty string if fetching fails.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Get text
        text = soup.get_text()

        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return ""

if __name__ == '__main__':
    # Example usage:
    test_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    content = fetch_and_parse(test_url)
    if content:
        print(f"Successfully fetched and parsed content from {test_url}")
        # print(content[:500] + "...") # Print first 500 characters
