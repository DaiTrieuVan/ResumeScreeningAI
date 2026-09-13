import React, { useState, useEffect } from 'react';
import { PlusCircle, Edit3, Sliders, X } from 'lucide-react';
import { createJob, updateJob } from '../services/api';

export default function JobPostingForm({ initialData = null, onJobSaved, onClose }) {
  const isEdit = Boolean(initialData && initialData.id);

  const [title, setTitle] = useState(initialData?.title || '');
  const [department, setDepartment] = useState(initialData?.department || '');
  const [skillsInput, setSkillsInput] = useState(
    Array.isArray(initialData?.required_skills) ? initialData.required_skills.join(', ') : ''
  );
  const [minExp, setMinExp] = useState(initialData?.min_years_experience ?? 3);
  const [education, setEducation] = useState(initialData?.required_education || "Cử nhân CNTT hoặc ngành liên quan");
  
  // Weights (Skills, Exp, Edu)
  const [wSkills, setWSkills] = useState(
    initialData?.weight_skills ? Math.round(initialData.weight_skills * 100) : 50
  );
  const [wExp, setWExp] = useState(
    initialData?.weight_experience ? Math.round(initialData.weight_experience * 100) : 35
  );
  const [wEdu, setWEdu] = useState(
    initialData?.weight_education ? Math.round(initialData.weight_education * 100) : 15
  );
  
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !skillsInput.trim()) return;

    setLoading(true);
    try {
      const skillsArray = skillsInput.split(',').map(s => s.trim()).filter(Boolean);
      
      const payload = {
        title,
        department,
        required_skills: skillsArray,
        min_years_experience: parseInt(minExp, 10),
        required_education: education,
        weight_skills: wSkills / 100,
        weight_experience: wExp / 100,
        weight_education: wEdu / 100
      };

      let saved;
      if (isEdit) {
        saved = await updateJob(initialData.id, payload);
      } else {
        saved = await createJob(payload);
      }
      onJobSaved(saved);
    } catch (err) {
      alert(`Lỗi ${isEdit ? 'cập nhật' : 'tạo'} vị trí tuyển dụng: ` + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" role="presentation">
      <div className="glass-panel modal-card animate-fade-in" role="dialog" aria-modal="true" aria-label={isEdit ? 'Chỉnh sửa yêu cầu tuyển dụng' : 'Tạo yêu cầu tuyển dụng'} style={{ width: '100%', maxWidth: '600px', padding: '28px', border: '1px solid var(--border-glow)' }}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
            {isEdit ? <Edit3 color="var(--accent-cyan)" size={20} /> : <PlusCircle color="var(--accent-primary)" size={20} />}
            {isEdit ? 'Chỉnh sửa yêu cầu tuyển dụng' : 'Tạo yêu cầu tuyển dụng'}
          </h2>
          <button onClick={onClose} className="btn btn-secondary" style={{ padding: '6px' }} aria-label="Đóng biểu mẫu">
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '6px', color: 'var(--text-secondary)' }}>Tên Vị trí Tuyển dụng *</label>
            <input
              className="input-field"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="VD: Lập trình viên Backend Senior"
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '6px', color: 'var(--text-secondary)' }}>Phòng ban / Bộ phận</label>
              <input
                className="input-field"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                placeholder="VD: Khối Công nghệ"
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '6px', color: 'var(--text-secondary)' }}>Kinh nghiệm tối thiểu (Năm)</label>
              <input
                type="number"
                className="input-field"
                value={minExp}
                onChange={(e) => setMinExp(e.target.value)}
                min="0"
                max="20"
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '6px', color: 'var(--text-secondary)' }}>Kỹ năng bắt buộc (Phân cách bằng dấu phẩy) *</label>
            <input
              className="input-field"
              value={skillsInput}
              onChange={(e) => setSkillsInput(e.target.value)}
              placeholder="Python, FastAPI, PostgreSQL, Docker, Redis"
              required
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '6px', color: 'var(--text-secondary)' }}>Yêu cầu Bằng cấp / Học vấn</label>
            <input
              className="input-field"
              value={education}
              onChange={(e) => setEducation(e.target.value)}
            />
          </div>

          {/* Criterion Weighting Sliders (FR-008) */}
          <div style={{ background: '#f7faf8', padding: '14px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
              <Sliders size={16} color="var(--accent-cyan)" />
              <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>Trọng số Đánh giá AI</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.8rem' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span>Khớp Kỹ năng (Skills)</span>
                  <span style={{ fontWeight: 700 }}>{wSkills}%</span>
                </div>
                <input type="range" min="0" max="100" value={wSkills} onChange={(e) => setWSkills(Number(e.target.value))} style={{ width: '100%' }} />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span>Độ phù hợp Kinh nghiệm (Experience)</span>
                  <span style={{ fontWeight: 700 }}>{wExp}%</span>
                </div>
                <input type="range" min="0" max="100" value={wExp} onChange={(e) => setWExp(Number(e.target.value))} style={{ width: '100%' }} />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span>Học vấn & Bằng cấp (Education)</span>
                  <span style={{ fontWeight: 700 }}>{wEdu}%</span>
                </div>
                <input type="range" min="0" max="100" value={wEdu} onChange={(e) => setWEdu(Number(e.target.value))} style={{ width: '100%' }} />
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '12px' }}>
            <button type="button" onClick={onClose} className="btn btn-secondary">Hủy bỏ</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? (isEdit ? 'Đang lưu...' : 'Đang tạo...') : (isEdit ? 'Lưu thay đổi' : 'Tạo Yêu cầu Tuyển dụng')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
