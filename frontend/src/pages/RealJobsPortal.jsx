import React, { useState, useEffect } from 'react';
import { Sparkles, UploadCloud, Loader2, RefreshCw } from 'lucide-react';
import RealJobCard from '../components/RealJobCard';
import RealJobFilters from '../components/RealJobFilters';

export default function RealJobsPortal() {
  const [cvFile, setCvFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [crawling, setCrawling] = useState(false);
  const [crawlStatusMsg, setCrawlStatusMsg] = useState('');
  const [matchResults, setMatchResults] = useState([]);
  const [hasScanned, setHasScanned] = useState(false);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [locationFilter, setLocationFilter] = useState('ALL');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [minScore, setMinScore] = useState(0);

  // Initial load: fetch un-matched real jobs
  useEffect(() => {
    fetchInitialJobs();
  }, []);

  const fetchInitialJobs = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/real-jobs');
      const data = await res.json();
      setMatchResults(data.map((j) => ({
        real_job: j,
        match_score: null,
        skills_sub_score: null,
        experience_sub_score: null,
        strengths_summary: [],
        gaps_summary: [],
        match_reasoning: "Tải lên CV PDF để kích hoạt chấm điểm AI riêng cho bạn."
      })));
    } catch (err) {
      console.error(err);
    }
  };

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, locationFilter, categoryFilter, minScore, matchResults]);

  const handleCrawlJobs = async () => {
    setCrawling(true);
    setCrawlStatusMsg('');
    try {
      const res = await fetch('http://127.0.0.1:8000/api/real-jobs/crawl?limit=50', {
        method: 'POST'
      });
      if (!res.ok) throw new Error('Lấy dữ liệu thất bại');
      const data = await res.json();
      setCrawlStatusMsg(data.message || 'Đã lấy dữ liệu việc làm đa ngành thành công!');
      await fetchInitialJobs();
    } catch (err) {
      setCrawlStatusMsg('Lỗi Lấy dữ liệu: ' + err.message);
    } finally {
      setCrawling(false);
    }
  };

  const handleScanJobs = async (e) => {
    e.preventDefault();
    setLoading(true);
    setHasScanned(true);

    try {
      const formData = new FormData();
      if (cvFile) {
        formData.append('file', cvFile);
      }

      const res = await fetch('http://127.0.0.1:8000/api/real-jobs/match', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) throw new Error('Không thể quét công việc');
      const data = await res.json();
      setMatchResults(data);
    } catch (err) {
      alert('Lỗi quét việc: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const detectedCvDomain = matchResults.length > 0 ? matchResults[0].cv_domain : null;

  const filteredMatches = matchResults.filter((m) => {
    const job = m.real_job;
    const titleLower = (job.title || '').toLowerCase();
    const skillsText = (job.required_skills || []).join(' ').toLowerCase();
    const descLower = (job.description_text || '').toLowerCase();

    const matchesSearch =
      titleLower.includes(searchQuery.toLowerCase()) ||
      (job.company_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      skillsText.includes(searchQuery.toLowerCase());

    const matchesLoc = locationFilter === 'ALL' || job.location_tag === locationFilter;
    const matchesScore = m.match_score === null || m.match_score === undefined || m.match_score >= minScore;

    let matchesCategory = true;
    if (categoryFilter === 'CHEF') {
      matchesCategory = titleLower.includes('bếp') || titleLower.includes('chef') || skillsText.includes('culinary') || descLower.includes('bếp');
    } else if (categoryFilter === 'IT') {
      matchesCategory = titleLower.includes('developer') || titleLower.includes('engineer') || titleLower.includes('ai') || titleLower.includes('python') || titleLower.includes('react') || titleLower.includes('qa') || titleLower.includes('tester') || titleLower.includes('product owner') || titleLower.includes('pm') || titleLower.includes('devops') || titleLower.includes('design') || titleLower.includes('data');
    } else if (categoryFilter === 'MARKETING') {
      matchesCategory = titleLower.includes('marketing') || titleLower.includes('seo') || titleLower.includes('content');
    } else if (categoryFilter === 'SALES') {
      matchesCategory = titleLower.includes('sales') || titleLower.includes('kinh doanh') || titleLower.includes('account');
    } else if (categoryFilter === 'FINANCE') {
      matchesCategory = titleLower.includes('kế toán') || titleLower.includes('tài chính') || titleLower.includes('accountant');
    }

    return matchesSearch && matchesLoc && matchesScore && matchesCategory;
  });

  // Calculate Pagination values
  const totalItems = filteredMatches.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const validCurrentPage = Math.min(currentPage, totalPages);
  const startIndex = (validCurrentPage - 1) * pageSize;
  const paginatedMatches = filteredMatches.slice(startIndex, startIndex + pageSize);

  return (
    <div className="jobs-page animate-fade-in">

      {/* Hero Header */}
      <div className="jobs-hero">
        <div className="jobs-hero__copy">
          <span className="page-kicker">Việc làm dành riêng cho bạn</span>
          <h2>Tìm công việc phù hợp với năng lực của bạn</h2>
          <p>Đối chiếu CV với cơ hội mới nhất từ TopCV và ITViec. AI giúp bạn hiểu mức độ phù hợp trước khi ứng tuyển.</p>
        </div>

        {/* Upload & Crawl Control Bar */}
        <form onSubmit={handleScanJobs} className="jobs-hero__actions">
          <div style={{ position: 'relative' }}>
            <input
              type="file"
              accept=".pdf"
              id="cv-upload-realjobs"
              onChange={(e) => setCvFile(e.target.files ? e.target.files[0] : null)}
              style={{ display: 'none' }}
            />
            <label
              htmlFor="cv-upload-realjobs"
              className="btn btn-secondary"
              style={{ cursor: 'pointer', padding: '10px 18px', fontSize: '0.9rem' }}
            >
              <UploadCloud size={18} color="var(--accent-cyan)" />
              {cvFile ? cvFile.name : 'Chọn CV (PDF)'}
            </label>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading} style={{ padding: '10px 24px', fontSize: '0.9rem' }}>
            {loading ? (
              <>
                <Loader2 size={18} className="spin" /> Đang phân tích CV...
              </>
            ) : (
              <>
                <Sparkles size={18} /> Gợi ý việc phù hợp
              </>
            )}
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleCrawlJobs}
            disabled={crawling}
            style={{ padding: '10px 18px', fontSize: '0.9rem', borderColor: 'var(--accent-cyan)', color: 'var(--accent-cyan)' }}
          >
            {crawling ? (
              <>
                <Loader2 size={18} className="spin" /> Đang cập nhật dữ liệu...
              </>
            ) : (
              <>
                <RefreshCw size={18} /> Cập nhật việc làm
              </>
            )}
          </button>
        </form>

        {crawlStatusMsg && (
          <div className="inline-notice">
            {crawlStatusMsg}
          </div>
        )}

        {hasScanned && detectedCvDomain && (
          <div style={{
            marginTop: '16px',
            padding: '12px 20px',
            borderRadius: '12px',
            background: '#e5f6ef',
            border: '1px solid var(--accent-cyan)',
            color: 'var(--accent-primary-dark)',
            fontSize: '0.9rem',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Sparkles size={18} color="var(--accent-cyan)" />
            <span>AI nhận diện chuyên môn: <b>{detectedCvDomain}</b>. Danh sách đã được xếp theo độ phù hợp.</span>
          </div>
        )}
      </div>

      {/* Filter Bar */}
      <RealJobFilters
        minScore={minScore}
        setMinScore={setMinScore}
        locationFilter={locationFilter}
        setLocationFilter={setLocationFilter}
        categoryFilter={categoryFilter}
        setCategoryFilter={setCategoryFilter}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
      />

      {/* Job Results Header Info & Page Size Select */}
      <div className="glass-panel" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', padding: '12px 20px' }}>
        <div>
          <h4 style={{ fontSize: '1rem', fontWeight: 700, margin: 0 }}>
            {hasScanned ? 'Công việc phù hợp nhất với CV của bạn' : 'Cơ hội việc làm mới nhất'}
          </h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '2px 0 0' }}>
            Hiển thị <b>{totalItems > 0 ? startIndex + 1 : 0} - {Math.min(startIndex + pageSize, totalItems)}</b> trong tổng số <b>{totalItems}</b> vị trí tuyển dụng
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {hasScanned && <span className="badge badge-shortlisted">Đã quét & Rerank bởi AI</span>}

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            <span>Hiển thị:</span>
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
              style={{
                background: '#fff',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                padding: '4px 8px',
                fontSize: '0.8rem',
                cursor: 'pointer'
              }}
            >
              <option value={5}>5 vị trí/trang</option>
              <option value={10}>10 vị trí/trang</option>
              <option value={20}>20 vị trí/trang</option>
              <option value={999}>Tất cả ({totalItems})</option>
            </select>
          </div>
        </div>
      </div>

      {/* Job Cards List */}
      {paginatedMatches.length === 0 ? (
        <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
          Không tìm thấy vị trí tuyển dụng phù hợp với bộ lọc hiện tại.
        </div>
      ) : (
        paginatedMatches.map((m, idx) => (
          <RealJobCard key={m.real_job.id || idx} matchData={m} />
        ))
      )}

      {/* Pagination Footer Controls */}
      {totalPages > 1 && (
        <div className="glass-panel" style={{
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center',
          padding: '12px 20px',
          marginTop: '20px',
          borderRadius: '12px'
        }}>
          <button
            className="btn btn-secondary"
            onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
            disabled={validCurrentPage === 1}
            style={{ fontSize: '0.85rem', padding: '6px 14px' }}
          >
            ← Trang trước
          </button>

          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((pg) => (
              <button
                key={pg}
                onClick={() => setCurrentPage(pg)}
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  border: pg === validCurrentPage ? '1px solid var(--accent-cyan)' : '1px solid var(--border-color)',
                  background: pg === validCurrentPage ? 'var(--accent-primary)' : '#fff',
                  color: pg === validCurrentPage ? '#fff' : 'var(--text-primary)',
                  fontWeight: pg === validCurrentPage ? 700 : 400,
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  transition: 'all 0.2s ease'
                }}
              >
                {pg}
              </button>
            ))}
          </div>

          <button
            className="btn btn-secondary"
            onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
            disabled={validCurrentPage === totalPages}
            style={{ fontSize: '0.85rem', padding: '6px 14px' }}
          >
            Trang sau →
          </button>
        </div>
      )}

    </div>
  );
}

