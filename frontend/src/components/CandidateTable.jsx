import React, { useState, useEffect } from 'react';
import { Search, Eye, Filter, SlidersHorizontal, ChevronLeft, ChevronRight, Award, Zap } from 'lucide-react';
import { updateCandidateStatus } from '../services/api';

export default function CandidateTable({ candidates, jobWeights, onSelectCandidate, onStatusChange }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [minScore, setMinScore] = useState(0);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 10;

  // Reset to page 1 whenever filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, minScore, statusFilter]);

  // Compute live overall score based on current slider weights if jobWeights are adjusted
  const getLiveScore = (cand) => {
    if (!jobWeights) return cand.overall_score;
    const { wSkills, wExp, wEdu } = jobWeights;
    const live = (cand.skills_sub_score * wSkills) + (cand.experience_sub_score * wExp) + (cand.education_sub_score * wEdu);
    return Math.round(live * 10) / 10;
  };

  const filteredCandidates = candidates.filter((c) => {
    const score = getLiveScore(c);
    const matchesSearch = 
      (c.candidate_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.strengths_summary || []).some(s => s.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesMinScore = score >= minScore;
    const matchesStatus = statusFilter === 'ALL' || c.recruiter_status === statusFilter;

    return matchesSearch && matchesMinScore && matchesStatus;
  });

  const totalPages = Math.ceil(filteredCandidates.length / ITEMS_PER_PAGE) || 1;
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const paginatedCandidates = filteredCandidates.slice(startIndex, endIndex);

  // Helper for smart compact pagination with ellipsis (...)
  const getPaginationRange = (current, total) => {
    if (total <= 7) {
      return Array.from({ length: total }, (_, i) => i + 1);
    }

    const pages = [];
    pages.push(1);

    if (current > 3) {
      pages.push('...');
    }

    const start = Math.max(2, current - 1);
    const end = Math.min(total - 1, current + 1);

    for (let i = start; i <= end; i++) {
      if (!pages.includes(i)) {
        pages.push(i);
      }
    }

    if (current < total - 2) {
      pages.push('...');
    }

    if (!pages.includes(total)) {
      pages.push(total);
    }

    return pages;
  };

  const getScoreBadgeClass = (score) => {
    if (score >= 80) return 'score-high';
    if (score >= 60) return 'score-medium';
    return 'score-low';
  };

  const getStatusBadgeClass = (st) => {
    switch (st) {
      case 'SHORTLISTED': return 'badge-shortlisted';
      case 'UNDER_REVIEW': return 'badge-review';
      case 'REJECTED': return 'badge-rejected';
      default: return 'badge-new';
    }
  };

  const handleStatusSelect = async (candidate, newStatus) => {
    try {
      const updated = await updateCandidateStatus(candidate.id, newStatus);
      if (onStatusChange) onStatusChange(updated);
    } catch (err) {
      alert('Cập nhật trạng thái thất bại: ' + err.message);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      
      {/* Filter Bar */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: '1', minWidth: '260px' }}>
          <div style={{ position: 'relative', width: '100%' }}>
            <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              className="input-field"
              placeholder="Tìm kiếm tên ứng viên hoặc kỹ năng..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ paddingLeft: '38px' }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          
          {/* Min Score Threshold Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}>
            <SlidersHorizontal size={14} color="var(--accent-cyan)" />
            <span>Điểm tối thiểu: <b>{minScore}%</b></span>
            <input
              type="range"
              min="0"
              max="95"
              step="5"
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              style={{ width: '100px' }}
            />
          </div>

          {/* Status Dropdown Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
            <Filter size={14} color="var(--text-muted)" />
            <select
              className="select-field"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{ padding: '6px 12px', width: 'auto' }}
            >
              <option value="ALL">Tất cả trạng thái</option>
              <option value="NEW">Mới (New)</option>
              <option value="SHORTLISTED">Đã chọn lọc (Shortlisted)</option>
              <option value="UNDER_REVIEW">Đang xem xét (Under Review)</option>
              <option value="REJECTED">Từ chối (Rejected)</option>
            </select>
          </div>

        </div>

      </div>

      {/* Candidate Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
              <th style={{ padding: '12px 16px' }}>Ứng viên</th>
              <th style={{ padding: '12px 16px' }}>Điểm Phù hợp Tổng thể</th>
              <th style={{ padding: '12px 16px' }}>Khớp Kỹ năng</th>
              <th style={{ padding: '12px 16px' }}>Kinh nghiệm</th>
              <th style={{ padding: '12px 16px' }}>Trạng thái</th>
              <th style={{ padding: '12px 16px', textAlign: 'right' }}>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {paginatedCandidates.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  Không có ứng viên nào phù hợp với bộ lọc hiện tại.
                </td>
              </tr>
            ) : (
              paginatedCandidates.map((cand) => {
                const liveScore = getLiveScore(cand);
                return (
                  <tr
                    key={cand.id}
                    style={{
                      borderBottom: '1px solid var(--border-color)',
                      transition: 'var(--transition)'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                        <span>{cand.candidate_name}</span>
                        {cand.honors_badges && cand.honors_badges.map((badge, idx) => (
                          <span
                            key={idx}
                            style={{
                              fontSize: '0.68rem',
                              padding: '2px 8px',
                              borderRadius: '12px',
                              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                              color: '#fff',
                              fontWeight: 700,
                              boxShadow: '0 2px 6px rgba(245, 158, 11, 0.3)',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}
                          >
                            <Award size={12} /> {badge}
                          </span>
                        ))}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{cand.candidate_email || cand.candidate_file_name}</div>
                      {(cand.skills_summary || cand.experience_summary) && (
                        <div style={{ fontSize: '0.72rem', color: 'var(--accent-cyan)', marginTop: '4px', maxWidth: '280px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Zap size={12} style={{ shrink: 0 }} /> {cand.skills_summary || cand.experience_summary}
                        </div>
                      )}
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                        <span className={`score-pill ${getScoreBadgeClass(liveScore)}`}>
                          {liveScore}%
                        </span>
                        {cand.stage1_similarity_score > 0 && (
                          <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '4px', fontFamily: 'var(--font-mono)' }} title="Vector Similarity Tie-Breaker">
                            Vector: {Math.round(cand.stage1_similarity_score * 10) / 10}%
                          </span>
                        )}
                      </div>
                    </td>

                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)' }}>
                      <div>{cand.skills_sub_score}%</div>
                      {cand.skills_summary && (
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 400, fontFamily: 'sans-serif', maxWidth: '120px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={cand.skills_summary}>
                          {cand.skills_summary}
                        </div>
                      )}
                    </td>

                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)' }}>
                      <div>{cand.experience_sub_score}%</div>
                      {cand.experience_summary && (
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 400, fontFamily: 'sans-serif', maxWidth: '120px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={cand.experience_summary}>
                          {cand.experience_summary}
                        </div>
                      )}
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      <select
                        value={cand.recruiter_status}
                        onChange={(e) => handleStatusSelect(cand, e.target.value)}
                        className={`badge ${getStatusBadgeClass(cand.recruiter_status)}`}
                        style={{ border: 'none', cursor: 'pointer', outline: 'none' }}
                      >
                        <option value="NEW">MỚI</option>
                        <option value="SHORTLISTED">ĐÃ CHỌN LỌC</option>
                        <option value="UNDER_REVIEW">ĐANG XEM XÉT</option>
                        <option value="REJECTED">TỪ CHỐI</option>
                      </select>
                    </td>

                    <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                      <button
                        onClick={() => onSelectCandidate(cand)}
                        className="btn btn-secondary"
                        style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                      >
                        <Eye size={14} /> Phân tích AI
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {filteredCandidates.length > 0 && (
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '12px',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginTop: '20px',
          paddingTop: '16px',
          borderTop: '1px solid var(--border-color)',
          fontSize: '0.85rem',
          color: 'var(--text-muted)'
        }}>
          <div>
            Hiển thị <b>{startIndex + 1}</b> - <b>{Math.min(endIndex, filteredCandidates.length)}</b> trong tổng số <b>{filteredCandidates.length}</b> ứng viên
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
            <button
              onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
              disabled={currentPage === 1}
              className="btn btn-secondary"
              style={{
                padding: '4px 10px',
                fontSize: '0.8rem',
                opacity: currentPage === 1 ? 0.5 : 1,
                cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
              }}
            >
              <ChevronLeft size={14} /> Trang trước
            </button>

            {getPaginationRange(currentPage, totalPages).map((item, idx) => {
              if (item === '...') {
                return (
                  <span key={`ellipsis-${idx}`} style={{ padding: '0 4px', color: 'var(--text-muted)', fontWeight: 600 }}>
                    ...
                  </span>
                );
              }
              return (
                <button
                  key={item}
                  onClick={() => setCurrentPage(item)}
                  style={{
                    padding: '4px 10px',
                    minWidth: '32px',
                    borderRadius: '6px',
                    border: '1px solid var(--border-color)',
                    background: currentPage === item ? 'var(--accent-primary)' : 'rgba(255, 255, 255, 0.05)',
                    color: '#fff',
                    fontWeight: currentPage === item ? 700 : 400,
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                    transition: 'var(--transition)'
                  }}
                >
                  {item}
                </button>
              );
            })}

            <button
              onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="btn btn-secondary"
              style={{
                padding: '4px 10px',
                fontSize: '0.8rem',
                opacity: currentPage === totalPages ? 0.5 : 1,
                cursor: currentPage === totalPages ? 'not-allowed' : 'pointer'
              }}
            >
              Trang sau <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}

    </div>
  );
}
