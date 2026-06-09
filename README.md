Install link: https://discord.com/oauth2/authorize?client_id=1502479609701203998
Instructions are in the description of the discord bot

Here is a  dump of generic instructions for getting it working on a windows server:

#Machine Setup

open ports 22 and 3389

Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

choco install python312 -y

Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd

scp B:/Git/RoK/RoK.zip RoK@20.114.12.33:C:/Users/RoK/

#Bot setup

encode all py and txt files as UTF-8

run setup.py

run 'mitmproxy' on its own and then quit

check that there are cert files in ~/.mitmproxy/

scp B:/Git/RoK/mitmproxy-ca-cert.p12 RoK@20.114.12.33:C:/Users/RoK

install it:
Import-PfxCertificate `
  -FilePath "C:\Users\opc\RoK\mitmproxy-ca-cert.p12" `
  -CertStoreLocation Cert:\CurrentUser\Root

set the proxy:
netsh winhttp set proxy 127.0.0.1:8080
"netsh winhttp show proxy" should say "Proxy Server(s) : 127.0.0.1:8080"

run:
python discordListener.py <discord bot auth token>
