# MIT License

# Copyright (c) 2017-2021 UlionTse

# Warning: Prohibition of commercial use!
# This module is designed to help students and individuals with translation services.
# For commercial use, please purchase API services from translation suppliers.

# Don't make high frequency requests!
# Enterprises provide free services, we should remain grateful, not cause trouble.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software. You may obtain a copy of the
# License at

#     https://github.com/uliontse/translators/blob/master/LICENSE

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Union

import lxml.etree
import requests
import js2py
import time
import random
import urllib
import re


class TranslatorSeverRegion:
    @property
    def request_server_region_info(self):
        try:
            ip_address = requests.get('http://httpbin.org/ip').json()['origin']
            try:
                data = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=10).json()
                return data
            except requests.exceptions.Timeout:
                data = requests.post(
                    url='http://ip.taobao.com/outGetIpInfo',
                    data={'ip': ip_address, 'accessKey': 'alibaba-inc'}
                ).json().get('data')
                data.update({'countryCode': data.get('country_id')})
                return data

        except requests.exceptions.ConnectionError:
            raise Exception('Unable to connect the Internet.\n')
        except:
            raise Exception('Unable to find server backend.\n')


REQUEST_SERVER_REGION_INFO = TranslatorSeverRegion().request_server_region_info


def get_headers(host_url, if_api=False, if_referer_for_host=True, if_ajax_for_api=True, if_json_for_api=False):
    url_path = urllib.parse.urlparse(host_url).path
    user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/55.0.2883.87 Safari/537.36"
    host_headers = {
        'Referer' if if_referer_for_host else 'Host': host_url,
        "User-Agent": user_agent,
    }
    api_headers = {
        'Origin': host_url.split(url_path)[0] if url_path else host_url,
        'Referer': host_url,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        "User-Agent": user_agent,
    }
    if if_api and not if_ajax_for_api:
        api_headers.pop('X-Requested-With')
        api_headers.update({'Content-Type': 'text/plain'})
    if if_api and if_json_for_api:
        api_headers.update({'Content-Type': 'application/json'})
    return host_headers if not if_api else api_headers


def check_language(from_language, to_language, language_map, output_zh=None, output_auto='auto'):
    from_language = output_auto if from_language in ('auto', 'auto-detect') else from_language
    from_language = output_zh if output_zh and from_language in ('zh', 'zh-CN', 'zh-CHS', 'zh-Hans') else from_language
    to_language = output_zh if output_zh and to_language in ('zh', 'zh-CN', 'zh-CHS', 'zh-Hans') else to_language

    if from_language != output_auto and from_language not in language_map:
        raise Exception('Unsupported from_language[{}] in {}.'.format(from_language, sorted(language_map.keys())))
    elif to_language not in language_map:
        raise Exception('Unsupported to_language[{}] in {}.'.format(to_language, sorted(language_map.keys())))
    elif from_language != output_auto and to_language not in language_map[from_language]:
        raise Exception('Unsupported translation: from [{0}] to [{1}]!'.format(from_language, to_language))
    return from_language, to_language


def check_query_text(query_text, if_ignore_limit_of_length=False):
    if not isinstance(query_text, str):
        raise Exception('query_text is not string.')
    query_text = query_text.strip()
    if not query_text:
        return ''
    length = len(query_text)
    if length > 5000 and not if_ignore_limit_of_length:
        raise Exception('The length of the text to be translated exceeds the limit.')
    else:
        return query_text


class Bing():
    def __init__(self):
        self.host_url = None
        self.cn_host_url = 'https://cn.bing.com/Translator'
        self.en_host_url = 'https://www.bing.com/Translator'
        self.request_server_region_info = REQUEST_SERVER_REGION_INFO
        self.api_url = None
        self.host_headers = None
        self.api_headers = None
        self.host_info = None
        self.tk = None
        self.first_time = int(time.time())
        self.language_map = None
        self.query_count = 0
        self.output_auto = 'auto-detect'
        self.output_zh = 'zh-Hans'

    def get_host_info(self, host_html):
        et = lxml.etree.HTML(host_html)
        lang_list = et.xpath('//*[@id="tta_srcsl"]/option/@value') or et.xpath('//*[@id="t_srcAllLang"]/option/@value')
        lang_list = list(set(lang_list))
        if self.output_auto in lang_list:
            lang_list.remove(self.output_auto)
        language_map = {}.fromkeys(lang_list, lang_list)
        iid = et.xpath('//*[@id="rich_tta"]/@data-iid')[0] + '.' + str(self.query_count + 1)
        ig = re.compile('IG:"(.*?)"').findall(host_html)[0]
        return {'iid': iid, 'ig': ig, 'language_map': language_map}

    def get_tk(self, host_html):
        result_str = re.compile('var params_RichTranslateHelper = (.*?);').findall(host_html)[0]
        result = js2py.eval_js(result_str)
        return {'key': result[0], 'token': result[1]}

    def _bing_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en', **kwargs) -> Union[str, list]:
        """
        https://bing.com/Translator, https://cn.bing.com/Translator.
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param if_use_cn_host: boolean, default None.
                :param if_ignore_limit_of_length: boolean, default False.
                :param is_detail_result: boolean, default False.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default `random.random()`.
        :return: str or list
        """
        use_cn_condition = kwargs.get('if_use_cn_host', None) or self.request_server_region_info.get('countryCode') == 'CN'
        self.host_url = self.cn_host_url if use_cn_condition else self.en_host_url
        self.api_url = self.host_url.replace('Translator', 'ttranslatev3')
        self.host_headers = get_headers(self.host_url, if_api=False)
        self.api_headers = get_headers(self.host_url, if_api=True)
        is_detail_result = kwargs.get('is_detail_result', False)
        proxies = kwargs.get('proxies', None)
        sleep_seconds = kwargs.get('sleep_seconds', random.random())
        if_ignore_limit_of_length = kwargs.get('if_ignore_limit_of_length', False)
        query_text = check_query_text(query_text, if_ignore_limit_of_length)
        if not query_text:
            return ''

        with requests.Session() as ss:
            host_html = ss.get(self.host_url, headers=self.host_headers, proxies=proxies).text
            self.host_info = self.get_host_info(host_html)

            if not self.language_map:
                self.language_map = self.host_info.get('language_map')
            from_language, to_language = check_language(from_language, to_language, self.language_map,
                                                        output_zh=self.output_zh, output_auto=self.output_auto)
            # params = {'isVertical': '1', '': '', 'IG': self.host_info['ig'], 'IID': self.host_info['iid']}
            self.api_url = self.api_url + '?isVertical=1&&IG={}&IID={}'.format(self.host_info['ig'], self.host_info['iid'])

            if not self.tk or time.time() - self.first_time > 3500:  # 3600
                self.tk = self.get_tk(host_html)
            form_data = {
                'text': query_text,
                'fromLang': from_language,
                'to': to_language,
            }
            form_data.update(self.tk)
            r = ss.post(self.api_url, headers=self.host_headers, data=form_data, proxies=proxies)
            r.raise_for_status()
            data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data[0]['translations'][0]['text']

    def translate(self, query_text: str, from_language: str = 'auto', to_language: str = 'en'):
        return self._bing_api(query_text, from_language, to_language)


if __name__ == '__main__':
    tra = Bing()
    print(tra.translate('This a test', 'en', 'fr'))
