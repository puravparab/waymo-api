import logging
from typing import Optional

from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from .exceptions import WaymoClientError

from ..utils.logger import get_logger
logger = get_logger(__name__)

class AppiumDriverManager:
	def __init__(self, device_name: str, timeout: int):
		self.platform_name = 'Android'
		self.device_name = device_name
		self.timeout = timeout
		self.driver = None
		self.wait = None
		self.app_package = 'com.waymo.carapp'
		self.app_activity = 'com.google.android.apps.car.carapp.LaunchActivity'

	def _setup_driver(self) -> UiAutomator2Options:
		try:
			"""Configure and return Appium driver options"""
			options = UiAutomator2Options()
			options.platform_name = self.platform_name
			options.device_name = self.device_name
			options.app_package = self.app_package
			options.app_activity = self.app_activity
			options.no_reset = True
			options.set_capability('skipServerInstallation', True)
			options.set_capability('skipDeviceInitialization', True)
			options.set_capability('autoGrantPermissions', True)
			options.set_capability('disableWindowAnimation', True)
			options.set_capability('disableAndroidWatchers', True) 
			return options

		except Exception as e:
			logger.error(f"Failed to setup driver options: {str(e)}")
			raise WaymoClientError(f"Driver setup failed: {str(e)}")

	def connect(self) -> None:
		"""Establish connection to Appium server and initialize driver"""
		try:
			logger.info("Connecting to Appium...")
			options = self._setup_driver()
			self.driver = webdriver.Remote('http://localhost:4723', options=options)
			self.wait = WebDriverWait(self.driver, self.timeout)
			logger.info("Connected successfully to Appium")
			self._handle_app_state()
		except Exception as e:
			logger.error(f"Failed to connect to Appium: {str(e)}")
			self.quit()
			raise WaymoClientError(f"Appium connection failed: {str(e)}")

	def _handle_app_state(self) -> None:
		"""Handle the Waymo app state and ensure it's in the correct state"""
		try:
			if not self.driver:
				raise WaymoClientError("Driver not initialized")
					
			current_activity = self.driver.current_activity
			if current_activity == self.app_activity:
				logger.info("App already in correct state")
				return
					
			logger.info("Launching Waymo app...")
			self.driver.activate_app(self.app_package)
			
		except Exception as e:
			logger.error(f"Failed to handle app state: {str(e)}")
			raise WaymoClientError(f"App state handling failed: {str(e)}")

	def quit(self) -> None:
		"""Clean up and close the driver connection"""
		try:
			if self.driver:
				logger.info("Closing Appium driver...")
				self.driver.quit()
				logger.info("Successfully closed Appium driver")
		except Exception as e:
			logger.error(f"Error while closing driver: {str(e)}")
			raise WaymoClientError(f"Failed to close driver: {str(e)}")