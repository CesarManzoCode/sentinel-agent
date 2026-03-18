from __future__ import annotations

from dataclasses import dataclass

from sentinel.infrastructure.cli.renderer import TerminalRenderer
from sentinel.application.agent_runtime.context_builder import ContextBuilder
from sentinel.application.agent_runtime.executor import ExecutionService
from sentinel.application.agent_runtime.orchestrator import AgentOrchestrator
from sentinel.application.agent_runtime.planner import PlannerService
from sentinel.application.agent_runtime.reflector import ReflectionService
from sentinel.application.agent_runtime.responder import ResponseService
from sentinel.application.agent_runtime.session_manager import SessionManager
from sentinel.application.audit.trace_service import TraceService
from sentinel.application.llm.conversation_compactor import ConversationCompactor
from sentinel.application.llm.llm_gateway import LLMGateway
from sentinel.application.llm.prompt_assembler import PromptAssembler
from sentinel.application.llm.structured_output import StructuredOutputService
from sentinel.application.memory.consolidation_service import MemoryConsolidationService
from sentinel.application.memory.indexing_service import MemoryIndexingService
from sentinel.application.memory.memory_packager import MemoryPackager
from sentinel.application.memory.retrieval_service import MemoryRetrievalService
from sentinel.application.memory.summarization_service import SummarizationService
from sentinel.application.safety.approval_service import ApprovalService
from sentinel.application.safety.command_guard import CommandGuard
from sentinel.application.safety.policy_engine import PolicyEngine
from sentinel.application.safety.redaction import RedactionService
from sentinel.application.safety.risk_evaluator import RiskEvaluator
from sentinel.application.tools.argument_binding import ArgumentBinder
from sentinel.application.tools.capability_scope import CapabilityScopeService
from sentinel.application.tools.dispatcher import ToolDispatcher
from sentinel.application.tools.registry import ToolRegistryService
from sentinel.application.tools.result_normalizer import ToolResultNormalizer
from sentinel.application.use_cases.approve_action import ApproveAction
from sentinel.application.use_cases.handle_user_turn import HandleUserTurn
from sentinel.application.use_cases.inspect_trace import InspectTrace
from sentinel.application.use_cases.list_tools import ListTools
from sentinel.application.use_cases.manage_memory import ManageMemory
from sentinel.config.logging import LoggingConfigurator
from sentinel.config.settings import Settings
from sentinel.domain.agent.value_objects import ExecutionBudget
from sentinel.domain.llm.ports import LLMPort
from sentinel.domain.safety.services import SafetyPolicyService
from sentinel.domain.tools.ports import ToolRegistryPort
from sentinel.infrastructure.llm.groq_client import GroqLLMClient
from sentinel.infrastructure.llm.response_parser import ProviderResponseParser
from sentinel.infrastructure.llm.stream_adapter import LLMStreamAdapter
from sentinel.infrastructure.memory.embedding_model import LocalEmbeddingModel
from sentinel.infrastructure.memory.retrievers.bm25_retriever import BM25Retriever
from sentinel.infrastructure.memory.retrievers.fusion_retriever import FusionRetriever
from sentinel.infrastructure.memory.retrievers.vector_retriever import VectorRetriever
from sentinel.infrastructure.memory.summarizers.conversation_summarizer import ConversationSummarizer
from sentinel.infrastructure.persistence.db import DatabaseManager
from sentinel.infrastructure.persistence.repositories.approval_repository import SQLiteApprovalRepository
from sentinel.infrastructure.persistence.repositories.audit_repository import SQLiteAuditRepository
from sentinel.infrastructure.persistence.repositories.memory_repository import SQLiteMemoryRepository
from sentinel.infrastructure.persistence.repositories.session_repository import SQLiteSessionRepository
from sentinel.infrastructure.persistence.repositories.tool_catalog_repository import SQLiteToolCatalogRepository
from sentinel.infrastructure.persistence.vector.embedding_cache import EmbeddingCache
from sentinel.infrastructure.persistence.vector.hnsw_index import HNSWIndexStore
from sentinel.infrastructure.security.audit_logger import AuditLogger
from sentinel.infrastructure.security.secret_detector import SecretDetector
from sentinel.infrastructure.telemetry.health import HealthChecker
from sentinel.infrastructure.telemetry.metrics import MetricsRecorder
from sentinel.infrastructure.tools.registry_loader import ToolRegistryLoader
from sentinel.infrastructure.tools.terminal.validator import TerminalCommandValidator
from sentinel.shared.time import Clock


@dataclass(slots=True)
class ApplicationContainer:
    settings: Settings
    handle_user_turn: HandleUserTurn
    approve_action: ApproveAction
    list_tools: ListTools
    inspect_trace: InspectTrace
    manage_memory: ManageMemory
    health_checker: HealthChecker
    metrics: MetricsRecorder


