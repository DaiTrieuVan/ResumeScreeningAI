import React from 'react';
import { Filter, SlidersHorizontal, MapPin, DollarSign } from 'lucide-react';

export default function RealJobFilters({ minScore, setMinScore, locationFilter, setLocationFilter, searchQuery, setSearchQuery, categoryFilter, setCategoryFilter }) {
  return (
    <div className="glass-panel" style={{ padding: '16px 24px', marginBottom: '20px', display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center', justifyContent: 'space-between' }}>
      
      {/* Search Input */}
      <div style={{ flex: '1', minWidth: '220px' }}>
        <input
          className="input-field"
          placeholder="Lọc theo tên công việc, kỹ năng, công ty..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Location Filter */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}>
        <MapPin size={16} color="var(--accent-primary)" />
        <select
          className="select-field"
          value={locationFilter}
          onChange={(e) => setLocationFilter(e.target.value)}
          style={{ width: 'auto', padding: '6px 12px' }}
        >
          <option value="ALL">Tất cả địa điểm</option>
          <option value="HA_NOI">Hà Nội</option>
          <option value="HO_CHI_MINH">TP. Hồ Chí Minh</option>
          <option value="DA_NANG">Đà Nẵng</option>
          <option value="REMOTE">Remote / Làm từ xa</option>
        </select>
      </div>

      {/* Category Filter */}
      {categoryFilter !== undefined && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}>
          <Filter size={16} color="var(--accent-cyan)" />
          <select
            className="select-field"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            style={{ width: 'auto', padding: '6px 12px' }}
          >
            <option value="ALL">Tất cả ngành nghề</option>
            <option value="CHEF">Ẩm thực / Chef / F&B</option>
            <option value="IT">IT / Công nghệ / AI</option>
            <option value="MARKETING">Marketing & Truyền thông</option>
            <option value="SALES">Kinh doanh / Sales</option>
            <option value="FINANCE">Tài chính / Kế toán</option>
          </select>
        </div>
      )}

      {/* Score Threshold Slider */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem' }}>
        <SlidersHorizontal size={16} color="var(--accent-cyan)" />
        <span>Độ phù hợp tối thiểu: <b>{minScore}%</b></span>
        <input
          type="range"
          min="0"
          max="90"
          step="5"
          value={minScore}
          onChange={(e) => setMinScore(Number(e.target.value))}
          style={{ width: '110px' }}
        />
      </div>

    </div>
  );
}
