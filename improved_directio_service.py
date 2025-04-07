      import asyncio
      import base64
      import logging
      from pathlib import Path
      import random
      import time
      from types import SimpleNamespace
      from typing import List, Optional
      import uuid
      import aiofiles
      from fastapi import FastAPI, HTTPException
      from cterasdk import ctera_direct, settings
      from pydantic import BaseModel
      import os

      # Enable logging for cterasdk direct module to see detailed errors
      logging.getLogger('cterasdk.direct').setLevel(logging.DEBUG)
      logging.getLogger('cterasdk.http').setLevel(logging.DEBUG)
      logging.getLogger('connector').setLevel(logging.DEBUG)
      logger = logging.getLogger('connector')
      app = FastAPI()

      def ctera_direct_client():
      ssl = False
      ctera_timeout = SimpleNamespace(**{
            'sock_connect': 60,
            'sock_read': 120
      })

      if ssl is False:
            logging.getLogger('connector.sources').debug('Disabling SSL Verification.')
            settings.sessions.ctera_direct.api.ssl = False
            settings.sessions.ctera_direct.storage.ssl = False

      if ctera_timeout is not None:
            logging.getLogger('connector.sources').debug('Setting Timeout.')
            settings.sessions.ctera_direct.api.timeout.sock_connect = ctera_timeout.sock_connect
            settings.sessions.ctera_direct.api.timeout.sock_read = ctera_timeout.sock_read
            settings.sessions.ctera_direct.storage.timeout.sock_connect = ctera_timeout.sock_connect
            settings.sessions.ctera_direct.storage.timeout.sock_read = ctera_timeout.sock_read

      url = os.getenv("CTERA_PORTAL_URL")
      access_key_id = os.getenv("CTERA_ACCESS_KEY_ID")
      secret_access_key = os.getenv("CTERA_SECRET_ACCESS_KEY")
      return ctera_direct.client.DirectIO(url, access_key_id, secret_access_key)

      class Chunk(BaseModel):
      url: str
      index: int
      offset: int
      length: int


      class Request(BaseModel):
      encryption_key: str
      chunks: List[Chunk]
      name: str

      class Response(BaseModel):
      status: str
      error: Optional[str] = None

      async def download_from_metadata(request: Request):    
      async with ctera_direct_client() as session:        
            encryption_key = base64.b64decode(request.encryption_key.encode('utf-8'))
            executor = await session._client.executor(request.chunks, encryption_key)
            futures = await executor()
            
            async with aiofiles.open(f'{Path(request.name).stem}_{str(uuid.uuid4())}.pdf', 'wb') as f:            
                  for future in asyncio.as_completed(futures):
                  try:
                        block = await future
                        await f.seek(block.offset)
                        await f.write(block.data)
                  except Exception as e:
                        # Get the most detailed error possible
                        if hasattr(e, 'original_error'):
                              logger.error(f"Original error: {e.original_error}")
                        if hasattr(e, 'original_repr'):
                              logger.error(f"Original error repr: {e.original_repr}")
                        # Check for __cause__ which might contain the original exception
                        if e.__cause__:
                              logger.error(f"Cause: {e.__cause__}")
                        raise
                              
      async def stress_cpu():
      set_time = random.randint(1, 10)
      logger.debug(f"Stressing the CPU for {set_time} seconds")
      timeout = time.time() + float(set_time)
      i = 0
      while time.time() < timeout:
            i += 1
      logger.debug(f"CPU stress complete")
      
      @app.post('/textract')
      async def textract(request: Request) -> Response:
      logger.info(f"Entering textract: {request.name}")
      try:
            await download_from_metadata(request)
            logger.info(f"Downloaded file: {request.name}")
            await stress_cpu()        
            return Response(status="success")
      except Exception as e:
            # Extract detailed error information
            error_detail = str(e)
            if hasattr(e, 'original_error'):
                  error_detail = f"{error_detail} - Original: {e.original_error}"
            if hasattr(e, 'original_repr'):
                  error_detail = f"{error_detail} - Details: {e.original_repr}"
            if e.__cause__:
                  error_detail = f"{error_detail} - Cause: {e.__cause__}"
            
            logger.exception(f'Detailed error: {error_detail}')
            return Response(status="error", error=error_detail)