import os
import json
import glob
import traceback
import pandas as pd
from copy import deepcopy


def parse_author_info(aweme_info: dict):
    author_info = aweme_info['author']
    info_key_list = ["uid", "nickname", "signature", "custom_verify"]
    return {key: author_info[key] if key in author_info else '' for key in info_key_list}


def parse_statistic_info(aweme_info: dict):
    return deepcopy(aweme_info['statistics'])


def parse_video_info(aweme_info: dict):
    video_info = {}
    video_info["download_addr"] = deepcopy(aweme_info["video"]["download_addr"]["url_list"])
    video_info["play_addr"] = deepcopy(aweme_info["video"]["play_addr"]["url_list"])
    return video_info


def parse_aweme_info(aweme_info: dict):
    parse_func_list = [parse_author_info, parse_statistic_info]
    result = {}
    result["aweme_id"] = aweme_info["aweme_id"]
    result["create_time"] = aweme_info["create_time"]
    result["desc"] = aweme_info["desc"]
    for parse_func in parse_func_list:
        result.update(parse_func(aweme_info))
    return result

def main():
    data_path = "D:/pythonpro/crawls/data"
    aweme_info_list = []
    aweme_id_set = set()
    for path in glob.glob(data_path + "/*.json"):
        with open(path, 'r', encoding="utf-8") as f:
            try:
                json_data = json.load(f)
                if "data" in json_data:
                    data_list = json_data["data"]
                    for entry in data_list:
                        if "aweme_info" in entry:
                            aweme_info = entry["aweme_info"]
                            if "rawdata" in aweme_info and aweme_info["rawdata"]:
                                rawinfo = json.loads(aweme_info["rawdata"])
                                print(rawinfo)
                                continue
                            res = parse_aweme_info(aweme_info)
                            if res['aweme_id'] not in aweme_id_set:
                                aweme_info_list.append(res)
                                aweme_id_set.add(res['aweme_id'])
            except:
                print(path)
                traceback.print_exc()
    df = pd.DataFrame(aweme_info_list)
    df.to_csv(data_path + "/douyin.csv", index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    main()
