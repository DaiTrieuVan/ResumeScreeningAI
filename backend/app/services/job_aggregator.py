# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.real_job import RealJobPosting

logger = logging.getLogger(__name__)

# Sample Multi-Industry Real-World Job Feed for TopCV & ITViec Vietnam
CURATED_REAL_JOBS: List[Dict[str, Any]] = [
    # --- F&B / CHEF / CULINARY JOBS ---
    {
        "source": "TopCV",
        "external_id": "topcv-chef-101",
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
        "source_url": "https://www.topcv.vn/tim-viec-lam?keyword=Head+Chef"
    },
    {
        "source": "TopCV",
        "external_id": "topcv-chef-102",
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
        "source_url": "https://www.topcv.vn/tim-viec-lam?keyword=Sous+Chef"
    },
    {
        "source": "TopCV",
        "external_id": "topcv-chef-103",
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
        "source_url": "https://www.topcv.vn/tim-viec-lam?keyword=Pastry+Chef"
    },
    # --- IT / SOFTWARE JOBS ---
    {
        "source": "TopCV",
        "external_id": "topcv-qa-701",
        "title": "QA Specialist / Tester",
        "company_name": "CÔNG TY TNHH TRUESON APAC",
        "company_logo_url": "https://static.topcv.vn/company_logos/trueson.jpg",
        "location": "TP. Hồ Chí Minh",
        "location_tag": "HO_CHI_MINH",
        "salary_text": "15 - 25 Triệu VNĐ",
        "salary_min_vnd": 15000000,
        "salary_max_vnd": 25000000,
        "required_skills": ["Software Testing", "QA", "Manual Testing", "Automation Testing", "Test Cases", "Bug Tracking"],
        "experience_required": "1 năm",
        "description_text": "Thực hiện kiểm thử phần mềm, lập test plan, test case và phối hợp với đội ngũ Developer để theo dõi, xử lý lỗi trên hệ thống.",
        "source_url": "https://www.topcv.vn/tim-viec-lam?keyword=QA+Specialist+Tester"
    },
    {
        "source": "TopCV",
        "external_id": "topcv-pm-702",
        "title": "Product Owner / Project Manager / PM Dự Án Robot",
        "company_name": "CÔNG TY TNHH HORUS PRODUCTIONS",
        "company_logo_url": "https://static.topcv.vn/company_logos/horus.jpg",
        "location": "Hà Nội",
        "location_tag": "HA_NOI",
        "salary_text": "25 - 70 Triệu VNĐ",
        "salary_min_vnd": 25000000,
        "salary_max_vnd": 70000000,
        "required_skills": ["Agile/Scrum", "Project Management", "Product Roadmap", "Robotics/AI", "Jira", "Backlog Grooming"],
        "experience_required": "3 năm",
        "description_text": "Quản lý tiến độ dự án Robot tự động hóa, lập định hướng phát triển sản phẩm, làm việc với đối tác và quản lý đội ngũ kỹ sư.",
        "source_url": "https://www.topcv.vn/tim-viec-lam?keyword=Product+Owner+Project+Manager"
    },
    {
        "source": "TopCV",
        "external_id": "topcv-devops-703",
        "title": "Senior DevOps / Cloud Infrastructure Engineer Upto 50M",
        "company_name": "CÔNG TY TNHH VODAPLAY VIỆT NAM",
        "company_logo_url": "https://static.topcv.vn/company_logos/vodaplay.jpg",
        "location": "Hà Nội",
        "location_tag": "HA_NOI",
        "salary_text": "30 - 50 Triệu VNĐ",
        "salary_min_vnd": 30000000,
        "salary_max_vnd": 50000000,
        "required_skills": ["DevOps", "Cloud Infrastructure", "Docker", "Kubernetes", "CI/CD", "AWS", "Linux"],
        "experience_required": "4 năm",
        "description_text": "Xây dựng và tối ưu hạ tầng Cloud trên AWS/GCP, triển khai hệ thống Kubernetes clusters và đường ống CI/CD tự động hóa.",
        "source_url": "https://www.topcv.vn/tim-viec-lam?keyword=Senior+DevOps+Cloud+Infrastructure+Engineer"
    },
    {
        "source": "TopCV",
        "external_id": "topcv-design-704",
        "title": "Graphic Designer",
        "company_name": "CÔNG TY TNHH DH VENTURES VIETNAM",
        "company_logo_url": "https://static.topcv.vn/company_logos/dhventures.jpg",
        "location": "TP. Hồ Chí Minh",
        "location_tag": "HO_CHI_MINH",
        "salary_text": "12 - 18 Triệu VNĐ",
        "salary_min_vnd": 12000000,
        "salary_max_vnd": 18000000,
        "required_skills": ["Photoshop", "Illustrator", "UI/UX Design", "Branding", "Graphic Design", "Figma"],
        "experience_required": "1 năm",
        "description_text": "Thiết kế bộ nhận diện thương hiệu, hình ảnh marketing, banner và giao diện truyền thông kỹ thuật số cho các chiến dịch của công ty.",
        "source_url": "https://www.topcv.vn/tim-viec-lam?keyword=Graphic+Designer"
    },
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
        "source_url": "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?category_family=r257"
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
        "source_url": "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?category_family=r257"
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
        "source_url": "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?category_family=r257"
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
        "source_url": "https://www.topcv.vn/tim-viec-lam?keyword=Digital+Marketing"
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
        "source_url": "https://www.topcv.vn/tim-viec-lam?keyword=Sales+Manager"
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
        "source_url": "https://www.topcv.vn/tim-viec-lam?keyword=Ke+Toan+Truong"
    }
]

async def seed_real_jobs_if_empty(db: AsyncSession) -> int:
    """
    Seeds and syncs curated real jobs across all major industries into RealJobPosting database.
    Updates existing records' source_url if changed.
    """
    res = await db.execute(select(RealJobPosting))
    existing_jobs = res.scalars().all()
    existing_map = {j.external_id: j for j in existing_jobs}

    count = 0
    updated = 0
    for job_data in CURATED_REAL_JOBS:
        ext_id = job_data["external_id"]
        if ext_id not in existing_map:
            job = RealJobPosting(**job_data)
            db.add(job)
            count += 1
        else:
            existing_job = existing_map[ext_id]
            if existing_job.source_url != job_data["source_url"]:
                existing_job.source_url = job_data["source_url"]
                updated += 1

    if count > 0 or updated > 0:
        await db.commit()
        logger.info(f"Seeded/Updated real jobs: {count} new, {updated} updated source URLs.")

    return len(existing_map) + count
