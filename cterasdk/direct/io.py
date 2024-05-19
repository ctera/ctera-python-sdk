async def get(direct, file_id, credential):
    """
    Get File.

    :param cterasdk.clients.asynchronous.clients.DirectIO direct: Asynchronous DirectIO client.
    :param int file_id: File ID.
    :param cterasdk.objects.asynchronous.direct.Credential credential: Credential
    """
    response = await direct.chunks(f'{file_id}', headers={'Authorization': f'Bearer {credential.access_key_id}'})
    for chunk in response.chunks:
        res = await direct.get(chunk.url)
        with open(r'c:/users/saimon/downloads/1.pdf', 'wb') as fd:
            async for chunk in res.chunk:
                fd.write(chunk)

