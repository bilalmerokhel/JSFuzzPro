import asyncio
import aiohttp
import argparse
import csv
import re
import time
from bs4 import BeautifulSoup

CACHE = {}  # Cache for storing results

REQUEST_TIMEOUT = 10  # Request timeout in seconds
MAX_CONCURRENT_REQUESTS = 10  # Maximum concurrent requests

async def get_archived_pages(domain):
    if domain in CACHE:
        return CACHE[domain]

    url = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&collapse=urlkey"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                pages = [entry[2] for entry in data]
                CACHE[domain] = pages
                return pages
            else:
                print(f"Failed to retrieve archived pages for domain: {domain}")
                return []

async def get_js_files(url):
    if url in CACHE:
        return CACHE[url]

    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                js_files = []
                script_tags = soup.find_all('script')

                for script_tag in script_tags:
                    if script_tag.has_attr('src'):
                        js_url = script_tag['src']
                        if js_url.endswith('.js'):  # Filter to consider only JavaScript files
                            js_files.append(js_url)

                CACHE[url] = js_files
                return js_files
            else:
                print(f"Failed to retrieve JavaScript files from URL: {url}")
                return []

async def extract_endpoints(url):
    if url in CACHE:
        return CACHE[url]

    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            if response.status == 200:
                javascript_code = await response.text()

                # Use regular expressions or other techniques to extract endpoints from the JavaScript code
                patterns = [
                    r'"(https?://.*?)"',        # Example pattern 1
                    r'"(http?://.*?)"',         # Example pattern 2
                    r'"(/.*?)"',                # Example pattern 3
                    r'\'(https?://.*?)\'',      # Example pattern 4
                    r'\'(/.*?)\'',              # Example pattern 5
                    r'"(\/\/.*?)"',             # Example pattern 6
                    # Add more patterns as needed
                ]

                endpoints = []
                for pattern in patterns:
                    endpoints.extend(re.findall(pattern, javascript_code))

                CACHE[url] = endpoints
                return endpoints
            else:
                print(f"Failed to retrieve JavaScript code from URL: {url}")
                return []

async def extract_parameters(url):
    if url in CACHE:
        return CACHE[url]

    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            if response.status == 200:
                javascript_code = await response.text()

                # Use regular expressions or other techniques to extract parameter names from the JavaScript code
                patterns = [
                    r'(\w+)(?=:)',                      # Example pattern 1
                    r'\b(\w+)\b(?=\s*=\s*function\(\))', # Example pattern 2
                    r'\b(\w+)\b(?=\s*:\s*function\(\))', # Example pattern 3
                    r'function\s*\w+\s*\(([\w,\s]+)\)',  # Example pattern 4
                    # Add more patterns as needed
                ]

                parameters = []
                for pattern in patterns:
                    matches = re.findall(pattern, javascript_code)
                    parameters.extend(matches)

                CACHE[url] = parameters
                return parameters
            else:
                print(f"Failed to retrieve JavaScript code from URL: {url}")
                return []

async def fuzz_endpoint(session, endpoint, method, payload=None, wordlist=None):
    print(f"Performing fuzzing on endpoint: {endpoint}")

    if wordlist is None:
        wordlist = []

    request_functions = {
        'GET': session.get,
        'POST': session.post,
        'PUT': session.put,
        'PATCH': session.patch
    }

    async with request_functions[method](endpoint, data=payload, timeout=REQUEST_TIMEOUT) as response:
        pass

def generate_payloads(endpoints, parameters):
    payloads = []

    for endpoint in endpoints:
        for parameter in parameters:
            payload = {parameter: 'FUZZ'}
            payloads.append((endpoint, payload))

    return payloads

async def parse_domains(domains, use_wordlist=False, wordlist_path=None):
    all_results = []
    tasks = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    if use_wordlist and wordlist_path:
        with open(wordlist_path, 'r') as file:
            wordlist = file.read().splitlines()
    else:
        wordlist = None

    async with aiohttp.ClientSession() as session:
        for domain in domains:
            archived_pages = await get_archived_pages(domain)

            for page in archived_pages:
                js_files = await get_js_files(page)

                for js_file in js_files:
                    endpoints = await extract_endpoints(js_file)
                    parameters = await extract_parameters(js_file)
                    payloads = generate_payloads(endpoints, parameters)

                    for endpoint, payload in payloads:
                        async with semaphore:
                            task = asyncio.create_task(fuzz_endpoint(session, endpoint, payload=payload, wordlist=wordlist))
                            tasks.append(task)

        await asyncio.gather(*tasks)

def main():
    parser = argparse.ArgumentParser(description='JavaScript Fuzzing Tool')
    parser.add_argument('domains', metavar='domain', type=str, nargs='+',
                        help='single domain or comma-separated list of domains')
    parser.add_argument('-w', '--wordlist', dest='wordlist', action='store_true',
                        help='use wordlist for fuzzing')
    parser.add_argument('-p', '--path', dest='wordlist_path', type=str,
                        help='full path to the wordlist file')

    args = parser.parse_args()
    domains = [domain.strip() for domain in args.domains[0].split(',')]

    start_time = time.time()
    asyncio.run(parse_domains(domains, use_wordlist=args.wordlist, wordlist_path=args.wordlist_path))
    end_time = time.time()

    print(f"Execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
