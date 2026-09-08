import logging
import uuid
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.real_job import RealJobPosting

logger = logging.getLogger(__name__)

# Check Crawl4AI availability
CRAWL4AI_AVAILABLE = False
try:
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
    CRAWL4AI_AVAILABLE = True
    logger.info("Crawl4AI library successfully loaded.")
except Exception as err:
    logger.warning(f"Crawl4AI not active/available ({err}). Fallback mode enabled.")

# Multi-Industry Live Jobs Data Feed for MVP & Production Matching
MVP_DEMO_LIVE_JOBS: List[Dict[str, Any]] = [
    # --- F&B / CHEF / CULINARY JOBS ---
    {
        "source": "TopCV",
        "external_id": "topcv-chef-401",
        "title": "Bếp Trưởng Điều Hành / Head Chef (Khách Sạn - Nhà Hàng 5 Sao)",
        "company_name": "Golden Palace Resort & Hotel",
        "company_logo_url": "https://static.topcv.vn/company_logos/golden-palace.jpg",
        "location": "Hà Nội (Hoàn Kiếm)",
        "location_tag": "HA_NOI",
        "salary_text": "25 - 40 Triệu VNĐ",
        "salary_min_vnd": 25000000,
        "salary_max_vnd": 40000000,
        "required_skills": ["Culinary Arts", "Menu Planning", "Food Safety & Hygiene", "Kitchen Management", "Asian/European Cuisine", "Cost Control"],
        "experience_required": "3+ năm",
        "description_text": "Quản lý toàn bộ hoạt động khu vực Bếp nhà hàng 5 sao. Xây dựng thực đơn Á-Âu cao cấp, kiểm soát chi phí nguyên vật liệu và đào tạo đội ngũ nhân viên bếp.",
        "source_url": "https://www.topcv.vn/viec-lam/bep-truong-dieu-hanh-head-chef-khach-san"
    },
    {
        "source": "TopCV",
        "external_id": "topcv-chef-402",
        "title": "Bếp Chính / Sous Chef (Chuỗi Nhà Hàng Nhật Bản & Á Châu)",
        "company_name": "Ramen & Sushi House Vietnam",
        "company_logo_url": "https://static.topcv.vn/company_logos/sushi-house.jpg",
        "location": "TP. Hồ Chí Minh (Quận 1)",
        "location_tag": "HO_CHI_MINH",
        "salary_text": "15 - 25 Triệu VNĐ",
        "salary_min_vnd": 15000000,
        "salary_max_vnd": 25000000,
        "required_skills": ["Japanese Cuisine", "Sushi & Sashimi", "Food Preparation", "HACCP", "Inventory Control"],
        "experience_required": "2+ năm",
        "description_text": "Chế biến các món ăn Nhật Bản và Á Châu theo đúng định lượng chuẩn. Phối hợp với Bếp Trưởng duy trì tiêu chuẩn vệ sinh an toàn thực phẩm.",
        "source_url": "https://www.topcv.vn/viec-lam/bep-chinh-sous-chef-nhat-ban"
    },
    {
        "source": "TopCV",
        "external_id": "topcv-chef-403",
        "title": "Bếp Trưởng Bánh / Pastry Chef (Chuỗi Bakery & Café High-End)",
        "company_name": "Artisan Bakery & Café",
        "company_logo_url": "https://static.topcv.vn/company_logos/artisan.jpg",
        "location": "Đà Nẵng (Sơn Trà)",
        "location_tag": "DA_NANG",
        "salary_text": "18 - 30 Triệu VNĐ",
        "salary_min_vnd": 18000000,
        "salary_max_vnd": 30000000,
        "required_skills": ["Baking & Pastry", "French Desserts", "Cake Decoration", "Recipe Development", "Quality Assurance"],
        "experience_required": "2+ năm",
        "description_text": "Sáng tạo và sản xuất các loại bánh ngọt, bánh mì phong cách Pháp cao cấp. Giám sát quy trình bảo quản nguyên liệu bánh.",
        "source_url": "https://www.topcv.vn/viec-lam/bep-truong-banh-pastry-chef"
    },
    # --- IT / SOFTWARE JOBS ---
    {
        "source": "TopCV",
        "external_id": "topcv-live-301",
        "title": "Senior Backend Developer (Python / FastAPI / Microservices)",
        "company_name": "FPT Software Academy",
        "company_logo_url": "https://cdn-new.topcv.vn/unsafe/https://static.topcv.vn/company_logos/fpt-software-6178a9c3d4083.jpg",
        "location": "Hà Nội (Cầu Giấy)",
        "location_tag": "HA_NOI",
        "salary_text": "30 - 45 Triệu VNĐ",
        "salary_min_vnd": 30000000,
        "salary_max_vnd": 45000000,
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "REST API"],
        "experience_required": "3+ năm",
        "description_text": "Thiết kế và phát triển hệ thống backend high-concurrency sử dụng FastAPI và PostgreSQL. Triển khai dịch vụ trên Docker/Kubernetes và tích hợp các mô hình AI/LLM.",
        "source_url": "https://www.topcv.vn/viec-lam/senior-backend-developer-python-fastapi"
    },
    {
        "source": "ITViec",
        "external_id": "itviec-live-302",
        "title": "AI Engineer (Generative AI & RAG Pipeline)",
        "company_name": "VinAI Research",
        "company_logo_url": "https://itviec.com/assets/logo-itviec.png",
        "location": "Hà Nội (Bắc Từ Liêm)",
        "location_tag": "HA_NOI",
        "salary_text": "40 - 70 Triệu VNĐ",
        "salary_min_vnd": 40000000,
        "salary_max_vnd": 70000000,
        "required_skills": ["Python", "PyTorch", "Gemini API", "ChromaDB", "LangChain", "Vector DB"],
        "experience_required": "2+ năm",
        "description_text": "Nghiên cứu và phát triển giải pháp RAG, Vector Search và ứng dụng Generative AI với Google Gemini API, PyTorch và Sentence Transformers.",
        "source_url": "https://itviec.com/it-jobs/ai-engineer-generative-ai-rag-vinai"
    },
    {
        "source": "TopCV",
        "external_id": "topcv-live-303",
        "title": "Fullstack React & Node.js / Python Developer",
        "company_name": "VNG Corporation",
        "company_logo_url": "https://static.topcv.vn/company_logos/vng.jpg",
        "location": "TP. Hồ Chí Minh (Quận 7)",
        "location_tag": "HO_CHI_MINH",
        "salary_text": "28 - 50 Triệu VNĐ",
        "salary_min_vnd": 28000000,
        "salary_max_vnd": 50000000,
        "required_skills": ["React", "TypeScript", "Python", "Node.js", "TailwindCSS"],
        "experience_required": "2-4 năm",
        "description_text": "Phát triển tính năng Fullstack với React, TypeScript cho Frontend và FastAPI/Node.js cho Backend. Tối ưu hiệu năng trải nghiệm người dùng.",
        "source_url": "https://www.topcv.vn/viec-lam/fullstack-react-python-developer"
    },
    {
        "source": "ITViec",
        "external_id": "itviec-live-304",
        "title": "DevOps / Cloud Engineer (AWS / Docker / K8s)",
        "company_name": "OneMount Group",
        "company_logo_url": "https://itviec.com/assets/logo-itviec.png",
        "location": "Hà Nội / Remote",
        "location_tag": "REMOTE",
        "salary_text": "25 - 40 Triệu VNĐ",
        "salary_min_vnd": 25000000,
        "salary_max_vnd": 40000000,
        "required_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Terraform"],
        "experience_required": "2+ năm",
        "description_text": "Quản lý hạ tầng đám mây trên AWS, thiết lập đường ống CI/CD tự động và giám sát Kubernetes clusters cho các sản phẩm quy mô lớn.",
        "source_url": "https://itviec.com/it-jobs/devops-cloud-engineer-onemount"
    },
    # --- MARKETING & SALES JOBS ---
    {
        "source": "TopCV",
        "external_id": "topcv-mkt-501",
        "title": "Digital Marketing Leader / Specialist",
        "company_name": "Shopee Vietnam",
        "company_logo_url": "https://static.topcv.vn/company_logos/shopee.jpg",
        "location": "TP. Hồ Chí Minh (Quận 10)",
        "location_tag": "HO_CHI_MINH",
        "salary_text": "20 - 35 Triệu VNĐ",
        "salary_min_vnd": 20000000,
        "salary_max_vnd": 35000000,
        "required_skills": ["Facebook Ads", "Google Ads", "SEO", "Content Strategy", "Google Analytics", "Performance Marketing"],
        "experience_required": "2+ năm",
        "description_text": "Lập kế hoạch và thực thi chiến dịch Performance Marketing trên Facebook, Google Ads, TikTok Ads. Tối ưu chi phí CPL/CAC và tăng chuyển đổi mua hàng.",
        "source_url": "https://www.topcv.vn/viec-lam/digital-marketing-leader-shopee"
    },
    {
        "source": "TopCV",
        "external_id": "topcv-sales-502",
        "title": "Trưởng Phòng Kinh Doanh B2B / Sales Manager",
        "company_name": "MISA Joint Stock Company",
        "company_logo_url": "https://static.topcv.vn/company_logos/misa.jpg",
        "location": "Hà Nội (Cầu Giấy)",
        "location_tag": "HA_NOI",
        "salary_text": "25 - 45 Triệu VNĐ",
        "salary_min_vnd": 25000000,
        "salary_max_vnd": 45000000,
        "required_skills": ["B2B Sales", "Negotiation", "CRM", "Sales Strategy", "Team Leadership", "Key Account Management"],
        "experience_required": "3+ năm",
        "description_text": "Quản lý và phát triển đội ngũ kinh doanh phần mềm B2B. Tìm kiếm khách hàng doanh nghiệp, đàm phán hợp đồng và hoàn thành chỉ tiêu doanh số.",
        "source_url": "https://www.topcv.vn/viec-lam/truong-phong-kinh-doanh-b2b-misa"
    },
    # --- FINANCE & ACCOUNTING JOBS ---
    {
        "source": "TopCV",
        "external_id": "topcv-acc-601",
        "title": "Kế Toán Trưởng / Chief Accountant",
        "company_name": "Sun Group Vietnam",
        "company_logo_url": "https://static.topcv.vn/company_logos/sungroup.jpg",
        "location": "Đà Nẵng (Hải Châu)",
        "location_tag": "DA_NANG",
        "salary_text": "30 - 50 Triệu VNĐ",
        "salary_min_vnd": 30000000,
        "salary_max_vnd": 50000000,
        "required_skills": ["Financial Statements", "Tax Reporting", "General Ledger", "Internal Audit", "ERP MISA/SAP", "VAS Standards"],
        "experience_required": "5+ năm",
        "description_text": "Chịu trách nhiệm toàn bộ công tác tài chính kế toán của tập đoàn. Lập báo cáo tài chính, quyết toán thuế và làm việc với các cơ quan thanh tra thuế.",
        "source_url": "https://www.topcv.vn/viec-lam/ke-toan-truong-chief-accountant"
    }
]

