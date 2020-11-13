FROM neo4j:4.1.3
ADD ./config/neo4j.conf /var/lib/neo4j/conf/
ENV NEO4J_AUTH=neo4j/test NEO4JLABS_PLUGINS='["graph-data-science"]'
EXPOSE 7687 7474