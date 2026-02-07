import asyncio
import os
import re
import uuid
import aiohttp
import urllib.parse
from typing import Dict, Optional
from pathlib import Path
from dataclasses import dataclass

from pyrogram import errors
from anony import config, logger, app


@dataclass
class MusicTrack:
    cdnurl: str
    url: str
    id: str
    key: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "MusicTrack":
        return cls(
            cdnurl=data.get("cdnurl", ""),
            url=data.get("url", ""),
            id=data.get("id", ""),
            key=data.get("key"),
        )


class FallenApi:
    def __init__(self, retries: int = 3, timeout: int = 15):
        self.api_url = config.API_URL.rstrip("/")
        self.api_key = config.API_KEY
        self.retries = retries
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.download_dir = Path("downloads")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }

    async def get_track(self, url: str) -> Optional[MusicTrack]:
        endpoint = f"{self.api_url}/api/track?url={urllib.parse.quote(url)}"

        for attempt in range(1, self.retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(endpoint, headers=self._get_headers()) as resp:
                        data = await resp.json(content_type=None)

                        if resp.status == 200 and isinstance(data, dict):
                            return MusicTrack.from_dict(data)

                        error_msg = data.get("message") if isinstance(data, dict) else None
                        status = data.get("status", resp.status) if isinstance(data, dict) else resp.status
                        logger.warning(f"[API ERROR] {error_msg or 'Unexpected error'} (status {status})")
                        return None

            except aiohttp.ClientError as e:
                logger.warning(f"[NETWORK ERROR] Attempt {attempt}/{self.retries} failed: {e}")
            except asyncio.TimeoutError:
                logger.warning(f"[TIMEOUT] Attempt {attempt}/{self.retries} exceeded timeout.")
            except Exception as e:
                logger.warning(f"[UNEXPECTED ERROR] {e}")

            await asyncio.sleep(1)

        logger.warning("[FAILED] All retry attempts exhausted.")
        return None

    async def download_cdn(self, cdn_url: str) -> Optional[str]:
        for attempt in range(1, self.retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(cdn_url) as resp:
                        if resp.status != 200:
                            logger.warning(f"[HTTP {resp.status}] Failed to download from {cdn_url}")
                            return None

                        cd = resp.headers.get("Content-Disposition")
                        if cd:
                            match = re.findall(r'filename="?([^";]+)"?', cd)
                            filename = match[0] if match else None
                        else:
                            filename = None

                        if not filename:
                            filename = os.path.basename(cdn_url.split("?")[0]) or f"{uuid.uuid4().hex[:8]}.mp3"

                        save_path = self.download_dir / filename

                        with open(save_path, "wb") as f:
                            async for chunk in resp.content.iter_chunked(16 * 1024):
                                if chunk:
                                    f.write(chunk)

                        return str(save_path)

            except aiohttp.ClientError as e:
                logger.warning(f"[NETWORK ERROR] Attempt {attempt}/{self.retries} failed: {e}")
            except asyncio.TimeoutError:
                logger.warning(f"[TIMEOUT] Attempt {attempt}/{self.retries} exceeded timeout.")
            except Exception as e:
                logger.warning(f"[UNEXPECTED ERROR] {e}")

            await asyncio.sleep(1)

        logger.warning("[FAILED] CDN download attempts exhausted.")
        return None

    async def download_track(self, url: str) -> Optional[str]:
        track = await self.get_track(url)
        if not track:
            logger.warning("[❌] No track metadata found.")
            return None

        dl_url = track.cdnurl
        tg_match = re.match(r"https?://t\.me/([^/]+)/(\d+)", dl_url)
        if tg_match:
            chat, msg_id = tg_match.groups()
            try:
                msg = await app.get_messages(chat_id=chat, message_ids=int(msg_id))
                file_path = await msg.download(file_name=self.download_dir)
                return file_path
            except errors.FloodWait as e:
                logger.warning(f"[FLOODWAIT] Sleeping {e.value}s before retry.")
                await asyncio.sleep(e.value)
                return await self.download_track(url)
            except Exception as e:
                logger.warning(f"[TG DOWNLOAD ERROR] {e}")
                return None

        return await self.download_cdn(dl_url)
