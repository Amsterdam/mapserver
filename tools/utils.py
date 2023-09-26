import asyncio
import aiohttp
from schematools import types
import requests
import logging
from more_ds.network.url import URL

logger = logging.getLogger("authchecker.utils")

async def schema_task(q, schemas: dict[str, types.DatasetSchema]):
    async with aiohttp.ClientSession() as session:
        while not q.empty():
            base_url, schema_path = await q.get()
            async with session.get(base_url / schema_path / "dataset") as response:
                response_data = await response.json()

            # Include referenced tables for datasets.
            for i, table in enumerate(response_data["tables"]):
                if ref := table.get("$ref"):
                    table_response = await session.get(base_url / schema_path / ref)
                    table_response.raise_for_status()
                    payload = await table_response.json()
                    # Assume `ref` is of form "table_name/v1.1.0"
                    dvn = types.SemVer(ref.split("/")[-1])
                    response_data["tables"][i] = types.TableVersions(
                        id=table["id"], default_version_number=dvn, active={dvn: payload}
                    )
                    for version, ref in table.get("activeVersions", {}).items():
                        table_response = await session.get(base_url / schema_path / ref)
                        table_response.raise_for_status()
                        payload = await table_response.json()
                        response_data["tables"][i].active[types.SemVer(version)] = payload
                else:
                    dvn = types.SemVer(table["version"])
                    response_data["tables"][i] = types.TableVersions(
                        id=table["id"], default_version_number=dvn, active={dvn: table}
                    )
            logger.debug("retrieved %s", schema_path)
            schemas[schema_path] = types.DatasetSchema.from_dict(response_data)


async def _dataset_schemas_from_url(base_url: str):
    base_url = URL(base_url)
    q = asyncio.Queue()
    schemas = {}
    num_tasks = 60

    with requests.Session() as connection:
        response = connection.get(base_url / "index.json")
        response.raise_for_status()
        response_data = response.json()

        for i, (_, schema_path) in enumerate(response_data.items()):
            await q.put((base_url, schema_path))

    await asyncio.gather(*[schema_task(q, schemas) for _ in range(num_tasks)])

    return schemas


def dataset_schemas_from_url(base_url: str = "https://schemas.data.amsterdam.nl/datasets/"):
    return asyncio.run(_dataset_schemas_from_url(base_url))