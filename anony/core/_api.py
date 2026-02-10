import os
import aiohttp
import asyncio

from anony import config, logger


class FallenApi:
    def __init__(self, retries: int = 5, timeout: int = 15):
        self.api_url = "http://2.56.96.225:6900"
        self.vapi_url = "https://api.video.thequickearn.xyz"
        self.api_key = config.API_KEY
        self.retries = retries
        self.session: aiohttp.ClientSession = None
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.download_dir = "downloads"

    def get_session(self) -> aiohttp.ClientSession:
        if self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def download(
            self,
            link: str,
            video: bool = False,
            wait_for: int = 3,
        ) -> str | None:
        if "v=" in link:
            video_id = link.split("v=")[-1].split("&")[0]
        else:
            video_id = link.rstrip("/").split("/")[-1]

        exts = ("mp4", "webm", "mkv") if video else ("mp3", "m4a", "webm")
        for ext in exts:
            path = f"{self.download_dir}/{video_id}.{ext}"
            if os.path.exists(path):
                return path

        if video:
            song_url = f"{self.vapi_url}/video/{video_id}?api={self.api_key}" 
        else:
            song_url = f"{self.api_key}/audio?song={video_id}"
        dl_url = None
        file_ext = "mp4" if video else "mp3"

        for _ in range(self.retries):
            try:
                async with self.get_session().get(song_url) as resp:
                    if resp.status != 200:
                        logger.warning(f"[API] Request failed ({resp.status})")
                        return None

                    data = await resp.json()
                    status = (data.get("status") or "").lower()

                    if status == "done":
                        dl_url = data.get("link")
                        file_ext = (data.get("format") or "mp3").lower()
                        break
                    elif status == "downloading":
                        await asyncio.sleep(wait_for)
                        continue

                    logger.error(f"[API] Error: {data.get('error') or data.get('message')}")
                    return None
            except aiohttp.ClientError as e:
                logger.warning(f"[API] Network error: {e}")
                return None
            except Exception as e:
                logger.error(f"[API] Error: {e}")
                return None

        if not dl_url:
            logger.warning("[API] Max retries reached.")
            return None

        fpath = f"{self.download_dir}/{video_id}.{file_ext}"
        try:
            async with self.get_session().get(dl_url) as resp:
                if resp.status != 200:
                    logger.error(f"[API DL] Failed ({resp.status})")
                    return None

                with open(fpath, "ab") as f:
                    async for chunk in resp.content.iter_chunked(65536):
                        await asyncio.to_thread(f.write, chunk)
            return fpath

        except aiohttp.ClientError as e:
            logger.warning(f"[DL] Network error: {e}")
            return None
        except Exception as e:
            logger.error(f"[DL] File error: {e}")
            return None
