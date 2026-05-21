---
title: "AI Agents & MCP Servers for Network Engineers: RAG & Chroma MCP Deep Dive"
date: 2025-10-20T00:00:00Z
draft: false
toc: true
---

## Table of Contents

- [Introduction](#introduction)
- [RAG (Database for AI)](#rag-database-for-ai)
  - [Understanding the Challenges](#understanding-the-challenges)
  - [Cost Analysis and Real-World Experience](#cost-analysis-and-real-world-experience)
  - [Chroma MCP Implementation](#chroma-mcp-implementation)
  - [Semantic and Hybrid Search](#semantic-and-hybrid-search)
- [Conclusion](#conclusion)
- [References](#references)

## Introduction

I have reached the conclusion to write this article after 7 months of continous studying , tweaking and testing many AI workflows in order to optimize my daily work,

As a primarily network engineer, my field's vendors still are resisting the pivoting to AI in Infra, as unlike software engineering, which does not mind move fast and break things, in Infrastructure, the vendors can be much more cautous,

So in many cases as you will see, I had to write my own tools, by writing i meant vibing, but with my background in Python scripting, i can post-validate the results,

For each tool you will see in my Github, means i could not find any equivelant official developed tool.

But you must be cautaus, these tools are not vetted 100% security wise, so after you download/fork them, maybe you can do a better job, but the concept stands.

We are at a point that most of the absic tools you can vibe yourself.

Does not shield you from understanding or learning how the languages work , or how to write proper repos.

We will have a look at multiple conecpts in a random fashion.

## RAG (Database for AI)

Qdrant, i was looking to embed my emails into a Embeddings / Vector database which is the equivelent to SQL Database, but for "AI Stuff" just as the AI models learn its knowledge into vector mappings, you can turn your own data into something like it,

### Understanding the Challenges

But 2 hurdles i faced to do that [1 Updated],

1. The technicality : it is not plug and play, in order to store your data into embeddings, you must 1st study , and define the right strategy for Chunk Size, Chunk Overlap, and batch Size, which in simple words you must set an approximate size for the data that would represent a single email in my case,
   While one of the strategies, is to actually run each email through an AI call, and extract a summary in the same size each time,
   Hoever i failed to do it in a smart way, where it actually resulted into the model retrieving any data.

### Cost Analysis and Real-World Experience

2. Cost : Initially cost was a problem, since if you need to run embedding models, you must pay per use, no subscriptions model offered access to the embedding models, but since then, the per use cost of embedding models became extremely low cost, to the degree, that i was able to embed my whole mailbox of 0.5 USD for 5K Emails,
   While you can run a local embedding model, thats an enthusiast path, which is gonna be slow (Tried it already) an email embedding can take to 1 minute depending on its size,
   And more importantly you must remember the quality of the embedding model affects the data search, since, you Must use the same model to seach that database,
   Lets take the following example of an email :

   ``````bash
   To: sarah.johnson@company.com, james.lee@company.com, maria.garcia@company.com
   CC: robert.smith@company.com, emily.wang@company.com, david.brown@company.com, lisa.anderson@company.com
   Subject: Q3 Project Kickoff Meeting - Action Items Required
   Hi Sarah, James, and Maria,
   I hope this email finds you well. I'm writing to follow up on our Q3 project kickoff meeting scheduled for next Wednesday at 10 AM in Conference Room B.
   During our last discussion, we identified several key deliverables that need to be completed by the end of this month:

   Complete the requirements documentation (Sarah - due Sept 15)
   Design the system architecture (James - due Sept 18)
   Prepare the budget breakdown (Maria - due Sept 20)

   Please note that Robert and Emily from Finance have been copied on this email as they need to review the budget proposal. David from IT and Lisa from Operations will also need to provide their input on infrastructure and logistics.
   Could you all please confirm your availability for the Wednesday meeting and let me know if you have any preliminary questions?
   Looking forward to your updates.
   Best regards,
   Michael Chen
   Project Manager
   michael.chen@company.com
   (555) 123-4567
   ``````

   Input count for such an email would be approx 150 tokens, in addition to the prompt could be in total 200 tokens, with google's embedding 001 @ $0.15 per million token , a single email would cost you $0.00002025, to embed.

   **[Real Life Experince]** : from my usage cases so far i have averaged  1,400 Tokens per Email, coming to $0.000049 per email, using all-MiniLM-L6-v2 model required by ChromaDB official MCP server.

Since embedding and retrieval must use the same Model, choosing the right one is very important, since re-Embdding your data using a new diffirent model, will result into additional cost plus time,

### Chroma MCP Implementation

You can add RAG access to your IDE instead a part of a Pipeline or application, you need to point the MCP config towards you local ChromaDB file , which is an SQLlite database  but in a form of vector , meaning, its a single file database, that is easy to transport, if you wanna go more professional you can try Qdrant, which offers a server interface,

For now lets stick to Chroma MCP, one caveat, it uses a very strict dim size and a specific model , which you have to account for while embedding your data, or creating you collection. 384-dim instead of the standard 1536-dim used by open ai and frontier providers and all-minilm-l6-v2 model which is the embedding model supported by Chroma MCP.

### Semantic and Hybrid Search

**Semantic search** is what using RAG offers, meaning the Model employes the same techinque it was traind on to search for data in your database, so only relevance is enough, words does not have to match perfectly.

Its considered also best practice to go for the Hybrid search between the semantic and text filtering, since this way you would be able to search also more specifically for example if you are looking for an exact IP Address,

## Conclusion

## References

- [amrelhusseiny.github.io](https://github.com/amrelhusseiny/amrelhusseiny.github.io)
- [cisco_ise_mcp_server](https://github.com/amrelhusseiny/cisco_ise_mcp_server)
- [cisco_mcp](https://github.com/amrelhusseiny/cisco_mcp)
- [m365_mcp](https://github.com/amrelhusseiny/m365_mcp)
- [pano_mcp](https://github.com/amrelhusseiny/panos_mcp)
- [python_development_private](https://github.com/amrelhusseiny/python_development_private)
- Models Cost - https://models.dev/
- https://www.tensoreconomics.com/p/why-are-embeddings-so-cheap
- https://www.tensoreconomics.com/p/llm-inference-economics-from-first
- MCP Apps PR - https://github.com/modelcontextprotocol/modelcontextprotocol/pull/1865
- Elasticsearch support for Vector Search /Symantic using ELSER Models https://www.elastic.co/docs/solutions/search/semantic-search/semantic-search-elser-ingest-pipelines
- Docker MCP Gaewtway https://docs.docker.com/ai/mcp-catalog-and-toolkit/mcp-gateway/