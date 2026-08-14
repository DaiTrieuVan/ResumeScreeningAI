import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.real_job import RealJobPosting

logger = logging.getLogger(__name__)

# Sample Real-World Job Feed for TopCV & ITViec Vietnam Tech Roles
CURATED_REAL_JOBS: List[Dict[str, Any]] = [
    {
        "source": "TopCV",
        "external_id": "topcv-101",
        "title": "Senior Python Backend Engineer (FastAPI / AI)",
        "company_name": "FPT Software",
        "company_logo_url": "https://cdn-new.topcv.vn/unsafe/https://static.topcv.vn/company_logos/fpt-software-6178a9c3d4083.jpg",
        "location": "Hà Nội (Cầu Giấy)",
        "location_tag": "HA_NOI",
        "salary_text": "25 - 40 Triệu VNĐ",
        "salary_min_vnd": 25000000,
        "salary_max_vnd": 40000000,
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API"],
        "experience_required": "3-5 năm",
        "description_text": "Phát triển hệ thống Backend microservices bằng FastAPI và Python 3.13. Tích hợp các mô hình AI/LLM, tối ưu truy vấn PostgreSQL và triển khai Docker container trên hạ tầng Cloud.",
        "source_url": "https://www.topcv.vn/viec-lam/senior-python-backend-engineer"
    },
    {
        "source": "ITViec",
        "external_id": "itviec-202",
        "title": "Fullstack Developer (ReactJS / Python)",
        "company_name": "VNG Corporation",
        "company_logo_url": "https://itviec.com/assets/logo-itviec.png",
        "location": "TP. Hồ Chí Minh (Quận 7)",
        "location_tag": "HO_CHI_MINH",
        "salary_text": "30 - 50 Triệu VNĐ",
        "salary_min_vnd": 30000000,
        "salary_max_vnd": 50000000,
        "required_skills": ["React", "Python", "TypeScript", "FastAPI", "TailwindCSS"],
        "experience_required": "2-4 năm",
        "description_text": "Xây dựng ứng dụng web tương tác người dùng cao với ReactJS và TypeScript. Phát triển RESTful API backend bằng Python FastAPI, đảm bảo hiệu năng và responsive UI.",
        "source_url": "https://itviec.com/it-jobs/fullstack-developer-reactjs-python-vng"
    },
    {
        "source": "TopCV",
        "external_id": "topcv-103",
        "title": "AI / Machine Learning Engineer (LLM & Vector DB)",
        "company_name": "VinAI Research",
        "company_logo_url": "https://static.topcv.vn/company_logos/vinai.jpg",
        "location": "Hà Nội (Bắc Từ Liêm)",
        "location_tag": "HA_NOI",
        "salary_text": "35 - 65 Triệu VNĐ",
        "salary_min_vnd": 35000000,
        "salary_max_vnd": 65000000,
        "required_skills": ["Python", "PyTorch", "Gemini API", "ChromaDB", "NLP"],
        "experience_required": "2+ năm AI/ML",
        "description_text": "Nghiên cứu và triển khai các giải pháp Generative AI, RAG và Vector Embedding. Sử dụng Gemini API, PyTorch và xử lý dữ liệu lớn bằng Python.",
        "source_url": "https://www.topcv.vn/viec-lam/ai-machine-learning-engineer"
    },
    {
        "source": "ITViec",
        "external_id": "itviec-204",
        "title": "Frontend React Developer (Glassmorphism UI)",
        "company_name": "OneMount Group",
        "company_logo_url": "https://itviec.com/assets/logo-itviec.png",
        "location": "Remote / Hà Nội",
        "location_tag": "REMOTE",
        "salary_text": "20 - 35 Triệu VNĐ",
        "salary_min_vnd": 20000000,
        "salary_max_vnd": 35000000,
        "required_skills": ["React", "JavaScript", "CSS3", "Vite", "HTML5"],
        "experience_required": "2+ năm",
        "description_text": "Phát triển giao diện Dashboard hiện đại chuẩn Glassmorphic UI. Tương tác mượt mà với REST API backend và tối ưu UX web ứng dụng.",
        "source_url": "https://itviec.com/it-jobs/frontend-react-developer-onemount"
    },
    {
        "source": "TopCV",
        "external_id": "topcv-105",
        "title": "DevOps Engineer (Docker / Kubernetes / CI-CD)",
        "company_name": "MISA Joint Stock Company",
        "company_logo_url": "https://static.topcv.vn/company_logos/misa.jpg",
        "location": "Đà Nẵng (Hải Châu)",
        "location_tag": "DA_NANG",
        "salary_text": "22 - 38 Triệu VNĐ",
        "salary_min_vnd": 22000000,
        "salary_max_vnd": 38000000,
        "required_skills": ["Docker", "Kubernetes", "CI/CD", "Linux", "Python"],
        "experience_required": "3+ năm",
        "description_text": "Quản lý hệ thống containerization Docker/K8s, tự động hóa quy trình CI/CD deployment và giám sát hệ thống server.",
        "source_url": "https://www.topcv.vn/viec-lam/devops-engineer-misa"
    }
]

async def seed_real_jobs_if_empty(db: AsyncSession) -> int:
    """
    Seeds initial curated real tech jobs if DB has no RealJobPosting records.
    """
    res = await db.execute(select(RealJobPosting))
    existing = res.scalars().all()
    if existing:
        return len(existing)

    count = 0
    for job_data in CURATED_REAL_JOBS:
        job = RealJobPosting(**job_data)
        db.add(job)
        count += 1

    await db.commit()
    logger.info(f"Seeded {count} real job postings from TopCV / ITViec feeds.")
    return count
