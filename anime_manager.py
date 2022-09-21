import wx
import os
import pathlib
from resources.name_getter import NameGetter
from resources.anime_statistics import AnimeStatistics
from resources.folder_manager import FolderManager


class AniManaPanel(wx.Panel):

    __DESC_SIZE = (100, -1)
    __DESC_SIZE_WIDE = (205, -1)
    __TEXT_SIZE = (505, -1)
    __TEXT_SIZE_NARROW = (250, -1)
    __BUTTON_SIZE = (100, -1)
    __CHECKBOX_SIZE = (-1, -1)

    __DEFAULT_FOLDER_PATH = "Z:\System\Download"
    __DEFAULT_NAME_FILE_PATH = "Z:\System\Scripts\\resources"

    def __init__(self, parent):
        super().__init__(parent)

        self.name_getter = NameGetter()
        self.anime_stats = AnimeStatistics()
        self.folder_manager = FolderManager()

        self.current_folder_path = None
        self.current_name_file_path = self.__DEFAULT_NAME_FILE_PATH + '\\names.txt'
        self.episode_list_folder = list()
        self.episode_list_target = list()
        self.special_list_target = list()
        self.episode_list_combined = list()

        self.sizer_main = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer_main)

        self.folder_text = wx.TextCtrl(self, size=self.__TEXT_SIZE)
        self.anime_name_text = wx.TextCtrl(self, size=self.__TEXT_SIZE)
        self.subgroup_text = wx.TextCtrl(self, size=self.__TEXT_SIZE_NARROW)
        self.source_type_text = wx.TextCtrl(self, size=self.__TEXT_SIZE_NARROW)
        self.name_auto_text = wx.TextCtrl(self, size=self.__TEXT_SIZE)
        self.name_file_text = wx.TextCtrl(self, size=self.__TEXT_SIZE)
        self.rename_direct_text = wx.TextCtrl(self, size=self.__TEXT_SIZE)
        self.anime_name_replace_hyphen_check = wx.CheckBox(self, label='Hyphen style', size=self.__CHECKBOX_SIZE)
        self.anime_name_replace_year_check = wx.CheckBox(self, label='Remove year', size=self.__CHECKBOX_SIZE)
        self.name_auto_check = wx.CheckBox(self, label='Include Name', size=self.__CHECKBOX_SIZE)
        self.rename_episode_check = wx.CheckBox(self, label='Episode', size=self.__CHECKBOX_SIZE)
        self.rename_oped_check = wx.CheckBox(self, label='Opening/Ending', size=self.__CHECKBOX_SIZE)
        self.rename_ova_check = wx.CheckBox(self, label='OVA/OAD', size=self.__CHECKBOX_SIZE)
        self.rename_special_check = wx.CheckBox(self, label='Special', size=self.__CHECKBOX_SIZE)
        self.anime_listing = wx.ListCtrl(self, size=(1210, 600), style=wx.LC_REPORT | wx.BORDER_SUNKEN)

        self.create_controls()
        self.init_control_values()

        self.update_anime_listing()

    def create_controls(self):
        self.sizer_main.Add(self.create_folder_menu(), flag=wx.ALL, border=5)
        self.sizer_main.Add(self.create_anime_name_menu(), flag=wx.ALL, border=5)
        self.sizer_main.Add(self.create_subgroup_menu(), flag=wx.ALL, border=5)
        self.sizer_main.Add(self.create_name_auto_menu(), flag=wx.ALL, border=5)
        self.sizer_main.Add(self.create_name_file_menu(), flag=wx.ALL, border=5)
        self.sizer_main.Add(self.anime_listing, flag=wx.ALL, border=5)
        self.sizer_main.Add(self.create_rename_menu(), flag=wx.ALL, border=5)
        self.sizer_main.Add(self.create_rename_direct_menu(), flag=wx.ALL, border=5)

    def init_control_values(self):
        self.anime_name_replace_hyphen_check.SetValue(True)
        self.anime_name_replace_year_check.SetValue(True)
        self.name_auto_check.SetValue(True)
        self.rename_episode_check.SetValue(True)
        self.rename_oped_check.SetValue(True)
        self.rename_ova_check.SetValue(True)
        self.rename_special_check.SetValue(True)

    def create_action_button(self, parent, label, handler,
                             size=__BUTTON_SIZE, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5):
        button = wx.Button(self, label=label, size=size)
        button.Bind(event=wx.EVT_BUTTON, handler=handler, source=button)
        parent.Add(button, flag=flag, border=border)

    def create_line_desc(self, parent, label, size=__DESC_SIZE, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5):
        desc = wx.StaticText(self, label=label, size=size)
        parent.Add(desc, flag=flag, border=border)

    def create_folder_menu(self):
        sizer_folder = wx.BoxSizer(wx.HORIZONTAL)

        self.create_line_desc(sizer_folder, 'Folder Path')
        self.create_action_button(sizer_folder, 'Refresh Folder', self.action_refresh_folder)
        sizer_folder.Add(self.folder_text, flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.create_action_button(sizer_folder, 'Choose Folder', self.action_choose_folder)
        self.create_action_button(sizer_folder, 'Flatten Folder', self.action_flatten_folder)
        self.create_action_button(sizer_folder, 'Rename Folder', self.action_rename_folder)

        return sizer_folder

    def create_anime_name_menu(self):
        sizer_anime_name = wx.BoxSizer(wx.HORIZONTAL)

        self.create_line_desc(sizer_anime_name, 'Anime name')
        self.create_action_button(sizer_anime_name, 'Refresh Name', self.action_refresh_listing)
        sizer_anime_name.Add(self.anime_name_text, flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.create_action_button(sizer_anime_name, 'Replace Name', self.action_replace_anime_name)
        self.create_action_button(sizer_anime_name, 'Season Up', self.action_replace_anime_name_up)
        self.create_action_button(sizer_anime_name, 'Season Down', self.action_replace_anime_name_down)
        sizer_anime_name.Add(self.anime_name_replace_hyphen_check, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer_anime_name.Add(self.anime_name_replace_year_check, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5)

        return sizer_anime_name

    def create_subgroup_menu(self):
        sizer_subgroup = wx.BoxSizer(wx.HORIZONTAL)

        self.create_line_desc(sizer_subgroup, 'Sub Group', size=self.__DESC_SIZE_WIDE)
        sizer_subgroup.Add(self.subgroup_text, flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer_subgroup.Add(self.source_type_text, flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.create_action_button(sizer_subgroup, 'Parse Group', self.action_parse_subgroup)
        self.create_action_button(sizer_subgroup, 'Replace Group', self.action_replace_subgroup)

        return sizer_subgroup

    def create_name_auto_menu(self):
        sizer_name_auto = wx.BoxSizer(wx.HORIZONTAL)

        self.create_line_desc(sizer_name_auto, 'Anime ID', size=self.__DESC_SIZE_WIDE)
        sizer_name_auto.Add(self.name_auto_text, flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.create_action_button(sizer_name_auto, 'Load from API', self.action_load_episodes_from_api)
        sizer_name_auto.Add(self.name_auto_check, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5)

        return sizer_name_auto

    def create_name_file_menu(self):
        sizer_name_file = wx.BoxSizer(wx.HORIZONTAL)

        self.create_line_desc(sizer_name_file, 'Name File Path')
        self.create_action_button(sizer_name_file, 'Refresh File', self.action_update_target_list_from_file)
        sizer_name_file.Add(self.name_file_text, flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.create_action_button(sizer_name_file, 'Choose File', self.action_choose_name_file)

        return sizer_name_file

    def create_rename_menu(self):
        sizer_rename = wx.BoxSizer(wx.HORIZONTAL)

        self.create_line_desc(sizer_rename, 'Rename Options', size=self.__DESC_SIZE_WIDE)
        sizer_rename.Add(self.rename_episode_check, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer_rename.Add(self.rename_oped_check, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer_rename.Add(self.rename_ova_check, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer_rename.Add(self.rename_special_check, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.create_action_button(sizer_rename, 'Rename', self.action_rename_apply)
        self.create_action_button(sizer_rename, 'Clean', self.action_clean_folder)
        self.create_action_button(sizer_rename, 'Transition', self.action_transition_folder)

        return sizer_rename

    def create_rename_direct_menu(self):
        sizer_rename_direct = wx.BoxSizer(wx.HORIZONTAL)

        self.create_line_desc(sizer_rename_direct, 'Rename Directly', size=self.__DESC_SIZE_WIDE)
        sizer_rename_direct.Add(self.rename_direct_text, flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.create_action_button(sizer_rename_direct, 'Rename Select', self.action_rename_indirect)

        return sizer_rename_direct

    def action_choose_folder(self, event):
        title = "Choose a folder:"
        dlg = wx.DirDialog(self, title, style=wx.DD_DEFAULT_STYLE)
        dlg.SetPath(self.__DEFAULT_FOLDER_PATH)
        if dlg.ShowModal() == wx.ID_OK:
            self.current_folder_path = dlg.GetPath()
            self.update_folder_list()
            self.folder_text.SetValue(self.current_folder_path)
        dlg.Destroy()

    def action_refresh_folder(self, event):
        self.current_folder_path = self.folder_text.GetValue()
        self.update_folder_list()

    def action_flatten_folder(self, event):
        self.folder_manager.move_all_files_to_main_folder(self.current_folder_path)
        self.update_folder_list()

    def action_rename_folder(self, event):
        new_name = self.folder_manager.rename_folder(
            self.current_folder_path, f"{self.anime_name_text.GetValue()} [{self.subgroup_text.GetValue()}]")
        self.current_folder_path = new_name
        self.folder_text.SetValue(new_name)
        self.update_folder_list()

    def update_folder_list(self):
        self.episode_list_folder = self.name_getter.get_anime_episodes_from_folder(self.current_folder_path,
                                                                                   self.anime_name_text.GetValue())
        self.update_combined_list()

    def action_load_episodes_from_api(self, event):
        self.update_target_list("api")

    def action_choose_name_file(self, event):
        title = "Choose a text file:"
        dlg = wx.FileDialog(self, title, style=wx.DD_DEFAULT_STYLE, wildcard="TXT files (*.txt)|*.txt")
        dlg.SetDirectory(self.__DEFAULT_NAME_FILE_PATH)
        if dlg.ShowModal() == wx.ID_OK:
            self.current_name_file_path = dlg.GetPath()
            self.update_target_list("file")
            self.name_file_text.SetValue(self.current_name_file_path)
        dlg.Destroy()

    def action_update_target_list_from_file(self, event):
        self.update_target_list("file")

    def update_target_list(self, source):
        if source == "file":
            self.episode_list_target = self.name_getter.get_anime_episodes_from_file(self.current_name_file_path)
        elif source == "api":
            self.episode_list_target, self.special_list_target, anime_name = \
                self.name_getter.get_anime_episodes_from_api(self.name_auto_text.GetValue())
            if self.name_auto_check.GetValue():
                self.anime_name_text.SetValue(anime_name)
        self.update_combined_list()

    def action_refresh_listing(self, event):
        self.update_combined_list()

    def action_replace_anime_name(self, event):
        self.replace_anime_name()

    def action_replace_anime_name_up(self, event):
        self.replace_anime_name(1)

    def action_replace_anime_name_down(self, event):
        self.replace_anime_name(-1)

    def replace_anime_name(self, count=0):
        self.anime_name_text.SetValue(
            self.name_getter.replace_anime_name(
                self.anime_name_text.GetValue(), self.anime_name_replace_hyphen_check.GetValue(),
                self.anime_name_replace_year_check.GetValue(), count))
        self.update_combined_list()

    def action_replace_subgroup(self, event):
        self.subgroup_text.SetValue(self.name_getter.replace_special_characters(self.subgroup_text.GetValue()))

    def action_parse_subgroup(self, event):
        self.subgroup_text.SetValue(self.name_getter.parse_subgroup(self.folder_text.GetValue()))

    def action_transition_folder(self, event):
        new_name = self.anime_name_text.GetValue() + " [" + self.subgroup_text.GetValue() + "]"
        self.current_folder_path = self.folder_manager.create_folder_with_icon(
            self.current_folder_path, self.source_type_text.GetValue().upper(), new_name)
        self.folder_text.SetValue(self.current_folder_path)

    def action_clean_folder(self, event):
        new_list = list()
        for file in self.episode_list_combined:
            if file["type"] == "DEL":
                os.remove(file["path"])
            else:
                new_list.append(file)
        self.update_folder_list()
        self.episode_list_combined = new_list
        self.update_anime_listing()

    def update_combined_list(self):
        anime_name = self.anime_name_text.GetValue()
        self.episode_list_combined = list()
        for epf in self.episode_list_folder:
            ep = dict()
            ep["file_name"] = epf["file_name"]
            ep["path"] = epf["path"]
            ep["type"] = epf["type"]
            ep["id"] = epf["id"]
            ep["eid"] = epf["eid"]
            if anime_name:
                if epf["type"] == "EP" and len(self.episode_list_target) >= epf["id"]:
                    ep["target_name"] = anime_name + " " + epf["eid"] + " - " + \
                                        self.episode_list_target[epf["id"]-1] + pathlib.Path(epf["file_name"]).suffix
                elif epf["type"] and epf["type"] != "SKIP":
                    ep["target_name"] = anime_name + " " + epf["eid"] + pathlib.Path(epf["file_name"]).suffix
                else:
                    ep["target_name"] = epf["file_name"]
            else:
                ep["target_name"] = epf["file_name"]
            self.episode_list_combined.append(ep)
        self.update_anime_listing()

    def update_anime_listing(self):
        default_width_name = 500
        default_width_short = 100
        default_width_narrow = 50
        self.anime_listing.ClearAll()
        self.anime_listing.InsertColumn(0, 'File name', width=default_width_name)
        self.anime_listing.InsertColumn(1, 'Type', width=default_width_narrow)
        self.anime_listing.InsertColumn(2, 'ID', width=default_width_narrow)
        self.anime_listing.InsertColumn(3, 'EID', width=default_width_short)
        self.anime_listing.InsertColumn(4, 'Target Name', width=default_width_name)
        index = 0
        for ep in self.episode_list_combined:
            self.anime_listing.InsertItem(index, ep["file_name"])
            self.anime_listing.SetItem(index=index, column=1, label=ep["type"])
            self.anime_listing.SetItem(index=index, column=2, label=str(ep["id"]))
            self.anime_listing.SetItem(index=index, column=3, label=ep["eid"])
            self.anime_listing.SetItem(index=index, column=4, label=ep["target_name"])
            index += 1

    def action_rename_apply(self, event):
        self.rename_apply()

    def action_rename_indirect(self, event):
        self.rename_apply_direct(self.anime_listing.GetFocusedItem(), self.rename_direct_text.GetValue(), False)

    def rename_apply(self):
        include_ep = self.rename_episode_check.GetValue()
        include_oped = self.rename_oped_check.GetValue()
        include_ova = self.rename_ova_check.GetValue()
        include_special = self.rename_special_check.GetValue()

        for file in self.episode_list_combined:
            if (include_ep and file["type"] == "EP") or \
               (include_oped and file["type"] in ["OP", "ED"]) or \
               (include_ova and file["type"] in ["OVA", "ONA", "OAD"]) or \
               (include_special and file["type"] in ["Special", "Extra", "SP"]):
                source = os.path.join(self.current_folder_path, file["file_name"])
                target = os.path.join(self.current_folder_path, file["target_name"])
                print("From: " + file["file_name"])
                print("To  : " + file["target_name"] + "\n")
                try:
                    os.rename(source, target)
                except Exception as err:
                    print("Failed " + target)
                    print(err)
        self.update_folder_list()

    def rename_apply_direct(self, item_id, new_name, direct):
        if item_id >= 0 and new_name:
            if direct:
                pass
            else:
                self.episode_list_combined[item_id]["type"] = "SP"
                self.episode_list_combined[item_id]["id"] = ""
                self.episode_list_combined[item_id]["eid"] = ""
                self.episode_list_combined[item_id]["target_name"] = self.anime_name_text.GetValue() + " " + new_name
            self.update_anime_listing()


class AnimeManager(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title='Anime Manager')
        self.Maximize(True)
        self.panel = AniManaPanel(self)
        self.Show()


if __name__ == '__main__':
    try:
        app = wx.App(False)
        frame = AnimeManager()
        app.MainLoop()
    except Exception as e:
        input(e)
