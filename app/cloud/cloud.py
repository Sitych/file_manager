import boto3
import asyncio
from app.cloud.utils import async_wrap


class Cloud:
    def __init__(self, config: dict):
        loop = asyncio.get_event_loop()
        if loop is None:
            loop = asyncio.new_event_loop()
        self.loop = loop
        self.client = self.get_s3_client(config)
        self.__config = config
    
    @staticmethod
    def get_s3_client(config: dict):
        boto_config = {
            'service_name': 's3',
            'region_name': config.get('region', 'ru'),
            'verify': False,
            'aws_access_key_id': config['key'],
            'aws_secret_access_key': config['secret'],
            'endpoint_url': config['endpoint'],
        }
        s3obj = boto3.client(**boto_config)
        return s3obj
    
    async def uplod_file_by_chunks(self, chunk: bytes):
        async_upload_fileobj = async_wrap(self.client.upload_fileobj)
        await async_upload_fileobj(chunk, self.__config['bucket'], self.__config['secret'], loop=self.loop)
