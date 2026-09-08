import React, { useState, useEffect } from 'react';
import { Search, Sparkles, UploadCloud, FileText, Loader2, Globe, RefreshCw, Bot } from 'lucide-react';
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

  const handleCrawlJobs = async () => {
    setCrawling(true);
    setCrawlStatusMsg('');
    try {
      const res = await fetch('http://127.0.0.1:8000/api/real-jobs/crawl?limit=10', {
        method: 'POST'
      });
      if (!res.ok) throw new Error('Cào dữ liệu thất bại');
      const data = await res.json();
      setCrawlStatusMsg(data.message || 'Đã cào dữ liệu việc làm đa ngành thành công!');
      await fetchInitialJobs();
    } catch (err) {
      setCrawlStatusMsg('Lỗi cào dữ liệu: ' + err.message);
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

  return (
    <div className="animate-fade-in" style={{ maxWidth: '1050px', margin: '0 auto' }}>
      
      {/* Hero Header */}
      <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px', textAlign: 'center' }}>
        <div style={{
          width: '52px', height: '52px', borderRadius: '16px', background: 'var(--accent-gradient)',
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '12px'
        }}>
          <Globe size={28} color="#fff" />
        </div>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Tìm Việc Thật Đa Ngành Trực Tiếp từ TopCV & ITViec</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: '650px', margin: '8px auto 0' }}>
          Tải CV của bạn (Đầu bếp, IT, Marketing, Sales, Kế toán...) để Động cơ AI quét toàn bộ công việc thực tế, phân loại đúng ngành nghề và chấm điểm độ phù hợp (%).
        </p>

        {/* Upload & Crawl Control Bar */}
        <form onSubmit={handleScanJobs} style={{ marginTop: '20px', display: 'flex', flexWrap: 'wrap', gap: '12px', justifyContent: 'center', alignItems: 'center' }}>
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
              {cvFile ? cvFile.name : 'Chọn File CV (PDF)'}
            </label>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading} style={{ padding: '10px 24px', fontSize: '0.9rem' }}>
            {loading ? (
              <>
                <Loader2 size={18} className="spin" /> Đang Phân tích & Quét Việc Thật...
              </>
            ) : (
              <>
                <Sparkles size={18} /> Quét Việc Thật Phù Hợp Với CV
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
                <Loader2 size={18} className="spin" /> Đang Cào Dữ Liệu Đa Ngành...
              </>
            ) : (
              <>
                <Bot size={18} /> Crawl Dữ Liệu Việc Làm Đa Ngành (MVP Bot)
              </>
            )}
          </button>
        </form>

        {crawlStatusMsg && (
          <div style={{ marginTop: '12px', padding: '8px 16px', borderRadius: '8px', background: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', fontSize: '0.85rem', display: 'inline-block' }}>
            {crawlStatusMsg}
          </div>
        )}

        {hasScanned && detectedCvDomain && (
          <div style={{
            marginTop: '16px',
            padding: '12px 20px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%)',
            border: '1px solid var(--accent-cyan)',
            color: '#fff',
            fontSize: '0.9rem',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Sparkles size={18} color="var(--accent-cyan)" />
            <span>🧠 AI Nhận diện CV thuộc ngành: <b>{detectedCvDomain}</b>. Đã tự động lọc và gợi ý công việc phù hợp nhất!</span>
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

      {/* Job Results Count */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', padding: '0 4px' }}>
        <h4 style={{ fontSize: '1rem', fontWeight: 700 }}>
          {hasScanned ? 'Công việc Thật Phù hợp nhất với CV của bạn' : 'Danh sách Công việc Thật Mới nhất'} ({filteredMatches.length})
        </h4>
        {hasScanned && <span className="badge badge-shortlisted">Đã quét & Rerank bởi AI</span>}
      </div>

      {/* Job Cards List */}
      {filteredMatches.length === 0 ? (
        <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
          Không tìm thấy vị trí tuyển dụng phù hợp với bộ lọc hiện tại.
        </div>
      ) : (
        filteredMatches.map((m, idx) => (
          <RealJobCard key={m.real_job.id || idx} matchData={m} />
        ))
      )}

    </div>
  );
}

