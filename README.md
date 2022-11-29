# OW2 Cache Merge
This is a tool to check multiple configurable github repos for dxvk cache files for Overwatch 2 and download if a new (bigger) cache file found on the repo, then merge downloaded cache files with your current cache file and put it under your game directory after backing up your current cache file. It uses [dxvk-cache-tool](https://github.com/DarkTigrus/dxvk-cache-tool) from DarkTigrus github repo for merging dxvk cache files.

## Installation
```bash 
pip install ow2-cache-merge
```
or
```bash
git clone https://github.com/leventguney/ow2-cache-merge.git
cd ow2-cache-merge
python setup.py install
```
## Usage
Just run the script from command line
```bash 
ow2-cache-merge
```
## Configuration
This tool creates `.ow2-cache-merge` folder under your home directory.
Using `config.toml` you can set your game folder
If your game is in "/home/username/Games/overwatch-2" you should set `game_dir = "Games/overwatch-2"`
If it is installed elsewhere you can also set an absolute path here like `gamedir="/run/media/Games/overwatch-2"`

You can add repos in the `config.toml` file like below:
```
[repos]
GolDNenex="https://raw.githubusercontent.com/GolDNenex/overwatch2-dxvk-cache/main/Overwatch.dxvk-cache"
Elagoht="https://github.com/Elagoht/overwatch2-dxvkcache/raw/master/Overwatch.dxvk-cache"
```

 `records.toml` file under `.ow2-cache-merge` directory, holds the cache file sizes of the repos