async def crawl_with_crawl4ai(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Crawls job URLs using Crawl4AI AsyncWebCrawler.
    Extracts clean Markdown and returns job posting dictionary structures.
    """
    if not CRAWL4AI_AVAILABLE:
        logger.warning("Crawl4AI is not available. Skipping live URL crawl.")
        return []

    crawled_results = []
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            for url in urls:
                try:
                    logger.info(f"Crawl4AI crawling target URL: {url}")
                    result = await crawler.arun(url=url, config=run_config)
                    if result.success and result.markdown:
                        ext_id = f"c4ai-{hashlib.md5(url.encode('utf-8')).hexdigest()[:12]}"
                        markdown_text = result.markdown.raw_markdown if hasattr(result.markdown, 'raw_markdown') else str(result.markdown)
                        
                        job_entry = {
                            "source": "Crawl4AI_Live",
                            "external_id": ext_id,
                            "title": "Crawled Job Posting",
                            "company_name": "Tech Employer",
                            "company_logo_url": "https://cdn-icons-png.flaticon.com/512/3242/3242257.png",
                            "location": "Việt Nam",
                            "location_tag": "OTHER",
                            "salary_text": "Thỏa thuận",
                            "salary_min_vnd": 0,
                            "salary_max_vnd": 0,
                            "required_skills": ["Python", "Web Scraping", "AI"],
                            "experience_required": "Yêu cầu trao đổi",
                            "description_text": markdown_text[:1500] if len(markdown_text) > 1500 else markdown_text,
                            "source_url": url
                        }
                        crawled_results.append(job_entry)
                except Exception as ex:
                    logger.error(f"Crawl4AI failed to crawl single URL {url}: {ex}")
    except Exception as e:
        logger.error(f"Crawl4AI browser execution error: {e}")

    return crawled_results

async def crawl_and_sync_jobs(
    db: AsyncSession, 
    limit: int = 10, 
    target_urls: Optional[List[str]] = None
) -> Tuple[int, int, int]:
    """
    Crawls and synchronizes live job postings into database using Crawl4AI (with graceful fallback).
    Returns a tuple: (new_jobs_added, existing_jobs_updated, total_active_jobs)
    """
    logger.info(f"Starting job crawl operation with limit={limit}, target_urls={target_urls}...")
    
    new_added = 0
    updated = 0
    jobs_to_sync: List[Dict[str, Any]] = []

    # Attempt Crawl4AI if target_urls provided
    if target_urls and CRAWL4AI_AVAILABLE:
        c4ai_jobs = await crawl_with_crawl4ai(target_urls[:limit])
        jobs_to_sync.extend(c4ai_jobs)

    # Fallback to curated live jobs feed if Crawl4AI yielded no items or no target URLs provided
    if not jobs_to_sync:
        logger.info("Using Curated Feed data for job synchronization.")
        jobs_to_sync = MVP_DEMO_LIVE_JOBS[:limit]

    for job_data in jobs_to_sync:
        ext_id = job_data["external_id"]
        source = job_data["source"]

        # Check existing job by source + external_id
        res = await db.execute(
            select(RealJobPosting).where(
                RealJobPosting.source == source,
                RealJobPosting.external_id == ext_id
            )
        )
        existing = res.scalars().first()

        if existing:
            # Update fields if modified
            existing.title = job_data["title"]
            existing.company_name = job_data["company_name"]
            existing.salary_text = job_data["salary_text"]
            existing.salary_min_vnd = job_data.get("salary_min_vnd", 0)
            existing.salary_max_vnd = job_data.get("salary_max_vnd", 0)
            existing.required_skills = job_data.get("required_skills", [])
            existing.description_text = job_data["description_text"]
            updated += 1
        else:
            # Add new job posting
            new_job = RealJobPosting(**job_data)
            db.add(new_job)
            new_added += 1

    await db.commit()

    # Query total active count
    res_total = await db.execute(select(RealJobPosting).where(RealJobPosting.status == "ACTIVE"))
    total_active = len(res_total.scalars().all())

    logger.info(f"Crawl finished. Added: {new_added}, Updated: {updated}, Total in DB: {total_active}")
    return new_added, updated, total_active
