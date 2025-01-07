### What is this?

Waymo does not have an API where you con get ride prices after entering a pickup point and destination. This is my attempt at building an unofficial api for Waymo that you can run locally and get realtime ride prices. 

### Setup

Getting the server setup is a little tedious so bare with me. For now this setup works with MacOS/Linux

Before you get started, you'll need the following:
```
- Android Studio (To run the Waymo application)
- uv (Python package manager)
- Python
```

#### Android Virtual Device

1. Install [Android Studio](https://developer.android.com/studio) on your device

2. Create a virtual android device `Projects > More Actions > Device Manager`

3. On the virtual device, install the the [Waymo One](https://play.google.com/store/apps/details?id=com.waymo.carapp) application.

4. After the Waymo One application is installed, enter your username and password into the app.

#### Python API
1. Install [uv](https://docs.astral.sh/uv) if you don't have it already

2. Install python dependencies
	```bash
	uv sync
	```

3. Run appium in a separate terminal with the following commands

	```bash
	export ANDROID_HOME=$HOME/Library/Android/sdk
	export ANDROID_SDK_ROOT=$HOME/Library/Android/sdk
	export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools

	appium
	```

	This should run the appium server


4. Run the python script

	```bash
	uv run main.py
	```

### Contributing / Issues

Feel free to create a pull request or an issue and i will try to review it

### License

MIT (I'm not affiliated with Waymo or Google. This project is for educational purposes only)