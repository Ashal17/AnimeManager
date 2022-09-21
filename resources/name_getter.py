import os
import codecs
import re
import requests
from xml.etree import ElementTree
from operator import itemgetter
from api_config import API


class NameGetter:

    __REPLACER = [["/", "⁄"], ["?", "？"], [": ", "："], [":", "："], ['"', "'"], ["`", "'"], ["<", "＜"], [">", "＞"],
                  ["*", "✱"], ["\\", "＼"]]
    __REPLACER_HYPHEN = [["/", "⁄"], ["?", "？"], [": ", " - "], [":", " - "], ['"', "'"], ["`", "'"], ["<", "＜"],
                         [">", "＞"], ["*", "✱"], ["\\", "＼"]]
    __VIDEO_FILE = ['.mkv', '.avi', '.mp4']
    __SUBFILES = ['.ass', '.srt', '.ssa', '.sup']
    __ENDING = ['NCED', ' ED', '_ED', 'Clean Ending', 'Ending']
    __OPENING = ['NCOP', ' OP', '_OP', 'Clean Opening', 'Opening']
    __OTHER = ['OVA', 'ONA', 'OAD', 'Special', 'Extra', 'SP']
    __SKIP = ['E00 ']
    __REGEX_ROMAN_NUMERALS = r' ?M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$'
    __REGEX_YEAR = r'\(\d+\)'
    __REGEX_SUBGROUP = r'(?<=\[)(.*?)(?=\])'
    __CLIENT = API.CLIENT
    __CLIENT_VER = API.CLIENT_VER
    __NAMESPACES = API.NAMESPACES

    def __init__(self):
        self.roman_numerals = RomanNumerals()

    @staticmethod
    def __return_regex_group(regex, string, grp=None, default=""):
        regex_result = re.search(regex, string, re.IGNORECASE)
        if regex_result:
            if grp:
                return regex_result.group(grp)
            else:
                return regex_result.group()
        else:
            return default

    def replace_special_characters(self, input_obj, output_key="name", replacer=None):
        if replacer is None:
            replacer = self.__REPLACER
        if isinstance(input_obj, list):
            output = list()
            for ep in input_obj:
                output.append(self.replace_special_characters(ep))
            return output
        elif isinstance(input_obj, str):
            input_obj = input_obj.strip()
            for rep in replacer:
                input_obj = input_obj.replace(rep[0], rep[1])
            return input_obj
        elif isinstance(input_obj, dict):
            return self.replace_special_characters(input_obj[output_key])

    def __check_special(self, anime_name, source):
        for ending in self.__ENDING:
            if ending in source:
                num = re.search(ending + " *-* *0*([a-zA-Z0-9]+)", source)
                if num:
                    return "ED", "Ending " + num.group(1), num.group(1)
                else:
                    return "ED", "Ending", None
        for opening in self.__OPENING:
            if opening in source:
                num = re.search(opening + " *-* *0*([a-zA-Z0-9]+)", source)
                if num:
                    return "OP", "Opening " + num.group(1), num.group(1)
                else:
                    return "OP", "Opening", None
        for other in self.__OTHER:
            if not (not (other in source) or other in anime_name):
                num = re.search(other + " *-* *0*([a-zA-Z0-9]+)", source)
                if num:
                    return other, other + " " + num.group(1), num.group(1)
                else:
                    return other, other, None
        for skip in self.__SKIP:
            if not (not (skip in source) or skip in anime_name):
                return "SKIP", skip, None
        return False, False, False

    def __check_special_simple(self, anime_name, source):
        for ending in self.__ENDING:
            if ending in source:
                return True
        for opening in self.__OPENING:
            if opening in source:
                return True
        for other in self.__OTHER:
            if not (not (other in source) or other in anime_name):
                return True
        for skip in self.__SKIP:
            if not (not (skip in source) or skip in anime_name):
                return True
        return False

    def __check_type(self, source):
        if os.path.isfile(source):
            if source[-4:] in self.__VIDEO_FILE:
                return "VIDEO"
            elif source[-4:] in self.__SUBFILES:
                return "SUB"
            else:
                return "NONE"
        elif os.path.isdir(source):
            return "DIR"
        else:
            return "NONE"

    @staticmethod
    def __get_episode_id(cur, total):
        if total > 99:
            if cur < 10:
                return "E00" + str(cur)
            elif cur < 100:
                return "E0" + str(cur)
            else:
                return "E" + str(cur)
        else:
            if cur < 10:
                return "E0" + str(cur)
            else:
                return "E" + str(cur)

    def __get_episode_count(self, files, anime_name):
        count = 0
        for file in files:
            if not self.__check_special_simple(anime_name, file):
                if self.__check_type(file) == "VIDEO":
                    count += 1
        return count

    def replace_anime_name(self, anime_name, hyphen_replacer, remove_year, count=0):
        if hyphen_replacer:
            replacer = self.__REPLACER_HYPHEN
        else:
            replacer = self.__REPLACER
        if remove_year:
            anime_name = re.sub(self.__REGEX_YEAR, '', anime_name)
        anime_name = self.replace_special_characters(anime_name, replacer=replacer)
        anime_name.strip()
        if count != 0:
            roman_num = re.search(self.__REGEX_ROMAN_NUMERALS, anime_name)
            if roman_num:
                anime_name = re.sub(self.__REGEX_ROMAN_NUMERALS, '', anime_name)
                result_roman = self.roman_numerals.add_int_to_roman(roman_num.group(), count)
            else:
                result_roman = "I"
            anime_name = anime_name + " " + result_roman
        return anime_name

    def parse_subgroup(self, text):
        return self.__return_regex_group(self.__REGEX_SUBGROUP, text, 1)

    def get_anime_episodes_from_folder(self, folder, anime_name=""):
        files = os.listdir(folder)
        files.sort()
        episodes = list()
        if len(files):
            i_vid = 0
            i_sub = 0
            episode_count = self.__get_episode_count(files, anime_name)
            for file in files:
                path = os.path.join(folder, file)
                file_type = self.__check_type(path)
                episode = dict()
                episode["file_name"] = file
                episode["path"] = path
                if file_type == "NONE":
                    episode["type"] = "DEL"
                    episode["id"] = ""
                    episode["eid"] = "NONE"
                elif file_type == "DIR":
                    episode["type"] = "SKIP"
                    episode["id"] = ""
                    episode["eid"] = "DIR"
                else:
                    special_type, special_eid, special_id = self.__check_special(anime_name, file)
                    if special_type:
                        episode["type"] = special_type
                        episode["id"] = special_id
                        episode["eid"] = special_eid
                    else:
                        if file_type == "VIDEO":
                            i_vid += 1
                            i = i_vid
                        elif file_type == "SUB":
                            i_sub += 1
                            i = i_sub
                        episode["type"] = "EP"
                        episode["id"] = i
                        episode["eid"] = self.__get_episode_id(i, episode_count)
                episodes.append(episode)
        episodes = sorted(episodes, key=itemgetter('eid'))
        return episodes

    def get_anime_episodes_from_file(self, filename='names.txt'):
        with codecs.open(filename, encoding='utf-8') as n:
            lines = n.readlines()
        episodes = list()
        for line in lines:
            if re.search('[a-zA-Z]', line):
                split = line.split("\t")
                for s in split:
                    if re.search('[a-zA-Z]', s):
                        episodes.append(s)
                        break
        return self.replace_special_characters(episodes)

    def __get_url(self, anime_id, url_type):
        if url_type == "api":
            return f"http://api.anidb.net:9001/httpapi?request=anime&client={self.__CLIENT}" \
                   f"&clientver={str(self.__CLIENT_VER)}&protover=1&aid={anime_id}"
        elif url_type == "html":
            return f"https://anidb.net/anime/{anime_id}"

    def get_anime_episodes_from_api(self, anime_id):
        response = requests.get(self.__get_url(anime_id, "api"))
        tree = ElementTree.fromstring(response.content)
        title = tree.find(".//titles/title[@type='main']")
        episodes_xml = tree.findall(".//episodes/episode")
        episodes = list()
        specials = list()
        for episode_xml in episodes_xml:
            episode_id = episode_xml.find("epno")
            if episode_id.attrib["type"] == '1':
                episode = dict()
                episode["id"] = int(episode_id.text)
                episode["name"] = episode_xml.find("title[@xml:lang='en']", namespaces=self.__NAMESPACES).text
                episodes.append(episode)
            elif episode_id.attrib["type"] == '2':
                special = dict()
                special["id"] = episode_id.text
                special["name"] = episode_xml.find("title[@xml:lang='en']", namespaces=self.__NAMESPACES).text
                specials.append(special)
        episodes = sorted(episodes, key=itemgetter('id'))
        specials = sorted(specials, key=itemgetter('id'))
        return self.replace_special_characters(episodes), self.replace_special_characters(specials), title.text


class RomanNumerals:

    __ROMAN = ["I", "IV", "V", "IX", "X", "XL", "L", "XC", "C", "CD", "D", "CM", "M"]
    __INT = [1, 4, 5, 9, 10, 40, 50, 90, 100, 400, 500, 900, 1000]

    def __init__(self):
        pass

    def convert_roman_to_int(self, roman):
        i = 0
        num = 0
        roman = roman.strip()
        while i < len(roman):
            if i + 1 < len(roman) and roman[i:i + 2] in self.__ROMAN:
                num += self.__INT[self.__ROMAN.index(roman[i:i + 2])]
                i += 2
            else:
                num += self.__INT[self.__ROMAN.index(roman[i])]
                i += 1
        return num

    def convert_int_to_roman(self, number):
        i = 12
        roman = ""
        while number:
            div = number // self.__INT[i]
            number %= self.__INT[i]

            while div:
                roman += self.__ROMAN[i]
                div -= 1
            i -= 1
        return roman

    def add_int_to_roman(self, roman, number):
        roman_int = self.convert_roman_to_int(roman)
        roman_int += number
        if roman_int <= 1:
            roman_int = 1
        return self.convert_int_to_roman(roman_int)
