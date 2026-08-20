"""
BLACKOUT Backend - HydraDB connection management
"""

from neo4j import GraphDatabase
import os


def get_driver():
    """Get a Neo4j driver connected to HydraDB."""
    uri = os.getenv("HYDRADB_BOLT_URI", "bolt://127.0.0.1:7687")
    auth_token = os.getenv("HYDRADB_AUTH_TOKEN", "local-development-token-32-bytes")

    driver = GraphDatabase.driver(uri, auth=("neo4j", auth_token))
    driver.verify_connectivity()
    return driver
