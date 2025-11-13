import React, { useState } from 'react';
import Panel from './Panel';
import Slider from './Slider';
import Button from './Button';
import { SectionVisualizationService } from '../../core/algorithms/services/SectionVisualizationService';
import { VisualizationConfig, VisualizationOptions } from '../../core/algorithms/services/SectionVisualizationService';

/**
 * 切面可视化配置接口
 */
interface SectionControlsProps {
  onConfigChange?: (config: VisualizationConfig) => void;
}

/**
 * 切面控制组件
 * 负责切面可视化参数的控制和配置
 */
const SectionControls: React.FC<SectionControlsProps> = ({ onConfigChange }) => {
  const [visualizationService] = useState(() => new SectionVisualizationService());
  const [config, setConfig] = useState<VisualizationConfig>(visualizationService.getDefaultConfig());
  const [options, setOptions] = useState<VisualizationOptions>({});

  /**
   * 更新配置并通知父组件
   */
  const updateConfig = (newOptions: VisualizationOptions) => {
    const newConfig = visualizationService.getVisualizationConfig([], newOptions);
    setConfig(newConfig);
    setOptions(newOptions);
    onConfigChange?.(newConfig);
  };

  /**
   * 处理颜色变化
   */
  const handleColorChange = (color: string) => {
    updateConfig({ ...options, color });
  };

  /**
   * 处理线宽变化
   */
  const handleLineWidthChange = (lineWidth: number) => {
    updateConfig({ ...options, lineWidth });
  };

  /**
   * 处理透明度变化
   */
  const handleOpacityChange = (opacity: number) => {
    updateConfig({ ...options, opacity });
  };

  /**
   * 处理高亮切换
   */
  const handleHighlightToggle = () => {
    updateConfig({ ...options, highlight: !options.highlight });
  };

  /**
   * 处理高亮颜色变化
   */
  const handleHighlightColorChange = (highlightColor: string) => {
    updateConfig({ ...options, highlightColor });
  };

  /**
   * 重置为默认配置
   */
  const handleReset = () => {
    const defaultConfig = visualizationService.getDefaultConfig();
    setConfig(defaultConfig);
    setOptions({});
    onConfigChange?.(defaultConfig);
  };

  return (
    <div className="controls-section">
      <Panel title="切面可视化控制" className="controls-panel">
        <div className="control-group">
          <Button onClick={handleReset} variant="secondary">
            重置配置
          </Button>
        </div>

        <div className="control-group">
          <label>切面颜色</label>
          <div className="color-picker">
            <input
              type="color"
              value={config.color}
              onChange={(e) => handleColorChange(e.target.value)}
              className="color-input"
            />
            <span className="color-value">{config.color}</span>
          </div>
        </div>

        <div className="control-group">
          <label>线宽: {config.lineWidth}px</label>
          <Slider
            value={config.lineWidth}
            min={1}
            max={10}
            step={1}
            onChange={handleLineWidthChange}
          />
        </div>

        <div className="control-group">
          <label>透明度: {Math.round(config.opacity * 100)}%</label>
          <Slider
            value={config.opacity}
            min={0}
            max={1}
            step={0.1}
            onChange={handleOpacityChange}
          />
        </div>

        <div className="control-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={config.highlight}
              onChange={handleHighlightToggle}
              className="checkbox-input"
            />
            高亮显示
          </label>
        </div>

        {config.highlight && (
          <div className="control-group">
            <label>高亮颜色</label>
            <div className="color-picker">
              <input
                type="color"
                value={options.highlightColor || '#ffff00'}
                onChange={(e) => handleHighlightColorChange(e.target.value)}
                className="color-input"
              />
              <span className="color-value">{options.highlightColor || '#ffff00'}</span>
            </div>
          </div>
        )}

        <div className="config-summary">
          <h4>当前配置</h4>
          <div className="summary-item">
            <span>可见性:</span>
            <span className={config.visible ? 'status-active' : 'status-inactive'}>
              {config.visible ? '可见' : '隐藏'}
            </span>
          </div>
          <div className="summary-item">
            <span>线宽:</span>
            <span>{config.lineWidth}px</span>
          </div>
          <div className="summary-item">
            <span>颜色:</span>
            <span style={{ color: config.color }}>{config.color}</span>
          </div>
          <div className="summary-item">
            <span>透明度:</span>
            <span>{Math.round(config.opacity * 100)}%</span>
          </div>
          <div className="summary-item">
            <span>高亮:</span>
            <span className={config.highlight ? 'status-active' : 'status-inactive'}>
              {config.highlight ? '启用' : '禁用'}
            </span>
          </div>
        </div>
      </Panel>
    </div>
  );
};

export default SectionControls;
