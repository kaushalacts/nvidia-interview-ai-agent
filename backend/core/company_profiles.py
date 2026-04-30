"""
Company-specific configuration for interview preparation.
Each profile defines: topic focus areas, blog RSS feeds, and question themes.
"""

COMPANY_PROFILES = {
    "NVIDIA": {
        "display_name": "NVIDIA",
        "focus_areas": [
            "CUDA programming", "GPU architecture", "Tensor Cores",
            "MLOps at scale", "Triton Inference Server", "NCCL / distributed training",
            "DGX infrastructure", "NVLink", "RAPIDS", "Kubernetes GPU device plugins",
            "CUDA-aware MPI", "GPU memory management", "Nsight profiling",
        ],
        "blog_feeds": [
            "https://developer.nvidia.com/blog/feed/",
            "https://blogs.nvidia.com/feed/",
        ],
        "interview_themes": [
            "How would you optimize a CUDA kernel for memory bandwidth?",
            "Design a multi-tenant GPU cluster scheduler.",
            "Explain NVLink vs PCIe trade-offs for multi-GPU training.",
            "How does Triton's autotune work under the hood?",
        ],
        "sre_focus": ["GPU utilization SLOs", "DCGM monitoring", "nvml alerting"],
    },
    "Google": {
        "display_name": "Google",
        "focus_areas": [
            "Borg / Kubernetes internals", "Spanner / distributed databases",
            "SRE practices (SLO, error budgets)", "Colossus / GFS",
            "Pub/Sub event streaming", "GKE autopilot", "Monarch monitoring",
            "Chubby distributed locks", "MapReduce / Dataflow",
            "BeyondCorp zero-trust", "Carbon-aware scheduling",
        ],
        "blog_feeds": [
            "https://cloudblog.withgoogle.com/rss/",
            "https://research.google/blog/rss/",
        ],
        "interview_themes": [
            "Design a globally consistent distributed cache.",
            "How would you set error budgets for a 99.99% SLO service?",
            "Explain Borg's resource model and bin-packing algorithm.",
            "How does Spanner achieve external consistency?",
        ],
        "sre_focus": ["Error budget burn rate", "CUJ mapping", "Toil reduction"],
    },
    "Meta": {
        "display_name": "Meta",
        "focus_areas": [
            "Tupperware / Twine container orchestration", "Scuba real-time analytics",
            "Presto distributed SQL", "Thrift RPC", "TAO social graph store",
            "Memcache at scale", "AI Infra / PyTorch distributed",
            "Capacity planning at hyperscale", "Scribe log pipeline",
            "Prophet time-series forecasting", "AIOps and anomaly detection",
        ],
        "blog_feeds": [
            "https://engineering.fb.com/feed/",
        ],
        "interview_themes": [
            "How does TAO handle fan-out reads for the social graph?",
            "Design a real-time anomaly detection pipeline for 1M metrics/sec.",
            "Explain Meta's approach to capacity planning across data centers.",
            "How does Presto federate queries across heterogeneous data stores?",
        ],
        "sre_focus": ["MTTR optimization", "Capacity forecasting", "Incident taxonomy"],
    },
    "Apple": {
        "display_name": "Apple",
        "focus_areas": [
            "Privacy-preserving ML (differential privacy)", "On-device inference",
            "CoreML / Neural Engine", "iCloud distributed storage",
            "Darwin / XNU kernel internals", "Siri NLP pipeline",
            "Push notification at scale (APNs)", "HealthKit data pipelines",
            "Hardware-software co-design", "Secure enclave architecture",
        ],
        "blog_feeds": [
            "https://machinelearning.apple.com/rss/all.xml",
        ],
        "interview_themes": [
            "How would you design a privacy-preserving telemetry system?",
            "Explain differential privacy with Laplace mechanism.",
            "Design on-device ML model updates with rollback guarantees.",
            "How does APNs handle 10B+ daily notifications reliably?",
        ],
        "sre_focus": ["Privacy-aware observability", "On-device reliability", "Zero-knowledge logging"],
    },
}


def get_profile(company: str) -> dict:
    """Return profile for company, defaulting to NVIDIA."""
    return COMPANY_PROFILES.get(company, COMPANY_PROFILES["NVIDIA"])


def list_companies() -> list:
    return list(COMPANY_PROFILES.keys())


def get_focus_areas(company: str) -> list:
    return get_profile(company)["focus_areas"]


def get_blog_feeds(company: str) -> list:
    return get_profile(company)["blog_feeds"]
