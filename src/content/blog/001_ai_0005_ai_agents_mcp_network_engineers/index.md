---
title: "AI Agents & MCP Servers for Network Engineers"
date: 2025-10-20T00:00:00Z
draft: true
toc: true
---

## Introduction

I have reached the conclusion to write this article after 7 months of continous studying , tweaking and testing many AI workflows in order to optimize my daily work, 

As a primarily network engineer, my field's vendors still are resisting the pivoting to AI in Infra, as unlike software engineering, which does not mind move fast and break things, in Infrastructure, the vendors can be much more cautous, 

So in many cases as you will see, I had to write my own tools, by writing i meant vibing, but with my background in Python scripting, i can post-validate the results,

For each tool you will see in my Github, means i could not find any equivelant official developed tool.

But you must be cautaus, these tools are not vetted 100% security wise, so after you download/fork them, maybe you can do a better job, but the concept stands.

We are at a point that most of the absic tools you can vibe yourself.

Does not shield you from understanding or learning how the languages work , or how to write proper repos.

We will have a look at multiple conecpts in a random fashion.

## Unorganized thoughts

### MCP Scale Up

At some point you are going to face the issue where you have too many tools, and then you must account for that not all providers support unlimited number of tools, as an example, with github copilot API, you are limited to 128 Tools max, while it seems like a lot, it reallu isn't, each MCP server would probably include many, and in my case , i have 9 MCP server at the moment, 

So what is the solution, 

Here comes the use of the AGENTS.md and the IDE md files, in my case Opencode.json :

1. Selective enabling of MCP servers per project / Directory, using your IDE's md file, in my case I can use an opencode.json per project, in the following format for example :
```json
   # opencode.json
   {
     "$schema": "https://opencode.ai/config.json",
     "mcp": {
       "mcp-ssh": {"enabled": true},
       "pyats-mcp": {"enabled": false},
       ....
     }
   }
```

2. Using the standardized AGENTS.md file to gorup the tools into more specific usage cases : 
```markdown
   # .opencode/AGENTS.md
   
   ## Agent: default
   - MCP: mcp-ssh, pyats-mcp
   - When: General tasks, network automation, SSH operations
   
   ## Agent: network
   - MCP: pyats-mcp, palo-alto-panos, mcp-ssh
   - When: Network device management, firewall config, Cisco ISE tasks
   
   .....
```
   
   Then you can start the right Agent you need whe you initiate the IDE : 
   
```bash
   opencode "Check firewall policies" --agent=network
```

Not only did that fix some of the Cloud providers limits for me, it significantly decreased the token usage for me with each API call to a model, i dont need to send all those tools for the model to select in-between, 

With current usage i have 9 MCP servers and 233 tools, producing 58,000 tokens even before asking any questions, so you can imageing the unecessary cost that is resulting into.

### MCP Dynamic Loading

Instead of having to configure each tool individually, and to also to avoid Context Rot and Tool poisonbing, you can also configure a Meta Gateway, as an exapmple we use the Docker open source **MCP gateway** to cheive that target , 

Also second Feature that you can utilize is **Dynamic Discovery** , 

#### Docker MCP Gateway

The following  demontrates the usage of Docker MCP Gateway vs lcoal config overhead Tools definition token usage.

[ To Do ]

### MCP-UI / MCP-Apps (https://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/)

One of the exciting new features being added to MCP standards, is the ability to present UI  parts by the MCP server to provide visulizations or interactive interaction with the use like selection boxes and so on.

### MCP - Progrissive Discovery

### MCP - Programatic tool calling

### MCP 

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