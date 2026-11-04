"""Optional LangChain StructuredTool contract bridge, not a framework Agent."""
from app.agent import SearchArgs,ReadArgs


def make_tools(registry):
    from langchain_core.tools import StructuredTool
    def search_documents(query:str,k:int=3)->dict:
        return registry.invoke('search_documents',dict(query=query,k=k))
    def read_evidence(source_id:str)->dict:
        return registry.invoke('read_evidence',dict(source_id=source_id))
    return {
        'search_documents':StructuredTool.from_function(func=search_documents,
            name='search_documents',description='Search current staff teaching documents',args_schema=SearchArgs),
        'read_evidence':StructuredTool.from_function(func=read_evidence,
            name='read_evidence',description='Read a source discovered in this run',args_schema=ReadArgs),
    }


def invoke_without_tracing(tools,name,arguments):
    from langsmith import tracing_context
    with tracing_context(enabled=False):
        return tools[name].invoke(arguments)
