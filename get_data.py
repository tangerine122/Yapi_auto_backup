# -*- coding: utf-8 -*-
# !/usr/bin/python3
# __author__ = "liyi"
# DATE: 2019/11/18
import requests
import json
import datetime
import subprocess
import os
from logger import get_logger
from config import BaseConfig
logger = get_logger()
current_path = os.path.abspath(__file__)
father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")
COMMAND_RUN_GIT = """
cd {}
git add .
git commit -m "auto push at {}"
git push
""".format(father_path, str(datetime.datetime.now()))


class ExportYapiApi(BaseConfig):

    current_path = os.path.abspath(__file__)
    father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")

    def __init__(self, project_name):
        self.project_name = project_name
        self.global_url = self.YAPI_URL + "/api/interface/{param}?token={token}&"

    def get_requests(self, param, token, **kwargs):
        some_param = ''
        if kwargs:
            for k, v in kwargs.items():
                some_param += '{}={}&'.format(k, v)
        res = requests.get(self.global_url.format(param=param, token=token) + some_param)
        res_json = res.json()
        return res_json

    def get_file_name(self):
        today = datetime.date.today()
        formatted_today = today.strftime('%Y%m%d')
        return self.project_name + "-" + formatted_today

    def check_execution(self):
        dirs = self.father_path + '/{}'.format(self.project_name)
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        file_list = []
        for filename in os.listdir(r'{}/{}'.format(self.father_path, self.project_name)):
            file_list.append(filename)
        if not file_list:
            return True
        file_list.sort(reverse=True)
        new_date = file_list[0].split('.')[0].split('-')[-1]
        logger.debug(new_date)
        new_date_obj = datetime.datetime.strptime(new_date, '%Y%m%d')
        now_date = datetime.datetime.now()
        diff_date = now_date - new_date_obj
        logger.debug(diff_date.days)
        if diff_date.days >= self.INTERVAL_DAY:
            return True
        else:
            return False

    def save_json_file(self, json_data):
        with open(self.father_path + "/{}/{}.json".format(self.project_name, self.get_file_name()), 'w') as f:
            f.write(json.dumps(json_data, indent=4, separators=(',', ':'), ensure_ascii=False))

    def export_api(self):
        if self.project_name == 'sidekick':
            token = self.token_sidekick
        elif self.project_name == 'wms':
            token = self.token_wms
        else:
            logger.error("项目名错误！！")
            return
        if not self.check_execution():
            logger.warning("上次导出时间未超过{}天，暂不用导出".format(self.INTERVAL_DAY))
            return
        res_json = self.get_requests(self.LIST_MENU, token)
        all_api = res_json.get(self.DATA)
        all_data = []
        for api in all_api:
            api_list = api.get(self.LIST)
            api_info_list = []
            for apii in api_list:
                api_id = apii.get(self._ID)
                apii_json = self.get_requests(self.GET, token, **{'id': api_id})
                api_info_list.append(apii_json.get(self.DATA))
            api[self.LIST] = api_info_list
            all_data.append(api)
        self.save_json_file(all_data)
        logger.debug(all_data)
        logger.info("导出成功！！")
        return


if __name__ == '__main__':
    ExportYapiApi('wms').export_api()
    ExportYapiApi('sidekick').export_api()
    # subprocess.call(["git", "clone", ""])
    # subprocess.call(["git", "add", "/home/boocax/yapi/Yapi_AutoBackup/."])
    # subprocess.call(["git", "commit", "-m", "auto push at " + str(datetime.datetime.now())])     # 加上当前系统的时间
    # subprocess.call(["git", "push"])
    subprocess.call(COMMAND_RUN_GIT, shell=True)    





