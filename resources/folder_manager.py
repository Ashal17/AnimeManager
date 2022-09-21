import os
import shutil


class FolderManager:

    __PRESET_FOLDER_SRC = "Z:\System\Icons\Preset folders\\folder_"
    __PRE_CREATED_FOLDER_SRC = "Z:\System\Icons\Precreated folders"
    __TRANSITION_FOLDER = "Z:\System\Transition"
    __SOURCE_TYPES = ["BD", "DVD", "TV", "WEB", "VHS"]

    @staticmethod
    def __get_all_files_in_sub_folder(folder_path):
        result = list()
        for path, sub_dirs, files in os.walk(folder_path):
            if path != folder_path:
                for name in files:
                    fullpath = os.path.join(path, name)
                    print(fullpath)
                    result.append(fullpath)
        return result

    def __delete_empty_sub_folders(self, folder_path):
        files = os.listdir(folder_path)
        if len(files) > 0:
            for file in files:
                path = os.path.join(folder_path, file)
                if os.path.isdir(path):
                    self.__delete_empty_sub_folders(path)
        elif len(files) == 0:
            os.rmdir(folder_path)

    def move_all_files_to_main_folder(self, folder_path):
        files = self.__get_all_files_in_sub_folder(folder_path)
        for file in files:
            shutil.move(file, folder_path)
        self.__delete_empty_sub_folders(folder_path)

    @staticmethod
    def rename_folder(path, new_name):
        new_path = path.rsplit("\\", 1)[0] + "\\" + new_name
        os.rename(path, new_path)
        return new_path

    def __create_empty_folder_with_icon(self, folder_name, source_type):
        source_folder = os.path.join(self.__PRE_CREATED_FOLDER_SRC, source_type)
        print("Folder count: " + str(len(os.listdir(source_folder))))
        pre_created_folder = os.listdir(source_folder)[0]
        source = os.path.join(source_folder, pre_created_folder)
        target = os.path.join(self.__TRANSITION_FOLDER, folder_name)
        shutil.move(source, target)
        return target

    def create_folder_with_icon(self, folder, source_type, new_name=False):
        if source_type in self.__SOURCE_TYPES:
            if new_name:
                folder_name = new_name
            else:
                folder_name = folder.split("\\")[-1]
            destination = self.__create_empty_folder_with_icon(folder_name, source_type)
            for file_name in os.listdir(folder):
                shutil.move(os.path.join(folder, file_name), destination)
            os.rmdir(folder)
            return destination
        else:
            print("Not a valid source type")
            return folder
