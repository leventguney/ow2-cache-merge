import os
import sys
from typing import Any, Dict, List
from urllib.request import urlopen, urlretrieve
from urllib.error import HTTPError, URLError
from loguru import logger
import toml
import shutil
import subprocess

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<level>{level} {time:DD-MM at HH:mm:ss} {message}</level>",
)

class CacheMerger:
    def __init__(self) -> None:
        self.work_path: str = os.path.join(os.getenv("HOME"), '.cache_merger') # type: ignore
        self.record_file_path: str = os.path.join(self.work_path, 'records.toml')  
        self.config_file_path: str = os.path.join(self.work_path, 'config.toml')  
        self.cache_files_dir: str = os.path.join(self.work_path, 'cache_files')  
        self.merge_files_dir: str = os.path.join(self.work_path, 'merge_files') 
        self.cache_tool_path: str = os.path.join(os.path.dirname(__file__), 'lib', 'dxvk-cache-tool')
        self.config: Dict[str, Any] = {}
        self.records: Dict[str, Any] = {}
        """Holds records of file sizes of the repos"""
        self.updated_cache_file_paths: List[str] = []
        """Used to determine which updated cache files to use while merging"""
        self.config_keys = set(['game_dir', 'repos'])
        """Used to check config file"""
        self.update_found: bool = False
        """Update record file with new sizes if this is true"""
        if not os.path.exists(self.work_path):
            try:
                logger.info("Creating work folder ~/.cache_manager")
                os.makedirs(self.work_path)
                self._create_initial_config()
            except Exception as e:
                logger.error(e)
                sys.exit(1)
        self._load_config()
        self.game_dir = os.path.join(os.getenv("HOME"), self.config["game_dir"])  # type:ignore

    def check_update(self):
        self._load_records()
        for repo, url in self.config['repos'].items():
            new_size = self._get_repo_file_size(url)
            old_size = self.records.get(repo) or 0
            if isinstance(new_size, int):
                if new_size > old_size:
                    logger.info(f'An updated cache file is found on github repo {repo}')
                    self._download_cache_file(repo, url)
                    self._update_record(repo,new_size)
                    self.update_found = True
                else:
                    logger.info(f'No new cache file found on the repo {repo}')
        if self.update_found:
            self._update_record_file()
            self._merge_cache_files()

    def _load_config(self):
        if not os.path.exists(self.config_file_path):
            logger.warning('Config file is not found, creating an initial config')
            self._create_initial_config()
        try:
            self.config = toml.load(self.config_file_path)
            config_keys = set(self.config.keys())
            if not config_keys == self.config_keys:
                logger.warning('Icorrect configuration file, do you want to create an initial one?')
                response = input('y/n\n')
                if response in ['Y', 'y']:
                    self._backup_old_config()
                    self._create_initial_config()
                    self._load_config()
                else:
                    logger.error('Cancelled creating initial config, exiting..')
                    sys.exit(1)
        except Exception as e:
            logger.error(e)
    
    def _create_initial_config(self):
        logger.info("Creating initial config..")
        initial_config_file_path = os.path.join(os.path.dirname(__file__), "config.toml")
        shutil.copyfile(initial_config_file_path, self.config_file_path)

    def _download_cache_file(self, repo: str, url: str):
        logger.info(f'Downloading cache file from repo {repo}..')
        cache_file_dir = os.path.join(self.cache_files_dir, repo)
        try:
            if not os.path.exists(cache_file_dir):
                os.makedirs(cache_file_dir)
            cache_file_name = url.split('/')[-1]
            cache_file_path = os.path.join(cache_file_dir, cache_file_name)
            self.updated_cache_file_paths.append(cache_file_path)
            urlretrieve(url, cache_file_path)
        except Exception as e:
            print(e)

    def _backup_old_config(self):
        shutil.copyfile(self.config_file_path, self.config_file_path + '.old')

    def _load_records(self):
        logger.info("Reading last downloaded dxvk cache file sizes from record file")
        try:
            self.records = toml.load(self.record_file_path)
        except FileNotFoundError as e:
            logger.warning(f"{self.record_file_path} is not found, will create a new one")
    
    def _merge_cache_files(self):
        if not os.path.exists(self.merge_files_dir):
            try:
                os.makedirs(self.merge_files_dir)
            except Exception as e:
                logger.error(e)
                sys.exit(1)
        current_cache_file_path = os.path.join(self.game_dir, "Overwatch.dxvk-cache")
        merged_cache_file_path = os.path.join(self.merge_files_dir, "Merged.dxvk-cache")
        command_tokens = [
            self.cache_tool_path, 
            "-o", 
            merged_cache_file_path,
            current_cache_file_path]
        command_tokens.extend(self.updated_cache_file_paths)
        try:
            completed_process = subprocess.run(command_tokens, check=True, stdout=subprocess.PIPE)
            print(completed_process.stdout.decode("UTF-8"))
        except subprocess.CalledProcessError as e:
            print(e.output)
        shutil.copyfile(current_cache_file_path, f"{current_cache_file_path}.old")
        shutil.copyfile(merged_cache_file_path, current_cache_file_path)
        logger.info("Cache files are merged and the result copied to game directory ")

    def _update_record(self, repo, new_size: int):
        if isinstance(new_size, int):
            self.records.update({repo: new_size})
    
    def _update_record_file(self):
        logger.info("Updating last downloaded dxvk cache file size record")
        try:
            with open(self.record_file_path, "w+") as record_file:
                toml.dump(self.records, record_file)
        except FileNotFoundError as e:
            logger.error(f"{self.record_file_path} is not found")
    
    def _get_repo_file_size(self, url: str) -> int|None:
        logger.info("Getting dxvk cache file size from github repo")
        try:
            handle = urlopen(url)
            return handle.length
        except HTTPError as e:
            logger.error(f"HTTP error, {url}")
            return None
        except URLError as e:
            logger.error(f"URL error, {url}")
            return None

def main():
    c=CacheMerger()
    c.check_update()

if __name__ == "__main__":
    main()