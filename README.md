setup.py

run 'mitmproxy' on its own and then quit
check that there are cert files in ~/.mitmproxy/
change your windows proxy settings to route through 192.0.0.1:8080
visit http://mitm.it/ and download the windows certificate
run:
mitmdump -p 8080 -s sniffer.py
then run:
python runRequest.py <discord bot auth token>