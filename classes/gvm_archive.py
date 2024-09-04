import shutil
from datetime import datetime
from pathlib import Path
from config import Config
from libraries import GVMLogger

class GVMArchive:
    def __init__(self, archive_path: Path | str, output_path: Path | str, logger: GVMLogger):
        self.archive_path: Path = Path(archive_path)
        self.output_path : Path = Path(output_path)
        self.__write_log : function = logger.write_log

        self.check_and_create_folder(self.archive_path)
    
    def check_and_create_folder(self, path: Path):
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            self.__write_log(f"Created missing directory: {path}", GVMLogger.INFO)

    def archive_output(self):
        
        if self.output_path.exists() and self.output_path.is_file():
            today_date = datetime.now().strftime("%Y%m%d")
            archive_file_name = f"{today_date}_scans"
            archive_file_path = self.archive_path / archive_file_name
            
        
            shutil.copy2(self.output_path, archive_file_path)
            self.__write_log(f"Archived scans file to: {archive_file_path}", GVMLogger.INFO)
            
        
            with open(self.output_path, 'w') as file:
                file.truncate(0)
            self.__write_log(f"Cleared content of file: {self.output_path}", GVMLogger.INFO)
        else:
            self.__write_log(f"No scans file found at: {self.output_path}", GVMLogger.WARNING)

if __name__ == "__main__":
    logger = GVMLogger(f"{Path(__file__).stem}.{GVMArchive.__qualname__}", Config.ARCHIVE_LOG_FILE)
    
    file_manager = GVMArchive(Config.ARCHIVE_PATH, Config.OUTPUT_PATH, logger)
    
    file_manager.archive_output()