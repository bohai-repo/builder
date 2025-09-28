import os
from dotenv import load_dotenv

from concurrent.futures import ThreadPoolExecutor, as_completed
from elasticsearch import Elasticsearch, helpers

from genie_tool.util.log_util import logger

# 加载 .env 文件
load_dotenv()

def get_docs(func):
    def wrapper(*args, **kwargs):
        doc = func(*args, **kwargs)["hits"]["hits"]
        if doc:
            retrieved_docs = []
            for item in doc:
                new_doc = item.get("_source")
                new_doc["score"] = item.get("_score")
                new_doc["_id"] = item.get("_id")
                retrieved_docs.append(new_doc)
            return retrieved_docs
        else:
            return []

    return wrapper


class ElasticsearchClient:
    def __init__(self, config):
        self._client = Elasticsearch(
            f"{config.get('scheme')}://{config.get('host')}",
            http_auth=(config.get("user"), config.get("password"))
        )
        self._thread_pool = ThreadPoolExecutor(max_workers=8)  # less than 10

    def search_body(self, index, search_body):
        def _query_by_ids(search_body):
            query = search_body.get("query", "这是一个es测试")
            model_code_list = search_body.get("model_code_list", [])
            size = search_body.get("size", 20)
            body = {
                "size": size,
                "query": {
                    "bool": {
                        "must": {
                            "match": {
                                "value": {
                                      "query": query,
                                      "analyzer": "ik_max_word"
                                    }
                            }
                        },
                        "filter": [
                            {
                              "terms": {
                                "modelCode": model_code_list,
                                "boost": 1
                              }
                            }
                          ],
                    }
                },
                "sort": [
                    {
                        "_score": {
                            "order": "desc"
                        }
                    }
                ]
            }
            
            doc = self._client.search(index=index, body=body)
            logger.debug(f"elastic body {body} search result length {len(doc['hits']['hits'])}")
            return {hit['_id']: hit.get("_source") for hit in doc['hits']['hits']}

        res = _query_by_ids(search_body)
        return res
    
    @get_docs
    def query_by_customize(
            self,
            index: str,
            body: dict,
            size: int = 10000
    ):
        return self._client.search(index=index, body=body, size=size)

    @get_docs
    def query_by_scroll(
            self,
            scroll_id,
            scroll: str = '1m'
    ):
        return self._client.scroll(scroll_id=scroll_id, scroll=scroll)

    def insert(
            self,
            index: str,
            data: list[dict]
    ):
        actions = [
            {
                "_op_type": "index",
                "_index": index,
                "_id": d["id"],
                "_source": d["body"]
                }
            for d in data
        ]
        return helpers.bulk(self._client, actions)

    def delete(
            self,
            index: str,
            ids: list,
    ):
        actions = [
            {
                "_op_type": "delete",
                "_index": index,
                "_id": _id
            }
            for _id in ids
        ]
        return helpers.bulk(self._client, actions)

    def get_mapping(
            self,
            index: str
    ):
        return self._client.indices.get_mapping(index=index)

def main():
    # 读取环境变量
    config = {}
    config["host"] = os.getenv("TR_ES_CONFIGS_HOST")
    config["port"] = os.getenv("port")
    config["scheme"] = "http"
    config["user"] = os.getenv("TR_ES_CONFIGS_USER")
    config["password"] = os.getenv("TR_ES_CONFIGS_PASSWORD")
    es_index = config.get("TR_ES_CONFIGS_INDEX", None)
    
    es_client = ElasticsearchClient(config)
    print(config)
    question_es_client = ElasticsearchClient(config)

    search_body = {"query": "cho人数", "model_code_list": ["ceRaxqPbeFgVb8F4h32htcC0HMhrfi"], "size": 100}

    res = question_es_client.search_body(es_index, search_body=search_body)
    print(res)
    
if __name__ == '__main__':
    main()