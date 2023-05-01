# ruckus-captive-portal-client
The client is to auto-accept the captive portal from Ruckus. This tool pretty much automates getting access to the Internet through WiFi, accepting terms for you

### Dependencies
- **selenium** https://www.selenium.dev/


### To Install
Selenium requires a driver to interface with your favorite browser.
Firefox, for example, requires geckodriver, which needs to be installed before the script can be run.
Check [Drivers](https://selenium-python.readthedocs.io/installation.html#drivers) section for more info how to install it

An example how to install it with Chromium on Ubuntu:
```bash
apt install chromium-browser chromium-chromedriver
```
- After you get the driver, follow the steps below
```shell script
apt install python3-pip
git clone https://github.com/rooty0/ruckus-captive-portal-client
cd ruckus-captive-portal-client
cp config.example.yaml /etc/cp-client.yaml
pip3 install -r requirements.txt # alternatively you can do "python3 -m venv venv" to install everything under VENV, fix other stuff 
```
- MAKE sure `cpc` system user is created!
- Finish the installation
```bash
cp captive-portal-client.py /usr/bin/captive-portal-client.py
chmod +x /usr/bin/captive-portal-client.py
mv "cp-client.service" /etc/systemd/system
```

### To Confirm It Works
Just run something like below, you get the output
```bash
sudo -u cpc /usr/bin/captive-portal-client.py
```

### Configuration
You need to edit `/etc/cp-client.yaml` configuration file and modify path to your driver, example: "/usr/bin/chromedriver"

### To Run
```bash
systemctl daemon-reload
systemctl enable cp-client
systemctl start cp-client
journalctl -efu cp-client
```

## Contribute
Feel free to create a PR