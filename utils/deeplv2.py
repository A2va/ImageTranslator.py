# MIT License

# Copyright (c) 2020 ffreemt

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE
# https://github.com/ffreemt/deepl-tr-async

from typing import Any, List, Optional, Tuple, Union

# import os

import asyncio
from timeit import default_timer
from urllib.parse import quote

from pyppeteer import launch
from pyquery import PyQuery as pq


import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)

stdout_handler = logging.StreamHandler(sys.stdout)
log.addHandler(stdout_handler)
# output_file_handler = logging.FileHandler("latest.log")
# log.addHandler(output_file_handler)


URL = r"https://www.deepl.com/translator"
LOOP = asyncio.get_event_loop()

HEADFUL=1
DEBUG=0
PROXY = ""
LOOP = asyncio.get_event_loop()
class DeepL:
    def __init__(self,text,dest_lang,src_lang):
        self.src_lang=src_lang
        self.dest_lang=dest_lang
        self.text=text

    async def get_ppbrowser(self):
        """ get a puppeeter browser.
        headless=not HEADFUL; proxy: str = PROXY
        """
        try:
            browser = await launch(
                args=[
                    "--disable-infobars",
                    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
                    "--window-size=1440x900",
                    "--disable-popup-blocking",  #
                ],
                # autoClose=False,
                headless=1,
                dumpio=True,
            )
        except Exception as exc:
            log.error("get_ppbrowser exc: %s", exc)
            raise
        return browser

    async def deepl_tr_async(
            self,
            text: str,
            from_lang: str = "auto",
            to_lang: str = "auto",
            waitfor: Optional[float] = None,
    ) -> Optional[str]:
        """ deepl via pyppeteer
        from_lang = 'de'
        to_lang = 'en'
        debug = 1
        """
        then = default_timer()
        count = 0
        while count < 3:
            count += 1
            try:
                page = await self.browser.newPage()
                break
            except Exception as exc:
                log.error(f"browser.newPage exc: {exc}, failed attempt: {count}")
                await asyncio.sleep(0)
        else:
            return


        page.setDefaultNavigationTimeout(0)

        url_ = f"{URL}#{self.src_lang}/{self.dest_lang}/{quote(text)}"
        # url_ = f'{URL}#{from_lang}/{to_lang}/'

       

        count = 0
        while count < 3:
            count += 1
            try:
                await page.goto(url_, {"timeout": 90 * 1000})
                break
            except Exception as exc:
                await syncio.sleep(0)
                page = await self.browser.newPage()
                log.warning(f"page.goto exc: {str(exc)}, attempt {count}")
        else:
            # return
            raise Exception(f"Unable to fetch {url_[:20]}...")

        # wait for input area ".lmt__source_textarea"
        try:
            # await page.waitFor(".lmt__message_box2__content")
            await page.waitForSelector(".lmt__source_textarea", {"timeout": 1000})  # ms
            log.debug("Succes getting source textarea")
        # except TimeoutError:
        except Exception as exc:
            await asyncio.sleep(0.5)
            # raise

        log.debug(f"page.goto(url_) time: {default_timer() - then } s")
        then = default_timer()

        # .lmt__message_box2__content

        # await page.waitFor(2500)  # ms

        # wait for popup to be visible
        _ = """
        try:
            # await page.waitFor(".lmt__message_box2__content")
            await page.waitForSelector(".lmt__message_box2__content", {"timeout": 1000})  # ms
        # except TimeoutError:
        except Exception as exc:
            if debug:
                logger.error("Timedout: %s, waiting for 500 ms more", exc)
            await asyncio.sleep(0.5)
            # raise
        """

        if waitfor is None:
            _ = max(100, len(text) * 3.6)
            logging.debug(f"waiting for {_} ms")
        else:
            try:
                _ = float(waitfor)
            except Exception as exc:
                logging.warning(
                    f"invalif waitfor [{waitfor}]: %s, setting to auto-adjust", waitfor, exc
                )
                _ = max(100, len(text) * 3.6)

            logging.debug("preset fixed waiting for %.1f ms", _)

            await page.waitFor(_)
        except Exception as exc:
            logging.warning(" page.waitFor exc: %s", exc)
        try:
            content = await page.content()
        except Exception as exc:
            logging.warning(" page.waitFor exc: %s", exc)
            content = '<div class="lmt__target_textarea">%s</div>' % exc
    
        #Waiting for a fix of pyppeteer
        #element = await page.querySelector('.lmt__target_textarea')
        #title = await page.evaluate('(element) => element.textContent', element)
 
        count = -1
        while count < 50:
            count += 1
            logger.debug(" extra %s x 100 ms", count + 1)
            await page.waitFor(100)

            content = await page.content()
            doc = pq(content)
            res = doc(".lmt__translations_as_text").text()
            if 'Alternatives' in res:
                res=res.split('\n')[1]
            if res:
                break
            await asyncio.sleep(0)
            await asyncio.sleep(0)

        logging.debug("time: %.2f s", default_timer() - then)

        logging.debug("res: %s", res)

        await page.close()

        await asyncio.sleep(0.2)

        return res


    def translate(
            self,
            # headless: bool = not HEADFUL,
            waitfor: Optional[float] = None,
            loop=None
    ) -> Union[Tuple[Optional[str]], Any]:
        # ) -> List[Union[Optional[str], Any]]:
        """ multiple pages
        """

        if loop is None:
            loop = LOOP
        if loop.is_closed():
            loop = asyncio.new_event_loop()

        sents=self.text
        self.browser=LOOP.run_until_complete(self.get_ppbrowser())
        try:
            res = loop.run_until_complete( 
                self.deepl_tr_async(
                self.text,
                from_lang=self.src_lang,
                to_lang=self.dest_lang,
                waitfor=waitfor
            ))
        except Exception as exc:
            logging.error(" loop.run_until_complete exc: %s", exc)
            res = str(exc)

        return res




