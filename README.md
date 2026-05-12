Install link: https://discord.com/oauth2/authorize?client_id=1502479609701203998
Instructions are in the description of the discord bot

Here is a  dump of generic instructions for getting it working on a windows server:

encode all py and txt files as UTF-8

run setup.py

run 'mitmproxy' on its own and then quit

check that there are cert files in ~/.mitmproxy/

change your windows proxy settings to route through 192.0.0.1:8080 (netsh winhttp set proxy 127.0.0.1:8080)

visit http://mitm.it/ and download the windows certificate

install it:
Import-PfxCertificate `
  -FilePath "C:\Users\opc\RoK\mitmproxy-ca-cert.p12" `
  -CertStoreLocation Cert:\CurrentUser\Root

set the proxy:
netsh winhttp set proxy 127.0.0.1:8080
"netsh winhttp show proxy" should say "Proxy Server(s) : 127.0.0.1:8080"

run:
mitmdump -p 8080 -s sniffer.py

then run:
python runRequest.py <discord bot auth token>
