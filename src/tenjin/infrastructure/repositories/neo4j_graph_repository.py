"""Neo4j implementation of GraphRepository."""

from typing import Any, Sequence

from ...domain.entities.relationship import TheoryRelationship
from ...domain.repositories.graph_repository import GraphRepository
from ...domain.value_objects.relationship_type import RelationshipType
from ..adapters.neo4j_adapter import Neo4jAdapter
from ..config.logging import get_logger

logger = get_logger(__name__)


class Neo4jGraphRepository(GraphRepository):
    """Neo4j implementation of GraphRepository.

    Provides graph traversal and relationship operations using Neo4j.
    """

    def __init__(self, adapter: Neo4jAdapter) -> None:
        """Initialize repository with Neo4j adapter.

        Args:
            adapter: Neo4j database adapter.
        """
        self._adapter = adapter

    async def get_related_theories(
        self,
        theory_id: str,
        relationship_type: RelationshipType | None = None,
        depth: int = 1,
        limit: int = 20,
    ) -> Sequence[dict[str, Any]]:
        """Get theories related to a given theory."""
        if relationship_type:
            rel_filter = f":{relationship_type.value.upper()}"
        else:
            rel_filter = ""

        query = f"""
        MATCH (t1:Theory {{id: $id}})-[r{rel_filter}*1..{depth}]-(t2:Theory)
        WHERE t1 <> t2
        WITH DISTINCT t2, r
        RETURN t2 as theory,
               [rel in r | type(rel)] as relationship_types,
               length(r) as distance
        ORDER BY distance, t2.priority
        LIMIT $limit
        """
        records = await self._adapter.execute_read(
            query, {"id": theory_id, "limit": limit}
        )

        return [
            {
                "theory": dict(r["theory"]),
                "relationship_types": r["relationship_types"],
                "distance": r["distance"],
            }
            for r in records
        ]

    async def get_relationship(
        self,
        source_id: str,
        target_id: str,
    ) -> TheoryRelationship | None:
        """Get relationship between two theories."""
        query = """
        MATCH (t1:Theory {id: $source_id})-[r]->(t2:Theory {id: $target_id})
        RETURN type(r) as type, r.description as description,
               r.strength as strength, r.created_at as created_at
        """
        records = await self._adapter.execute_read(
            query, {"source_id": source_id, "target_id": target_id}
        )

        if records:
            r = records[0]
            return TheoryRelationship(
                source_id=source_id,
                target_id=target_id,
                relationship_type=RelationshipType(r["type"].lower()),
                description=r.get("description", ""),
                strength=r.get("strength", 0.5),
            )
        return None

    async def get_relationships(
        self,
        theory_id: str,
        direction: str = "both",
    ) -> Sequence[TheoryRelationship]:
        """Get all relationships for a theory."""
        if direction == "outgoing":
            query = """
            MATCH (t1:Theory {id: $id})-[r]->(t2:Theory)
            RETURN t1.id as source, t2.id as target, type(r) as type,
                   r.description as description, r.strength as strength
            """
        elif direction == "incoming":
            query = """
            MATCH (t1:Theory)-[r]->(t2:Theory {id: $id})
            RETURN t1.id as source, t2.id as target, type(r) as type,
                   r.description as description, r.strength as strength
            """
        else:  # both
            query = """
            MATCH (t1:Theory {id: $id})-[r]-(t2:Theory)
            RETURN t1.id as source, t2.id as target, type(r) as type,
                   r.description as description, r.strength as strength
            """

        records = await self._adapter.execute_read(query, {"id": theory_id})

        return [
            TheoryRelationship(
                source_id=r["source"],
                target_id=r["target"],
                relationship_type=RelationshipType(r["type"].lower()),
                description=r.get("description", ""),
                strength=r.get("strength", 0.5),
            )
            for r in records
        ]

    async def create_relationship(
        self,
        relationship: TheoryRelationship,
    ) -> TheoryRelationship:
        """Create a new relationship between theories."""
        rel_type = relationship.relationship_type.value.upper()

        query = f"""
        MATCH (t1:Theory {{id: $source_id}})
        MATCH (t2:Theory {{id: $target_id}})
        MERGE (t1)-[r:{rel_type}]->(t2)
        SET r.description = $description,
            r.strength = $strength,
            r.created_at = datetime()
        RETURN r
        """
        await self._adapter.execute_write(
            query,
            {
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "description": relationship.description,
                "strength": relationship.strength,
            },
        )

        # Create reverse relationship if bidirectional
        if relationship.bidirectional:
            inverse_type = relationship.relationship_type.inverse.value.upper()
            reverse_query = f"""
            MATCH (t1:Theory {{id: $target_id}})
            MATCH (t2:Theory {{id: $source_id}})
            MERGE (t1)-[r:{inverse_type}]->(t2)
            SET r.description = $description,
                r.strength = $strength,
                r.created_at = datetime()
            """
            await self._adapter.execute_write(
                reverse_query,
                {
                    "source_id": relationship.source_id,
                    "target_id": relationship.target_id,
                    "description": relationship.description,
                    "strength": relationship.strength,
                },
            )

        logger.debug(
            f"Created relationship: {relationship.source_id} "
            f"-[{rel_type}]-> {relationship.target_id}"
        )
        return relationship

    async def delete_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
    ) -> bool:
        """Delete a relationship."""
        rel_type = relationship_type.value.upper()
        query = f"""
        MATCH (t1:Theory {{id: $source_id}})-[r:{rel_type}]->(t2:Theory {{id: $target_id}})
        DELETE r
        RETURN count(r) as deleted
        """
        result = await self._adapter.execute_write(
            query, {"source_id": source_id, "target_id": target_id}
        )

        return result.get("relationships_deleted", 0) > 0

    async def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5,
    ) -> Sequence[dict[str, Any]] | None:
        """Find shortest path between two theories."""
        query = f"""
        MATCH path = shortestPath(
            (t1:Theory {{id: $source_id}})-[*1..{max_depth}]-(t2:Theory {{id: $target_id}})
        )
        RETURN [node in nodes(path) | {{
            id: node.id,
            name: node.name,
            type: labels(node)[0]
        }}] as nodes,
        [rel in relationships(path) | {{
            type: type(rel),
            source: startNode(rel).id,
            target: endNode(rel).id
        }}] as relationships
        """
        records = await self._adapter.execute_read(
            query, {"source_id": source_id, "target_id": target_id}
        )

        if records:
            return [
                {"nodes": r["nodes"], "relationships": r["relationships"]}
                for r in records
            ]
        return None

    async def get_theory_network(
        self,
        theory_id: str,
        depth: int = 2,
    ) -> dict[str, Any]:
        """Get network graph around a theory."""
        query = f"""
        MATCH path = (t1:Theory {{id: $id}})-[*0..{depth}]-(t2:Theory)
        WITH collect(distinct t1) + collect(distinct t2) as allNodes,
             collect(distinct relationships(path)) as allRels
        UNWIND allNodes as node
        WITH collect(distinct {{
            id: node.id,
            name: node.name,
            category: node.category,
            priority: node.priority
        }}) as nodes, allRels
        UNWIND allRels as rels
        UNWIND rels as rel
        WITH nodes, collect(distinct {{
            source: startNode(rel).id,
            target: endNode(rel).id,
            type: type(rel)
        }}) as edges
        RETURN nodes, edges
        """
        records = await self._adapter.execute_read(query, {"id": theory_id})

        if records:
            return {
                "nodes": records[0]["nodes"],
                "edges": records[0]["edges"],
                "center": theory_id,
            }
        return {"nodes": [], "edges": [], "center": theory_id}

    async def get_category_subgraph(
        self,
        category: str,
    ) -> dict[str, Any]:
        """Get subgraph for a category."""
        query = """
        MATCH (t:Theory {category: $category})
        OPTIONAL MATCH (t)-[r]-(t2:Theory {category: $category})
        WITH collect(distinct {
            id: t.id,
            name: t.name,
            priority: t.priority
        }) as nodes,
        collect(distinct case when r is not null then {
            source: startNode(r).id,
            target: endNode(r).id,
            type: type(r)
        } end) as edges
        RETURN nodes, [e in edges where e is not null] as edges
        """
        records = await self._adapter.execute_read(query, {"category": category})

        if records:
            return {
                "nodes": records[0]["nodes"],
                "edges": records[0]["edges"],
                "category": category,
            }
        return {"nodes": [], "edges": [], "category": category}

    async def get_influence_chain(
        self,
        theory_id: str,
        direction: str = "both",
        max_depth: int = 3,
    ) -> Sequence[dict[str, Any]]:
        """Get influence chain for a theory."""
        if direction == "influencers":
            query = f"""
            MATCH path = (t2:Theory)-[:INFLUENCES|BUILDS_UPON*1..{max_depth}]->(t1:Theory {{id: $id}})
            RETURN t2 as theory, length(path) as depth
            ORDER BY depth
            """
        elif direction == "influenced":
            query = f"""
            MATCH path = (t1:Theory {{id: $id}})-[:INFLUENCES|BUILDS_UPON*1..{max_depth}]->(t2:Theory)
            RETURN t2 as theory, length(path) as depth
            ORDER BY depth
            """
        else:  # both
            query = f"""
            MATCH path = (t1:Theory {{id: $id}})-[:INFLUENCES|BUILDS_UPON|INFLUENCED_BY*1..{max_depth}]-(t2:Theory)
            RETURN distinct t2 as theory, min(length(path)) as depth
            ORDER BY depth
            """

        records = await self._adapter.execute_read(query, {"id": theory_id})

        return [
            {"theory": dict(r["theory"]), "depth": r["depth"]}
            for r in records
        ]

    async def get_common_relationships(
        self,
        theory_ids: Sequence[str],
    ) -> Sequence[dict[str, Any]]:
        """Find common relationships among theories."""
        if len(theory_ids) < 2:
            return []

        query = """
        MATCH (t:Theory)-[r]-(common:Theory)
        WHERE t.id IN $ids AND NOT common.id IN $ids
        WITH common, count(distinct t) as connection_count
        WHERE connection_count >= 2
        RETURN common as theory, connection_count
        ORDER BY connection_count DESC
        """
        records = await self._adapter.execute_read(query, {"ids": list(theory_ids)})

        return [
            {
                "theory": dict(r["theory"]),
                "connection_count": r["connection_count"],
            }
            for r in records
        ]

    async def execute_cypher(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> Sequence[dict[str, Any]]:
        """Execute a Cypher query directly."""
        return await self._adapter.execute_read(query, parameters)