def bootstrap(
    *,
    settings: Settings | None = None,
    llm_provider: LLMPort | None = None,
    tool_registry: ToolRegistryPort | None = None,
) -> ApplicationContainer:
    settings = settings or Settings.load()
    LoggingConfigurator(settings).configure()
    renderer = TerminalRenderer(debug_mode=settings.app.debug)
    db = DatabaseManager(settings.paths.db_file)
    db.initialize()

    session_repo = SQLiteSessionRepository(db)
    memory_repo = SQLiteMemoryRepository(db)
    trace_repo = SQLiteAuditRepository(db)
    approval_repo = SQLiteApprovalRepository(db)
    tool_catalog_repo = SQLiteToolCatalogRepository(db)

    cache = EmbeddingCache(db)
    embeddings = LocalEmbeddingModel(settings.memory.embedding_dim, cache=cache)
    vector_index = HNSWIndexStore(settings.paths.vector_dir, settings.memory.embedding_dim)

    lexical = BM25Retriever(memory_repo)
    semantic = VectorRetriever(memory_repo, embeddings, vector_index)
    fusion = FusionRetriever(lexical=lexical, semantic=semantic)
    memory_retrieval = MemoryRetrievalService(fusion)
    memory_packager = MemoryPackager()
    summarization = SummarizationService(ConversationSummarizer())
    indexing = MemoryIndexingService(memory_repo, embeddings)
    memory_consolidation = MemoryConsolidationService(memory_repo, summarization, indexing)

    tool_registry = tool_registry or ToolRegistryLoader(settings, tool_catalog_repo).load()
    tool_registry_service = ToolRegistryService(tool_registry)

    command_validator = TerminalCommandValidator(set(settings.safety.denied_binaries))
    command_guard = CommandGuard(command_validator)
    approval_service = ApprovalService(approval_repo, clock=Clock(), ttl_seconds=settings.safety.approval_ttl_seconds)
    risk_evaluator = RiskEvaluator()
    policy_engine = PolicyEngine(
        risk_evaluator=risk_evaluator,
        safety_service=SafetyPolicyService(),
        approval_service=approval_service,
        command_guard=command_guard,
        auto_approve_low_risk=settings.profile.auto_approve_low_risk,
        auto_approve_medium_risk=settings.profile.auto_approve_medium_risk,
    )

    dispatcher = ToolDispatcher(
        registry=tool_registry,
        policy_engine=policy_engine,
        binder=ArgumentBinder(),
        normalizer=ToolResultNormalizer(),
    )

    if llm_provider is None:
        llm_provider = GroqLLMClient(
            api_key=settings.llm.api_key,
            model=settings.llm.model,
            base_url=settings.llm.base_url,
            timeout_seconds=settings.llm.timeout_seconds,
            parser=ProviderResponseParser(),
            stream_adapter=LLMStreamAdapter(),
        )

    llm_gateway = LLMGateway(
        provider=llm_provider,
        renderer=renderer,
    )
    prompt_assembler = PromptAssembler()
    planner = PlannerService(llm_gateway, prompt_assembler, StructuredOutputService())
    responder = ResponseService(llm_gateway, prompt_assembler)

    session_manager = SessionManager(session_repo, ConversationCompactor())
    trace_service = TraceService(trace_repo)
    context_builder = ContextBuilder(memory_retrieval, memory_packager, tool_registry_service)
    executor = ExecutionService(dispatcher)
    reflector = ReflectionService()
    metrics = MetricsRecorder()
    audit_logger = AuditLogger(settings.paths.audit_dir / "audit.log")
    redaction = RedactionService(SecretDetector())
    # eager initialization for audit infrastructure
    audit_logger.record("bootstrap", {"status": "initialized"})
    _ = redaction

    orchestrator = AgentOrchestrator(
        session_manager=session_manager,
        context_builder=context_builder,
        planner=planner,
        executor=executor,
        reflector=reflector,
        responder=responder,
        trace_service=trace_service,
        scope_service=CapabilityScopeService(),
        memory_consolidation=memory_consolidation,
        default_budget=ExecutionBudget(
            max_steps=settings.profile.max_steps_per_turn,
            max_tool_calls=settings.profile.max_tool_calls_per_turn,
            max_tokens=12_000,
            wall_clock_seconds=60,
        ),
        memory_top_k=settings.memory.top_k,
    )

    handle_user_turn = HandleUserTurn(orchestrator)
    approve_action = ApproveAction(approval_service)
    list_tools = ListTools(tool_registry_service)
    inspect_trace = InspectTrace(trace_service)
    manage_memory = ManageMemory(memory_repo)
    health_checker = HealthChecker(settings, db)

    return ApplicationContainer(
        settings=settings,
        handle_user_turn=handle_user_turn,
        approve_action=approve_action,
        list_tools=list_tools,
        inspect_trace=inspect_trace,
        manage_memory=manage_memory,
        health_checker=health_checker,
        metrics=metrics,
    )
