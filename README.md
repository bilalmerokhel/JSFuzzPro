# JSFuzzPro
JSFuzzPro is an advanced JavaScript fuzzing tool for automated endpoint identification and testing. Unleash the power of fuzzing on JavaScript files from archived web pages, detecting vulnerabilities in web applications.

## Usage
`python JSFuzzPro.py [options] domain(s)`


## Arguments

- `domain(s)`: Specify one or more domains to perform fuzzing on. Multiple domains can be separated by commas.

## Options

- `-w, --wordlist`: Use a wordlist for fuzzing. If this option is specified, a wordlist file must also be provided using the `-p` option.
- `-p, --path`: Specify the full path to the wordlist file to be used for fuzzing.

## Functionality

1. **Archived Pages Retrieval**: The tool retrieves archived pages for the specified domains from the Wayback Machine (web.archive.org).
2. **JavaScript File Extraction**: It extracts JavaScript files from the retrieved archived pages using web scraping techniques.
3. **Endpoint Extraction**: The tool scans the extracted JavaScript files to identify URLs representing endpoints using regular expressions.
4. **Parameter Extraction**: It extracts parameter names from the JavaScript code to be used for fuzzing.
5. **Fuzzing**: The tool performs fuzzing on the identified endpoints using various HTTP methods (GET, POST, PUT, PATCH) and payloads generated from the extracted parameters and a wordlist (if provided).
6. **Throttling**: The tool limits the number of concurrent requests using a semaphore to avoid overwhelming the target server.
7. **Request Timeouts**: Each HTTP request has a timeout value specified to handle unresponsive or slow endpoints.

## Example

- This command will perform fuzzing on the domain example.com using the wordlist specified in the `wordlist.txt` file.

`python JSFuzzPro.py example.com -w -p wordlist.txt`

## Requirements
- To install the required dependencies, run the following command.

`pip install -r requirements.txt`

