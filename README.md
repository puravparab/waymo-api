### What is this?

Waymo does not have an API where you can get ride prices after entering pickup/dropoff points. This is an unofficial python api for Waymo that can be run locally to get realtime waymo ride data. 

### Setup

Getting the server setup is a little tedious so bear with me. For now this setup works with MacOS/Linux

Before you get started, you'll need the following:
```
- Android Studio
- uv (Python package manager)
- Python
```

1. Clone the repository

	```bash
	git clone git@github.com:puravparab/waymo-api.git

	cd waymo-api
	```

#### Android Virtual Device

1. Install [Android Studio](https://developer.android.com/studio) on your device

2. Create a virtual android device `Projects > More Actions > Virtual Device Manager > Select a device`

3. On the virtual device, install the the [Waymo One](https://play.google.com/store/apps/details?id=com.waymo.carapp) application.

4. After the Waymo One application is installed, enter your username and password into the app.

For future uses, you can spin up the virtual device with the Waymo One application as follows:

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

4. Wait for the device to spin up before proceeeding

#### Python API
1. Install [uv](https://docs.astral.sh/uv) if you don't have it already

2. Install python dependencies
	```bash
	uv sync
	```

3. Create a new terminal instance and enter the following commands
	```bash
	export ANDROID_HOME=$HOME/Library/Android/sdk
	export ANDROID_SDK_ROOT=$HOME/Library/Android/sdk
	export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools

	appium
	```

	This should run the appium server


4. Run the python script in another terminal

	```bash
	uv run examples/demo/main.py --trip "Fort Mason" "Salesforce Tower"
	```
	```
	uv run examples/demo/main.py --trips examples/demo/trips.json
	```

### Developer Usage

#### Android debug bridge

1. For MacOS
	```
	brew install android-platform-tools
	```
2. For Linux (Ubuntu)
	```
	sudo apt install adb
	```

#### Update location

1. If you want to use Waymo in a different location do this. (You will need to download [adb](#android-debug-bridge))
	```
	adb emu geo fix <longitude> <latitude>

	adb emu geo fix -122.431297 37.773972 // San Francisco

	adb emu geo fix -118.243683 34.052235 // Los Angeles

	adb emu geo fix -112.074036 33.448376 // Phoenix

	adb emu geo fix -97.733330 30.266666 // Austin
	```
	
#### Save screen state

1. You'll need [adb](#android-debug-bridge) for this
	```bash
	adb shell uiautomator dump && adb pull /sdcard/window_dump.xml
	```

### Contributing / Issues

Feel free to create a pull request or an issue and i will try to review it

### License

MIT (I'm not affiliated with Waymo or Google. This project is for educational purposes only)