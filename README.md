

# RAG-Search-LAB

This repository has educational purpose on advanced RAG Search techniques based on PostgreSQL-pgvector-pgvectorscale-pgai...

## MCP Server for SD Agent

A new MCP server project `custom-agent-tools` has been added to this repository to support the Service Desk AI Agent with modular tools and resources.

### Features added in MCP server:

- Chat interaction logging as resources and tool to add chat logs
- Ticket management as resources and tool to update tickets
- Search tool to query chat logs and tickets by keyword
- Feedback submission tool and resources
- Problem linking tool and resources

This MCP server enables flexible and extensible integration of these functionalities with the AI Agent backend.

The MCP server project is located in the `custom-agent-tools` directory and can be built and run independently.

### How to build and run the MCP server:

```bash
cd custom-agent-tools
npm install
npm run build
node build/index.js
```

### Integration

Once running, the MCP server exposes tools and resources accessible via the Model Context Protocol, allowing the AI Agent to offload these responsibilities.

Please refer to the `custom-agent-tools/README.md` for more details on the MCP server implementation and usage.


## The AI agent Service Desk example

In order to expose a real use cases and prove the point and added value of advanced RAG Search techniques, I created the following data sources
and the associated scenario of a Service Desk team that would take leverage of AI/LLM and RAG Search techniques.   
An AI Agent for the Service Desk team is holding the business logic and has deferent tools like email, document management,... This AI Agent also take leverage of
the RAG Search process that is at the center of experiment. The goal is to explain how different RAG search techniques can impact the response of the Agent.


Intent of the solution and added value expected : 

- Faster Time to Resolution for teams.
- Improvements on the quality of service. 
    - avoid having twice the same error by learning from past resolution
    - link alerts with solutions
    - link SOP with best practices
    - no hanging tickets with automated routing
    - KPI generation for mgmt


## Architecture

![image](https://github.com/user-attachments/assets/5b8d301b-3e73-4d8e-a7b5-a3c5a7453ccd)


# Documents database

This is a sample database that is storing informations about document storage application like Sharepoint or M-Files. 
The intent is to store SOP (Standard Operationnal Procedures) in various format like pdf or makdown to allow retrieval from the RAG Search workflow. 
It is important to note that the database is holding metadata informations of the documents and links of there real paths on the file system. 

## Description of the data model


# Service Desk database 

This database is a sample database of customer service request made on technologies like PostgreSQL, SQL Server, Oracle, RHEL, Ubuntu, ...etc. 
Since there is no sample source of information or model available this database was completely created for this purpose.



## Description of the data model


# RAG database

This database is to allow management of the RAG search process of our application. 
It holds user profile information 

## Description of the data model 


# Hybrid RAG Search design 

## refresh embeddings 


## manual vs dynamic wheigts 



# Data ingestion

In order to test the relevance of this model and find its limits, it is important to feed the databases with realistic data that will 
provide examples of nunances found in the technical environment. 
The AI agent has to provide highly technical information to users that are experienced and avoid miss leading them, the quality of the data 
as much as the way it is processed in the embedding process is a critical part. 

## Chunk sizes 


## Tokenization 


## Embeddings refresh 


# Data retrieval 


## Indexes on pgvector-pgvectorscale 


# Limitations 


## Data flow 

In this example the databases are static. Realistically, the databases of Service Desk and documents would be live with continuously incoming data.
The document database wouldn't be much of challenge since the data won't change so much, so you could run a batch process periodically without much issues on precision and relevance. 
Regarding the Service Desk database, you would need an event that would trigger the re-embedding of the tickets, for example. If a ticket changed drastically, it would make sense 
to process the embedding again and this might happen a lot especially in the early stages of the ticket lifecycle since new informations will be flowing with the investigation. 
I guess it makes sense then to only process new tickets after some time or after a certain level of status is reached. Some fields like alert content could be process right away though since they 
might not change at all after the ticket creation. 
In all case we will need to trace how much a field that is part of an embedding is changed in order to be able to refresh the embedding automatically.
