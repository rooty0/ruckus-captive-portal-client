import urllib3.exceptions
import yaml
import signal
import logging
import argparse
import sys
import os

from time import sleep

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options


__version__ = 1
log = logging.getLogger('cpc')


def load_config():
    config_path_search = ['config.yaml', '/etc/cp-client.yaml']
    active_config = ''

    for config in config_path_search:
        if os.path.isfile(config):
            active_config = config
            break

    if not active_config:
        raise Exception('Configuration is missing')

    return yaml.load(open(active_config).read(), Loader=yaml.UnsafeLoader)


class Cpc:
    driver = None
    termination = 0
    check_interval_seconds = 10
    cp_detection_url = 'http://captive.apple.com/'
    cp_search_in_url = 'Success\n'

    def __init__(self, driver_path, open_chrome=False):
        chrome_options = Options()
        if not open_chrome:
            chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(driver_path, options=chrome_options)
        signal.signal(signal.SIGINT, Cpc.signal_handler)

    def __del__(self):
        try:
            self.driver.close()
        except (urllib3.exceptions.MaxRetryError, ValueError):
            pass  # this is ugly hack to suppress errors that "driver.close()" produces for some reason

    def get_driver(self):
        return self.driver

    @classmethod
    def signal_handler(cls, signum, frame):
        cls.termination += 1
        if cls.termination == 1:
            print("Ok, shutting down, please wait", flush=True)
        else:
            sys.exit()

    def run(self):

        while not self.termination:

            self.driver.get(self.cp_detection_url)
            if self.cp_search_in_url in self.driver.page_source:
                log.debug("Already connected")
            else:
                log.info("Auto-login initiated...")

                try:
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "acceptBtn")))
                except exceptions.TimeoutException:
                    log.error("Can't find the button to click, re-initiating the sequence")
                    continue

                try:
                    for i in range(3):  # clicking the button couple times if nothing happens
                        log.debug(f"Clicking AGREE button, retry {i}")
                        accept_button = self.driver.find_element(By.ID, "acceptBtn")
                        accept_button.click()
                        log.debug("Waiting until the BOX page content is different")
                        try:
                            WebDriverWait(self.driver, 5).until(EC.staleness_of(accept_button))  # seconds
                            break
                        except exceptions.TimeoutException:
                            continue

                except exceptions.NoSuchElementException as e:
                    print(e)

                try:
                    WebDriverWait(self.driver, 10).until(EC.title_contains("Success"))
                except exceptions.TimeoutException:
                    log.error(f"Can't reach {self.cp_detection_url}")
                    sleep(1)
                    log.info("Skipping countdown interval")
                    continue

            sleep(self.check_interval_seconds)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    log.setLevel(logging.INFO)
    fh = logging.StreamHandler(sys.stdout)
    fh.setFormatter(logging.Formatter('%(message)s'))
    log.addHandler(fh)

    parser = argparse.ArgumentParser(
        description='\033[93m[[ {} ]]\033[0m tool v{}'.format("CPC", __version__),
    )

    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False)
    parser.add_argument('--open-chrome', dest='show_chrome_browser', action='store_true', default=False)
    args = parser.parse_args(args)
    if args.debug is True:
        log.setLevel(logging.DEBUG)
        log.debug("Debug message mode is enabled")

    config = load_config()

    cpc = Cpc(config['SELENIUM_DRIVER_PATH'], args.show_chrome_browser)
    log.info("Starting to monitor")
    cpc.run()
    log.info("All done, bye")


if __name__ == '__main__':
    main()
