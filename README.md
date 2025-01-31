### What is this?

Waymo doesn't have an API where you can get ride prices after entering pickup/dropoff points. This is an unofficial python api for Waymo that can be run locally to get realtime waymo ride prices. 


### Setup

Getting the server and emulator setup is a little tedious. For now this setup works with MacOS/Linux.

Before you get started, you'll need the following installed on your machine:

- Android Studio
- uv (Python package manager)
- Python 3.12
- npm (for appium)

#### Setting up the Android virtual device

1. Install [Android Studio](https://developer.android.com/studio) on your device

2. Create a virtual android device `Projects > More Actions > Virtual Device Manager > Select a device`

3. On the virtual device, install the the [Waymo One](https://play.google.com/store/apps/details?id=com.waymo.carapp) application.

4. After the Waymo One application is installed, log into the application with your username and password.

For future uses, you can spin up the virtual device with the Waymo app through the terminal

#### Installing Android debug bridge

You will need this for changing the device location 

1. For MacOS
	```bash
	brew install android-platform-tools
	```
2. For Linux (Ubuntu)
	```bash
	sudo apt install adb
	```

#### Setting up the project repository

1. Clone the repository
	```bash
	git clone git@github.com:puravparab/waymo-api.git
	```

2. Change directory
	```
	cd waymo-api
	```

3. Install [uv](https://docs.astral.sh/uv) if you don't have it

4. Install python dependencies
	```bash
	uv sync
	```

### Usage

Before you can use the API, you have to do three things
- [Spin up](#start-the-android-virtual-device) the Android virtual device
- [Start](#start-appium-server) the appium server
- [Change location](#start-the-android-virtual-device) to desired Waymo service area (eg. San Francisco)

#### Start the Android virtual device

Make sure you have succesfully [set up](#setting-up-the-android-virtual-device) the virtual device and Waymo one application before proceeding

1. Create a new terminal instance and enter the following:
	```bash
	export ANDROID_HOME=$HOME/Library/Android/sdk
	export ANDROID_SDK_ROOT=$HOME/Library/Android/sdk
	export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools
	export PATH=$PATH:$ANDROID_HOME/emulator
	```

2. Display list of devices in android studio
	```bash
	emulator -list-avds
	```

3. Spin up the virtual android device with the installed Waymo One application
	```bash
	emulator -avd <device name>
	```

4. After the device is started, change the device location to the desired Waymo service area. (Make sure you have downloaded [adb](#installing-android-debug-bridge))
	> This will take some time before the Waymo app changes the location (I recommend running this when the device is booting up)

	```bash
	// Select one of the following

	adb emu geo fix <longitude> <latitude>

	adb emu geo fix -122.431297 37.773972 // San Francisco

	adb emu geo fix -118.243683 34.052235 // Los Angeles

	adb emu geo fix -112.074036 33.448376 // Phoenix

	adb emu geo fix -97.733330 30.266666 // Austin
	```

5. I would recommend opening the Waymo One app before using the API

#### Start appium server

We need appium so the API can talk to the virtual device

1. Create a new terminal instance and enter the following:
	```bash
	export ANDROID_HOME=$HOME/Library/Android/sdk
	export ANDROID_SDK_ROOT=$HOME/Library/Android/sdk
	export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools
	```

2. Install appium
	```bash
	npm install -g appium
	```

3. Start appium
	```bash
	appium
	```

#### Use Waymo API

See [examples](./examples/) directory for usage examples or use the following commands
```bash
uv run examples/demo/main.py --trip "Fort Mason" "Salesforce Tower"
```
```bash
uv run examples/demo/main.py --trips examples/demo/trips.json
```


### Developer Usage

#### Save screen state

1. You'll need [adb](#android-debug-bridge) for this
	```bash
	adb shell uiautomator dump && adb pull /sdcard/window_dump.xml
	```

### Contributing / Issues

Feel free to create a pull request or an issue and i will try to review it

### License

MIT (I'm not affiliated with Waymo or Google. This project is for educational purposes only)