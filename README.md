# THOWL-Gradescraper
A simple web scraper that pulls your grades from the TH OWL server and notifies you by e-mail when a new grade is published

## How to use
1. Clone/Download this repository
2. Put your *.p12 Certificate in the folder of the repository
3. Change the parameters smpt_port, smpt_server, email_sender, email_password, email_receiver, cer_filename, cer_password in the file "Scraper.py"
4. Change Line 9 of the dockerfile so that the filename matches the filename of your Certificate
5. run "sudo docker build -t gradescraper" 
6. run "docker run --restart unless-stopped gradescraper"

## Remark
This gradescraper was created for the THOWL website as of 18.12.2023, if the page is revised the code must be adapted.
## Important
The code is designed for the degree program Computer Engineering, if you study something else it may be that a string in the code needs to be adjusted. (Line 40 in Scraper.py, the number in the string must be changed to the same number that you see when you call up the page in the web browser to see your grade) 
