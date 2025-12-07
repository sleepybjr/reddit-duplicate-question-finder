from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union

#############################################################
########## Data classes for provider configuration ##########
#############################################################


@dataclass(frozen=True)
class ProviderModel:
    """
    A specific model within a LLM provider, such as "Llama 3.1".

    Attributes:
        id: The unique identifier for the model. example: "llama3.1"
        friendly_name: A human-readable name for the model. example: "Llama 3.1"
        description: A brief description of the model. 
    """
    id: str
    friendly_name: str
    description: str


@dataclass(frozen=True)
class ProviderInfo:
    """
    A provider backend, such as Ollama or OpenAI. Can be an LLM or a search API.

    Attributes:
        id: The unique identifier for the provider. example: "ollama"
        type: The type of provider. example: "ollama", "openai", "http", etc.
        friendly_name: A human-readable name for the provider. example: "Ollama"
        description: A brief description of the provider.
        models:
            - For LLM style providers, a map of model_id -> ProviderModel.
            - For search API's like Google, this can be empty.
        default_model:
            - The model id used if the caller does not override it.
            - Can be None for non model based providers.
    """
    id: str
    type: str
    friendly_name: str
    description: str
    models: Dict[str, ProviderModel] = field(default_factory=dict)
    default_model: Optional[str] = None


class SectionName(Enum):
    """
    Enum for provider section names.

    Attributes:
        text: The string representation of the section name.
        is_multi: Whether the section allows multiple provider selections.
    """
    QUERY = ("query", False)
    SEARCH = ("search", True)
    SUMMARY = ("summary", False)

    def __init__(self, text: str, is_multi: bool):
        self.text = text
        self.is_multi = is_multi


@dataclass(frozen=True)
class ProviderSection:
    """
    A provider section such as "query", "search", or "summary".

    Attributes:
        name: The name of the section. example: SectionName.QUERY, SectionName.SEARCH, or SectionName.SUMMARY.
        description: A brief description of the section's purpose.
        providers: A map of provider_id -> ProviderInfo available in this section.
        default_selection:
            - If it is "query" or "summary", it must be str (provider id). (only one provider allowed)
            - If it is "search", it must be List[str] (provider ids). (multiple providers allowed)
    """
    name: SectionName
    description: str
    providers: Dict[str, ProviderInfo]
    default_selection: Union[str, List[str]]

    def __post_init__(self):
        # Single-select case
        if not self.name.is_multi:
            if not isinstance(self.default_selection, str):
                raise TypeError(
                    f"Section '{self.name.text}' is single-select; "
                    f"default_selection must be a string, not {type(self.default_selection).__name__}."
                )

        # Multi-select case
        else:
            if not isinstance(self.default_selection, list):
                raise TypeError(
                    f"Section '{self.name.text}' is multi-select; "
                    f"default_selection must be a list of strings."
                )
            for item in self.default_selection:
                if not isinstance(item, str):
                    raise TypeError(
                        f"All items in default_selection for '{self.name.text}' "
                        f"must be strings. Got: {item}."
                    )


#############################################################
############### ProviderSection Instances ###################
#############################################################

QUERY_PROVIDERS = ProviderSection(
    name=SectionName.QUERY,
    description="LLM to convert a natural-language question into search queries.",
    providers={
        "ollama_query": ProviderInfo(
            id="ollama_query",
            type="ollama",
            friendly_name="Ollama (query generation)",
            description="Local LLM via Ollama for generating search queries.",
            models={
                "llama3.1": ProviderModel(
                    id="llama3.1",
                    friendly_name="Llama 3.1",
                    description="Default for query generation.",
                ),
            },
            default_model="llama3.1",
        ),
    },
    default_selection="ollama_query",
)

SEARCH_PROVIDERS = ProviderSection(
    name=SectionName.SEARCH,
    description="Searches for an answer. Can be API or LLM.",
    providers={
        "ollama_search": ProviderInfo(
            id="ollama_search",
            type="ollama",
            friendly_name="Ollama (search generation)",
            description="Local LLM via Ollama for generating search results.",
            models={
                "llama3.1": ProviderModel(
                    id="llama3.1",
                    friendly_name="Llama 3.1",
                    description="Default for LLM search generation.",
                ),
            },
            default_model="llama3.1",
        ),
        # Has an additional dependency on a running Ollama instance.
        "searxng": ProviderInfo(
            id="searxng",
            type="http",
            friendly_name="SearXNG",
            description="Meta search engine (self hosted).",
        ),
    },
    default_selection=["ollama_search", "searxng"],
)

SUMMARY_PROVIDERS = ProviderSection(
    name=SectionName.SUMMARY,
    description="LLMs that summarize retrieved context into a final answer.",
    providers={
        "ollama_summary": ProviderInfo(
            id="ollama_summary",
            type="ollama",
            friendly_name="Ollama (summary)",
            description="Local LLM summarizer.",
            models={
                "llama3.1": ProviderModel(
                    id="llama3.1",
                    friendly_name="Llama 3.1",
                    description="Fast summarizer.",
                ),
            },
            default_model="llama3.1",
        ),
    },
    default_selection="ollama_summary",
)

SECTIONS: Dict[str, ProviderSection] = {
    SectionName.QUERY.name: QUERY_PROVIDERS,
    SectionName.SEARCH.name: SEARCH_PROVIDERS,
    SectionName.SUMMARY.name: SUMMARY_PROVIDERS,
}

#############################################################
########## Helper functions for provider config #############
#############################################################


def get_default_query_provider():
    """
    Returns the (provider_id, default_model) tuple for the default query provider.
    """
    section = SECTIONS[SectionName.QUERY.name]
    pid = section.default_selection
    pinfo = section.providers[pid]
    return pid, pinfo.default_model


def get_default_search_providers():
    """
    Returns a list of (provider_id, default_model) tuples for the default search providers.

    [
        (provider_id: str, default_model: Optional[str]),
        (provider_id: str, default_model: Optional[str]),
        ...
    ]
    """
    section = SECTIONS[SectionName.SEARCH.name]
    providers = []
    for pid in section.default_selection:
        pinfo = section.providers[pid]
        providers.append((pid, pinfo.default_model))
    return providers


def get_default_summary_provider():
    """
    Returns the (provider_id, default_model) tuple for the default summary provider.
    """
    section = SECTIONS[SectionName.SUMMARY.name]
    pid = section.default_selection
    pinfo = section.providers[pid]
    return pid, pinfo.default_model
