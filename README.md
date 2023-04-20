# SdPaint with SHARK
A simple python script that lets you paint on a canvas and sends that image every stroke to the automatic1111 API and updates the canvas when the image is generated

## Updates

- added the possibility to save the image created by pressing the ```s``` key
- You can use the scrollmouse key to change the brush size

## Installation and Usage

* First download the latest SHARK SD webui .exe from [here](https://github.com/nod-ai/SHARK/releases) or follow instructions on the [README](https://github.com/nod-ai/SHARK#readme)
* Once you have the .exe where you would like SHARK to install, run the .exe from terminal/PowerShell with the `--api` flag:
```
## Run the .exe in API mode:
.\shark_sd_<date>_<ver>.exe --api
## For example:
.\shark_sd_20230411_671.exe --api
## From a the base directory of a source clone of SHARK:
./setup_venv.ps1
python apps\stable_diffusion\web\index.py --api
```

Your local SD server should start and look something like this:
![image](https://user-images.githubusercontent.com/87458719/231369758-e2c3c45a-eccc-4fe5-a788-4a3bf1ace1d1.png)

* Note: When running in api mode with `--api`, the .exe will not function as a webUI. Thus, the address in the terminal output will only be useful for API requests.

* If you are modifying `server_port` via SHARK's sd webui, then ensure you modify the port in `Scripts/SdPaint.py` as well.

* Now run `Start.sh` after setting the permission using `chmod` command. Or run `Start.bat` for Windows.

left mouse to draw and middlemouse to erase
press backspace to erase the image.
Enter prompt (default `shark`) in the toolbar above as well as change `steps` (default `20`).
the program is bound to 512x512 images right now and doesn't have the ability to save the image right now.
I may add more features at a later time.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
